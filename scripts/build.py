#!/usr/bin/env python3
"""
surge-rule 生成器。

替换了旧的 refresh.sh / generate.py —— 那两个都坏在同一件事上:
它们读 `/Users/…/Desktop/surge rules.conf`,一个 GitHub runner 上根本不存在的路径。
所以「每天自动刷新」从来没有跑起来过。

本脚本的硬约束:
  1. **只读网络与仓内文件**,绝不读任何本机路径。
  2. **绝不修改 rules/**(历史镜像,已冻结;只读它来数条数与算时间戳)。
  3. 只有标准库,CI 上不需要 pip install。

产出:
  sets/region/cn-ipv4.list · cn-ipv6.list · cn-asn.list   ← 从 APNIC 一手数据生成
  manifest.json                                           ← app 消费的目录(覆盖 sets/ + 冻结的 rules/)
"""

import ipaddress
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETS_DIR = os.path.join(REPO, "sets")
RULES_DIR = os.path.join(REPO, "rules")
MANIFEST = os.path.join(REPO, "manifest.json")

APNIC_URL = "https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest"
BASE_URL = "https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/"

NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------- 一手来源:APNIC

def fetch_apnic():
    """APNIC 每日发布的注册数据。这是**一手权威来源**,不是谁的策展。"""
    req = urllib.request.Request(APNIC_URL, headers={"User-Agent": "surge-rule-builder"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_apnic(text):
    """
    行格式:
      apnic|CN|ipv4|1.0.1.0|256|20110414|allocated     ← 第 5 列是**地址数量**,不是前缀长度
      apnic|CN|ipv6|2001:250::|35|20000426|allocated    ← 第 5 列**就是**前缀长度
      apnic|CN|asn|3460|1|20020801|allocated            ← 第 5 列是连续 ASN 的个数
    """
    v4, v6, asn = [], [], []
    for line in text.splitlines():
        if line.startswith("#") or "|CN|" not in line:
            continue
        parts = line.split("|")
        if len(parts) < 7 or parts[1] != "CN":
            continue
        kind, start, value, status = parts[2], parts[3], parts[4], parts[6]
        # 只要真正分配出去的;summary 行(status 为 summary)与保留段跳过。
        if status not in ("allocated", "assigned"):
            continue
        try:
            if kind == "ipv4":
                first = ipaddress.IPv4Address(start)
                last = ipaddress.IPv4Address(int(first) + int(value) - 1)
                # ⚠️ 数量不一定是 2 的幂、起点也不一定对齐 ⇒ 一个分配可能要拆成多条 CIDR。
                #    用标准库汇总,别手写位运算(手写最容易在非对齐段上悄悄算错)。
                v4.extend(ipaddress.summarize_address_range(first, last))
            elif kind == "ipv6":
                v6.append(ipaddress.IPv6Network(f"{start}/{value}", strict=False))
            elif kind == "asn":
                asn.extend(range(int(start), int(start) + int(value)))
        except (ipaddress.AddressValueError, ValueError) as exc:
            print(f"  ⚠️ 跳过一行无法解析的 APNIC 数据: {line!r} ({exc})", file=sys.stderr)
    return v4, v6, asn


# ---------------------------------------------------------------- 写清单

def write_list(rel_path, title, source_note, lines):
    """
    🔴 **表头里绝不写 Policy。** 旧仓每个 .list 的表头都有一行 `# Policy: DIRECT`,
    那是把「它该走哪」焊进了资产本身 —— 同一份清单在另一个用户手里可能是完全相反的走向。
    清单只回答「这些是什么」,「走哪」由使用者在自己的配置里决定。
    """
    path = os.path.join(REPO, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = "\n".join(lines)
    header = (
        f"# {title}\n"
        f"# Source: {source_note}\n"
        f"# Generated: {NOW}\n"
        f"# Rules: {len(lines)}\n"
        f"#\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + body + "\n")
    print(f"  {rel_path}: {len(lines)} 条")
    return len(lines)


def build_sets():
    print("[1/2] 从 APNIC 生成自建清单…")
    v4, v6, asn = parse_apnic(fetch_apnic())
    src = "APNIC delegated-apnic-latest(注册机构一手数据)"
    counts = {}
    counts["sets/region/cn-ipv4.list"] = write_list(
        "sets/region/cn-ipv4.list", "中国大陆 IPv4 地址段", src,
        [f"IP-CIDR,{n},no-resolve" for n in sorted(v4, key=lambda n: int(n.network_address))],
    )
    counts["sets/region/cn-ipv6.list"] = write_list(
        "sets/region/cn-ipv6.list", "中国大陆 IPv6 地址段", src,
        [f"IP-CIDR6,{n},no-resolve" for n in sorted(v6, key=lambda n: int(n.network_address))],
    )
    counts["sets/region/cn-asn.list"] = write_list(
        "sets/region/cn-asn.list", "中国大陆自治系统号(ASN)", src,
        [f"IP-ASN,{a},no-resolve" for a in sorted(set(asn))],
    )
    return counts


# ---------------------------------------------------------------- manifest

def rule_count(path):
    """
    真正会成为规则的行数。⚠️ **分母不是物理行数** —— 注释与空行不是规则。
    判据与 app 侧 `RuleSetHealth.ruleCount` 一致,两边不许分叉。
    """
    n = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            s = raw.strip()
            if s and not s.startswith("#") and not s.startswith(";") and not s.startswith("//"):
                n += 1
    return n


def git_last_commit_times():
    """
    每个文件最后一次被改动的时间。
    ⚠️ 一次 `git log` 走完,不要每个文件 spawn 一次 —— 605 个文件那样要几十秒。
    """
    out = subprocess.run(
        ["git", "-C", REPO, "log", "--pretty=format:@%cI", "--name-only"],
        capture_output=True, text=True, check=True,
    ).stdout
    times, current = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            current = line[1:]
        elif line and current and line not in times:
            times[line] = current  # 第一次出现 = 最近一次改动
    return times


# 文件名/目录 → 分类。**只写确凿的**;推不出来就留空,让 app 归到「其他」并原样显示名字。
# 🔴 不硬猜 —— 猜错的分类比没有分类更糟,它会让用户按错误的类别去找东西。
DIR_CATEGORY = {
    "AD-Blocked": "adblock",
    "AI": "ai",
    "DNS": "network",
    "STUN": "network",
    "Mail": "social",
}
NAME_CATEGORY = [
    ("media", r"netflix|youtube|disney|spotify|hbo|hulu|primevideo|iqiyi|bilibili|iptv|dazn|tidal|"
              r"deezer|soundcloud|twitch|viu|bbc|itv|cbs|nbcu?|foxnow|pbs|my5|all4|kktv|mytvsuper|"
              r"pandora|apple(tv|music)|netease.?music|joox|kkbox|myvideo|linetv|abema|niconico"),
    ("social", r"telegram|discord|twitter|facebook|instagram|whatsapp|^line$|wechat|weibo|reddit|"
               r"snapchat|tiktok|signal|threads|mastodon|4chan|quora|tumblr|pinterest|linkedin|"
               r"zoom|slack|skype|potatochat|truthsocial|gmail|outlook"),
    ("dev", r"github|gitlab|docker|npm|pypi|jetbrains|stackoverflow|vercel|netlify|cloudflare|"
            r"^aws$|azure|digitalocean|heroku|sourceforge|jquery|contentful|scaleflex|jsdelivr|unpkg"),
    ("game", r"steam|^psn$|playstation|xbox|nintendo|epicgames|origin|blizzard|riot|ubisoft|"
             r"^ea$|garena|miHoYo|genshin"),
    ("shopping", r"amazon|ebay|taobao|tmall|^jd$|pinduoduo|shopee|alibaba|etsy|walmart|adidas|"
                 r"nike|vancl|youzan|bestore|meitu"),
    ("finance", r"bank|paypal|visa|mastercard|stripe|alipay|^cmb$|^psbc$|icbc|^boc$|^ccb$|abchina|"
                r"crypto|coinbase|binance|taikang|chunyou"),
    ("apple", r"^apple|icloud|itunes|testflight|findmy"),
    ("google", r"^google"),
    ("microsoft", r"^microsoft|^windows|^office|onedrive|^bing"),
    ("ai", r"openai|chatgpt|claude|anthropic|gemini|copilot|deepseek"),
    ("network", r"^dns|^stun|^ntp|speedtest|^lan$|^ip"),
    ("region", r"china|^cn|asn|taiwan|hkgolden|hkedcity"),
]


def category_for(rel_path):
    parts = rel_path.split("/")
    if parts[0] == "sets":
        return parts[1]  # sets/ 的目录就是分类,这是新结构的定义
    if len(parts) >= 2 and parts[1] in DIR_CATEGORY:
        return DIR_CATEGORY[parts[1]]
    if len(parts) >= 2 and parts[1].startswith(("DIRECT-Fallback", "Proxy-Fallback")):
        stem = os.path.splitext(parts[-1])[0]
        if re.search(r"china|^cn", stem, re.I):
            return "region"
    stem = os.path.splitext(parts[-1])[0]
    for category, pattern in NAME_CATEGORY:
        if re.search(pattern, stem, re.I):
            return category
    return ""  # 🔴 推不出来就留空。app 会归到「其他」并原样显示名字,不会丢掉它。


BLACKMATRIX7 = {
    "repository": "blackmatrix7/ios_rule_script",
    "homepage": "https://github.com/blackmatrix7/ios_rule_script",
    # 🔴 逐字如实:上游 README 明写禁止转载。不粉饰,详见 SOURCES.md。
    "license": "仅供学习研究,上游明示禁止转载(详见 SOURCES.md)",
}
HAGEZI = {
    "repository": "hagezi/dns-blocklists",
    "homepage": "https://github.com/hagezi/dns-blocklists",
    "license": "GPL-3.0",
}


def upstream_for(rel_path):
    if not rel_path.startswith("rules/"):
        return None
    if "/AD-Blocked/" in rel_path and re.search(r"hagezi", rel_path, re.I):
        return HAGEZI
    return BLACKMATRIX7


def build_manifest(generated_counts):
    print("[2/2] 生成 manifest.json…")
    times = git_last_commit_times()
    entries = []
    for root_name in ("sets", "rules"):
        root = os.path.join(REPO, root_name)
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            for name in sorted(files):
                if not name.endswith(".list"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, REPO)
                # 🔴 三档 layer 必须分得开:
                #   authored = 我们从一手来源自己生成的
                #   mirrored = 内容是别人的,但我们确实托管着一份(← 历史遗留,待清理)
                #   indexed  = 只指路、不托管(本轮还没有这类条目)
                is_authored = rel.startswith("sets/")
                entry = {
                    "path": rel,
                    "displayName": os.path.splitext(name)[0],
                    "category": category_for(rel),
                    "tags": ["geo:cn", "basis:registry"] if is_authored else [],
                    "ruleCount": generated_counts.get(rel) or rule_count(full),
                    "layer": "authored" if is_authored else "mirrored",
                }
                stamp = NOW if is_authored else times.get(rel)
                # ⚠️ 拿不到时间戳就**不写这个字段**,绝不用「现在」顶替 ——
                #    那会把一份停更两年的清单显示成刚更新过。
                if stamp:
                    entry["updatedAt"] = stamp
                upstream = upstream_for(rel)
                if upstream:
                    entry["upstream"] = dict(upstream, listURL=BASE_URL + rel)
                entries.append(entry)

    entries.sort(key=lambda e: e["path"])
    manifest = {
        "schemaVersion": 1,
        "baseURL": BASE_URL,
        "generatedAt": NOW,
        "entries": entries,
    }
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")

    by_layer = {}
    for e in entries:
        by_layer[e["layer"]] = by_layer.get(e["layer"], 0) + 1
    uncategorized = sum(1 for e in entries if not e["category"])
    print(f"  条目 {len(entries)} · {by_layer} · 未归类 {uncategorized}(走「其他」,如实不猜)")


def main():
    counts = build_sets()
    build_manifest(counts)
    print("完成。rules/ 未被触碰。")


if __name__ == "__main__":
    main()
