# 来源与授权

本仓的内容分**两类**,授权状况完全不同,下面逐条列清楚。
格式参考 [StevenBlack/hosts](https://github.com/StevenBlack/hosts) 的逐源署名表。

---

## 一、`sets/` —— 本仓自建

从**注册机构一手数据**生成,不派生自任何人的策展。

| 清单 | 来源 | 来源性质 | 授权 |
|---|---|---|---|
| `sets/region/cn-ipv4.list` | [APNIC `delegated-apnic-latest`](https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest) | 地址注册机构每日发布的分配记录 | 公开事实数据 |
| `sets/region/cn-ipv6.list` | 同上 | 同上 | 同上 |
| `sets/region/cn-asn.list` | 同上 | 同上 | 同上 |

生成脚本:[`scripts/build.py`](scripts/build.py)。每日自动重跑。

> **为什么这类是干净的**:清单里的每一条都是从公开注册数据**直接推导**出来的事实
> (「这段 IP 分配给了中国大陆的组织」),不涉及任何人对「哪些域名值得收进来」的编辑判断 ——
> 也就没有别人的策展可以侵犯。

---

## 二、`rules/` —— 🔴 历史镜像,**已冻结**

这 605 个文件是本仓早期从上游镜像下来的,**内容不是我们写的**。
它们已于 2026-07-29 **冻结**:生成脚本不再触碰、不再每日重新拉取和发布。

保留它们的唯一原因是**已有配置正在引用这些地址**,直接删除会立刻打断使用者的网络。
**清理与迁移另立一件。**

| 上游 | 涉及范围 | 授权状况 |
|---|---|---|
| [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) | `rules/` 绝大部分 | 🔴 **上游 README 明示:「本项目仅供学习和研究使用」「禁止任何公众号、自媒体进行任何形式的转载、发布」,并禁止商业使用。** GitHub 的授权检测器给它标了 GPL-2.0,但**维护者写在 README 里的话与之冲突,应以维护者的表述为准。** |
| [hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists) | `rules/AD-Blocked/Hagezi-PRO-mini.list` | GPL-3.0(允许再分发,要求同等 copyleft 与署名) |

> **如实说明**:就 blackmatrix7 而言,本仓过去的镜像行为**不符合上游的表述**。
> 现已停止主动再分发(冻结),并在此明确署名。移除这批内容需要给现有引用方一条迁移路径,
> 正在单独处理中。

---

## 三、本仓的授权

本仓以 **GPL-3.0** 发布([LICENSE](LICENSE))—— 选它是因为其中包含 GPL-3.0 的上游内容(HaGeZi),
输出必须保持同等 copyleft。

---

## 四、一条设计原则(与授权无关,但影响你怎么用)

🔴 **清单只回答「这些域名/地址是什么」,不回答「它该走哪」。**

所以 `sets/` 里的**路径与表头都不含策略名**。旧的 `rules/Proxy/Netflix.list` 这种命名把
「Netflix 走代理」这个**个人决定**焊进了资产本身 —— 而另一个人可能正需要它直连。
把「是什么」和「走哪」分开,同一份清单才对所有人都成立;
「走哪」由你在自己的配置里写 `RULE-SET,<地址>,<你选的策略>` 决定。
