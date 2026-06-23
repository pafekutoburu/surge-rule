# Surge Rules 全集

所有规则集按分组归类，可直接在 Surge 配置中用 `RULE-SET` 引用。

---

## AI

| 规则集 | 策略 | 规则数 | 引用 |
|--------|------|--------|------|
| AI-Domains | AI | 126 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AI/AI-Domains.list,AI` |
| BardAI | Proxy | 2 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AI/BardAI.list,Proxy` |
| Copilot | Proxy | 31 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AI/Copilot.list,Proxy` |
| Gemini | Proxy | 4 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AI/Gemini.list,Proxy` |
| OpenAI | Proxy | 1 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AI/OpenAI.list,Proxy` |

## AD-Blocked

| 规则集 | 策略 | 规则数 | 引用 |
|--------|------|--------|------|
| AdColony | REJECT-TINYGIF | 1 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/AdColony.list,REJECT-TINYGIF,no-resolve` |
| Addthis | REJECT-TINYGIF | 3 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Addthis.list,REJECT-TINYGIF,no-resolve` |
| AddToAny | REJECT-TINYGIF | 1 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/AddToAny.list,REJECT-TINYGIF,no-resolve` |
| AdGuardSDNSFilter | REJECT-TINYGIF | 81745 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/AdGuardSDNSFilter.list,REJECT-TINYGIF,no-resolve` |
| Advertising | REJECT-TINYGIF | 735 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Advertising.list,REJECT-TINYGIF,no-resolve` |
| AdvertisingLite | REJECT-TINYGIF | 2 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/AdvertisingLite.list,REJECT-TINYGIF,no-resolve` |
| AdvertisingMiTV | REJECT-TINYGIF | 165 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/AdvertisingMiTV.list,REJECT-TINYGIF,no-resolve` |
| AdvertisingTest | REJECT-TINYGIF | 27 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/AdvertisingTest.list,REJECT-TINYGIF,no-resolve` |
| AppLovin | REJECT-TINYGIF | 1 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/AppLovin.list,REJECT-TINYGIF,no-resolve` |
| BlockHttpDNS | REJECT-TINYGIF | 26 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/BlockHttpDNS.list,REJECT-TINYGIF,no-resolve` |
| Domob | REJECT-TINYGIF | 26 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Domob.list,REJECT-TINYGIF,no-resolve` |
| EasyPrivacy | REJECT-TINYGIF | 38902 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/EasyPrivacy.list,REJECT-TINYGIF,no-resolve` |
| Flurry | REJECT-TINYGIF | 1 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Flurry.list,REJECT-TINYGIF,no-resolve` |
| Hijacking | REJECT-TINYGIF | 189 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Hijacking.list,REJECT-TINYGIF,no-resolve` |
| JiGuangTuiSong | REJECT-TINYGIF | 18 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/JiGuangTuiSong.list,REJECT-TINYGIF,no-resolve` |
| Privacy | REJECT-TINYGIF | 1 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Privacy.list,REJECT-TINYGIF,no-resolve` |
| Pubmatic | REJECT-TINYGIF | 1 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Pubmatic.list,REJECT-TINYGIF,no-resolve` |
| ZhihuAds | REJECT-TINYGIF | 11 | `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/ZhihuAds.list,REJECT-TINYGIF,no-resolve` |

> Custom-REJECT-TINYGIF（自定义拒绝规则，27 条）未包含在上表中，如需引用请使用：
> `RULE-SET,https://raw.githubusercontent.com/pafekutoburu/surge-rule/refs/heads/main/rules/AD-TRACKING/Custom-REJECT-TINYGIF.list,REJECT-TINYGIF,no-resolve`

## DIRECT-China

*（共 245 个规则集，待展开）*

## DIRECT-IP

*（共 11 个规则集，待展开）*

## Proxy-International

*（共 298 个规则集，待展开）*

---

> 所有规则集由 blackmatrix7/ios_rule_script 上游规则分发整理，每天凌晨 3 点自动刷新。
