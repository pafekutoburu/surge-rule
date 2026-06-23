#!/bin/bash
# ============================================================
# surge-rules 自动刷新脚本
# 每天运行: 下载最新 blackmatrix7 规则 + 自定义规则
# → 去重 → 重新生成 .list 文件 → 推送到 GitHub
# ============================================================
set -e

# --- 配置 ---
MY_DIR="$(cd "$(dirname "$0")" && pwd)"
DOWNLOADS="/tmp/surge-refresh"
mkdir -p "$DOWNLOADS"

echo "[1/4] 下载黑色矩阵7规则..."
# 从当前的 surge.conf 提取所有外部 RULE-SET URL
python3 << 'PYEOF'
import json, os, urllib.request, time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 读取当前配置文件中的 RULE-SET 列表
# 注意: 如果原始 surge rules.conf 已变动, 修改此处路径
in_line = False
line_list = []
if os.path.exists("/Users/succichang/Desktop/surge rules.conf"):
    with open("/Users/succichang/Desktop/surge rules.conf", "r") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("["):
                continue
            parts = s.split(",")
            if len(parts) >= 3 and parts[0].strip() == "RULE-SET":
                line_list.append({
                    "url": parts[1].strip(),
                    "policy": parts[2].strip(),
                    "options": ",".join(parts[3:]) if len(parts) > 3 else ""
                })

print(f"发现 {len(line_list)} 个外部规则集, 开始下载...")

download_dir = os.environ.get('DOWNLOADS', '/tmp/surge-refresh')
os.makedirs(download_dir, exist_ok=True)

# Deduplicate by URL
seen = set()
unique = []
for rs in line_list:
    if rs["url"] not in seen:
        seen.add(rs["url"])
        unique.append(rs)

print(f"去重后 {len(unique)} 个唯一 URL, 开始并行下载...")

def download(rs):
    url = rs["url"]
    name = url.split("/")[-1]
    fpath = os.path.join(download_dir, name)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=60)
            content = resp.read().decode("utf-8")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            rule_count = sum(1 for l in content.strip().split("\n") 
                           if l.strip() and not l.strip().startswith("#"))
            return (name, rule_count, None)
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                return (name, 0, str(e))

success = 0
total_rules = 0
with ThreadPoolExecutor(max_workers=20) as ex:
    fut = {ex.submit(download, rs): rs for rs in unique}
    for f in as_completed(fut):
        name, cnt, err = f.result()
        if err:
            print(f"  \u2717 {name}: {err[:50]}")
        else:
            success += 1
            total_rules += cnt
            if cnt > 0:
                print(f"  \u2713 {name:40s} {cnt:>6d} 条")

print(f"\n下载完成: {success}/{len(unique)} 成功, {total_rules} 条规则")
PYEOF

echo ""
echo "[2/4] 合并去重并重新生成 .list 文件..."
python3 << 'PYEOF'
import os, re, json, urllib.request
from collections import defaultdict, Counter

download_dir = os.environ.get('DOWNLOADS', '/tmp/surge-refresh')
output_dir = os.environ.get('MY_DIR', '/Users/succichang/Desktop/surge-rules')
rules_dir = os.path.join(output_dir, "rules")
os.makedirs(rules_dir, exist_ok=True)

# 读取原始配置文件中的 RULE-SET 映射
rs_entries = []
with open("/Users/succichang/Desktop/surge rules.conf", "r") as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("["):
            continue
        parts = s.split(",")
        if len(parts) >= 3 and parts[0].strip() == "RULE-SET":
            url = parts[1].strip()
            name = url.split("/")[-1]
            rs_entries.append({
                "name": name, "url": url, "policy": parts[2].strip(),
                "options": ",".join(parts[3:]) if len(parts) > 3 else ""
            })

# 解析内联规则
inline_rules = []
with open("/Users/succichang/Desktop/surge rules.conf", "r") as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("//") or s.startswith("["):
            continue
        text = s.split(" //")[0].strip()
        parts = text.split(",")
        if len(parts) < 3: continue
        rt = parts[0].strip()
        if rt == "RULE-SET": continue
        inline_rules.append({
            "type": rt, "value": parts[1].strip(),
            "policy": parts[2].strip(),
            "options": ",".join(parts[3:]) if len(parts) > 3 else "",
            "service": "Custom"
        })

# 提取服务名
def extract_service(url):
    u = url.split("/")
    try:
        si = u.index("Surge")
        return "/".join(u[si+1:-1])
    except ValueError:
        return u[-1].replace(".list", "")

# 解析外部规则
expanded = []
rs_url_map = {}
for rs in rs_entries:
    fp = os.path.join(download_dir, rs["name"])
    if not os.path.isfile(fp): continue
    rs_url_map[rs["name"]] = rs
    svc = extract_service(rs["url"])
    with open(fp, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    for raw_line in content.strip().split("\n"):
        st = raw_line.strip()
        if not st or st.startswith("#") or st.startswith("//"): continue
        p = st.split(",")
        if len(p) >= 2:
            expanded.append({
                "type": p[0].strip(), "value": p[1].strip(),
                "policy": rs["policy"], "source_file": rs["name"],
                "service": svc
            })

# 去重 (内联优先)
seen = {}
deduped = []
for r in inline_rules:
    key = (r["type"], r["value"])
    seen[key] = r
    deduped.append(r)
for r in expanded:
    key = (r["type"], r["value"])
    if key not in seen:
        seen[key] = r
        deduped.append(r)

# 分组
svc_pol = defaultdict(lambda: Counter())
svc_rules = defaultdict(list)
for r in deduped:
    svc = r.get("service", "Unknown")
    svc_rules[svc].append(r)
    svc_pol[svc][r["policy"]] += 1

custom_pol = defaultdict(list)
for r in svc_rules["Custom"]:
    custom_pol[r["policy"]].append(r)

def clean_name(svc):
    name = svc.replace("/", "-").replace("'", "").replace(" ", "-")
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '', name)

# 写 .list 文件
list_files = []
for svc in sorted(svc_rules.keys()):
    if svc == "Custom": continue
    rules = svc_rules[svc]
    if not rules: continue
    dominant = svc_pol[svc].most_common(1)[0][0]
    fn = clean_name(svc) + ".list"
    fp = os.path.join(rules_dir, fn)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(f"# {svc}\n# Policy: {dominant}\n# Total: {len(rules)} rules\n#\n")
        for r in sorted(rules, key=lambda x: (x["type"], x["value"])):
            f.write(f"{r['type']},{r['value']}\n")
    list_files.append((fn, dominant, len(rules)))

# Custom inline files (>10 rules)
for pol in ["AI","Proxy","DIRECT","REJECT-TINYGIF"]:
    rules = custom_pol.get(pol, [])
    if len(rules) <= 10: continue
    fn = f"Custom-{clean_name(pol)}.list"
    fp = os.path.join(rules_dir, fn)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(f"# Custom inline - policy: {pol}\n# Total: {len(rules)} rules\n#\n")
        for r in sorted(rules, key=lambda x: (x["type"], x["value"])):
            f.write(f"{r['type']},{r['value']}\n")
    list_files.append((fn, pol, len(rules)))

list_files.sort(key=lambda x: -x[2])

# Base rules
base_rules = {"GEOIP": [], "FINAL": [], "DOMAIN-SUFFIX,cn": [], "DOMAIN-KEYWORD,-cn": []}
for r in svc_rules["Custom"]:
    if r["type"] == "GEOIP": base_rules["GEOIP"].append(r)
    elif r["type"] == "FINAL": base_rules["FINAL"].append(r)
    elif (r["type"], r["value"]) == ("DOMAIN-SUFFIX","cn"): base_rules["DOMAIN-SUFFIX,cn"].append(r)
    elif (r["type"], r["value"]) == ("DOMAIN-KEYWORD","-cn"): base_rules["DOMAIN-KEYWORD,-cn"].append(r)

# 写 surge.conf
conf_path = os.path.join(output_dir, "surge.conf")
with open(conf_path, "w", encoding="utf-8") as f:
    f.write("# Surge 规则配置 - 自动刷新\n")
    f.write(f"# 生成时间: refresh-date\n# 总规则数: {len(deduped)}\n#\n[General]\n\n[Rule]\n\n")

    # AI
    f.write("# == AI ==\n\n")
    for fn, pol, cnt in list_files:
        if pol == "AI": f.write(f"RULE-SET,rules/{fn},{pol}\n")
    for r in custom_pol.get("AI",[]):
        opts = f",{r['options']}" if r.get("options") else ""
        f.write(f"{r['type']},{r['value']},{r['policy']}{opts}\n")
    for r in custom_pol.get("Direct",[]):
        opts = f",{r['options']}" if r.get("options") else ""
        f.write(f"{r['type']},{r['value']},{r['policy']}{opts}\n")
    f.write("\n")

    # Mail
    f.write("# == Mail ==\n\n")
    for r in custom_pol.get("Mail",[]):
        f.write(f"{r['type']},{r['value']},{r['policy']}\n")
    f.write("\n")

    # AD
    f.write("# == AD/TRACKING ==\n\n")
    for fn, pol, cnt in list_files:
        if pol == "REJECT-TINYGIF":
            f.write(f"RULE-SET,rules/{fn},{pol},no-resolve\n")
    f.write("\n")

    # DIRECT
    f.write("# == DIRECT ==\n\n")
    for fn, pol, cnt in list_files:
        if pol == "DIRECT":
            opts = ",no-resolve" if "IP" in fn or "ASN" in fn else ""
            f.write(f"RULE-SET,rules/{fn},{pol}{opts}\n")
    f.write("\n")

    # Proxy
    f.write("# == Proxy ==\n\n")
    for fn, pol, cnt in list_files:
        if pol == "Proxy":
            opts = ",no-resolve" if "IP" in fn or "CIDR" in fn else ""
            f.write(f"RULE-SET,rules/{fn},{pol}{opts}\n")
    f.write("\n")

    # CN Fallback
    f.write("# == CN Fallback ==\n\n")
    for k, rules in base_rules.items():
        for r in rules:
            f.write(f"{r['type']},{r['value']},{r['policy']}\n")
    f.write("\n# == FINAL ==\n\n")
    for r in base_rules.get("FINAL",[]):
        f.write(f"{r['type']},{r['value']},{r['policy']}\n")
    f.write("\n[URL Rewrite]\n^https?://(www.)?(g|google).cn https://www.google.com 302\n\n[MITM]\n")

print("重新生成完成!")
PYEOF

echo ""
echo "[3/4] 推送到 GitHub..."
cd "$MY_DIR"
git add -A
git commit -m "auto-refresh $(date +%Y-%m-%d)" --allow-empty
git push origin main 2>/dev/null || echo "  ⚠️ 推送失败 — 请先配置 GitHub 认证"

echo ""
echo "[4/4] 完成!"
echo "   规则总数: $(grep -c 'DOMAIN\|IP-CIDR\|USER-AGENT\|URL-REGEX' rules/*.list 2>/dev/null || echo 'N/A')"
