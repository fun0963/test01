# Objective Gates

> 客觀證據層(承重牆):「agent 說完成」不算完成,gate 綠了才算。
> 這是本專案 gate 指令的**唯一權威來源**——工單的 Required Verification 直接引用這裡,不要各自重寫。

## Gate 指令(權威來源)

| Gate | 指令 | 必須 | 何時跑 |
| --- | --- | --- | --- |
(上一列換成新專案真實指令lint/test/smoke 怎麼跑)
| Static | `<lint + typecheck 指令，例如 npm run lint && npm run typecheck>` | 是 | 每張工單 |
| Unit | `<例如 npm test / pytest>` | 是 | 每張工單 |
| Integration | `<例如 npm run test:integration>` | 視工單 | 碰 API / DB 時 |
| Smoke / E2E | `<例如 curl ... / 啟動腳本 / 真實檔案驗證>` | 是 | close 前 |
| Manual Product Check | human owner 看 UI / 行為 | 是 | close 前 |

> 開案時由 Orchestrator + Human 一起把 `<...>` 換成本專案真實指令。

## 環境 / 前置

- 怎麼起服務：`<指令>`
- 怎麼備測試資料 / DB：`<步驟>`
- 需要的環境變數 / 憑證：`<說明>`

## Release / Merge Gate（總關卡）

- [ ] 上面所有「必須」gate 綠燈
- [ ] CI pass
- [ ] review findings 已仲裁
- [ ] 無未解 P0/P1
- [ ] 剩餘風險已記錄並被 human owner 接受

## 「Not Run」認定規則

只有以下明確原因可接受某個 gate not run,且必須寫在 report 的 Verification 欄:

- `<例如：此工單未觸及該模組，integration 不適用>`
- `<例如：需要正式環境憑證，本地無法跑，已於 handoff 標記待 CI 驗>`

除此之外一律視為**未通過**,不得 close。不接受「應該可以」「看起來沒問題」「只是小改所以不用驗」。
