# Surge Rule Sets

Surge 可直接 `RULE-SET` 引用的规则集。内容分**两类**,授权状况完全不同 —— 详见 [SOURCES.md](SOURCES.md)。

---

## 一条设计原则

🔴 **清单只回答「这些域名/地址是什么」,不回答「它该走哪」。**

所以 `sets/` 里的**路径与表头都不含策略名**。像 `Proxy/Netflix.list` 这种命名把
「Netflix 走代理」这个**个人决定**焊进了资产本身 —— 而另一个人可能正需要它直连。
把「是什么」和「走哪」分开,同一份清单才对所有人都成立。

走向由你在自己的配置里决定:

```
RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/sets/region/cn-asn.list,DIRECT
```

---

## `sets/` —— 本仓自建 ✅

从**注册机构一手数据**生成,每日自动重建,不派生自任何人的策展。

| 清单 | 内容 | 来源 |
|---|---|---|
| `sets/region/cn-ipv4.list` | 中国大陆 IPv4 地址段 | APNIC `delegated-apnic-latest` |
| `sets/region/cn-ipv6.list` | 中国大陆 IPv6 地址段 | 同上 |
| `sets/region/cn-asn.list` | 中国大陆 ASN | 同上 |

生成脚本 [`scripts/build.py`](scripts/build.py),由
[Daily Refresh](.github/workflows/daily-refresh.yml) 每日 02:00 UTC 触发。

> ⚠️ **不夸大它的作用**:Surge 内建的 `GEOIP,CN` 已经能覆盖大部分「中国大陆流量走直连」的需求。
> 这几份清单的价值在于**来源可查、粒度可见、可以只取其中一类**(比如只要 ASN 不要 IP 段),
> 而不是替代 `GEOIP,CN`。

## `rules/` —— 🔴 历史镜像,已冻结

605 个文件,**内容不是本仓写的**,来自 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)
与 [hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists)。

**已于 2026-07-29 冻结**:生成脚本不再触碰,也不再每日重新拉取和发布。
保留的唯一原因是已有配置正引用着这些地址,直接删除会立刻打断使用者的网络。

🔴 **blackmatrix7 的 README 明示禁止转载与商业使用** —— 详见 [SOURCES.md](SOURCES.md)。
这批内容的移除与迁移正在单独处理。

## `manifest.json`

两类内容的统一目录:路径 / 分类 / 条数 / 最后更新 / 归属层
(`authored` 自建 · `mirrored` 历史镜像 · `indexed` 只指路)。给工具消费用。

---

## 历史产物(停在 2026-07-09,不再更新)

- `surge.conf` —— 旧管线生成的整份 `[Rule]` 引用表。**这是历史快照,不是当前配置。**
- `ALL.md` —— 旧的规则集链接总表,同样是历史快照。

> 上一版 README 写着「每天凌晨 3 点自动刷新」。**那句话是假的** ——
> 自动刷新的 workflow 因为一处 YAML 缩进错误从未成功运行过哪怕一次
> (40 次运行记录全部 0 秒失败,schedule 一次都没触发),仓库内容自 2026-07-09 起没有变过。
> 已在本次修复并改口。

## 授权

本仓以 [GPL-3.0](LICENSE) 发布(因为其中含 GPL-3.0 的上游内容,输出须保持同等 copyleft)。
