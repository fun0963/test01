# AI 協作開發指南

> 參考 `workflow.md` 的實戰經驗整理：不要讓單一模型硬扛整個專案，而是把最強模型放在最高槓桿的位置，讓 AI 團隊用明確分工、外部記憶、驗收 gate 和人類終審來穩定交付。

## 1. 核心觀念

AI 協作開發的重點不是「找一個模型單挑所有事情」，而是把不同模型放在最適合的位置。

最強推理模型不應該長時間消耗在大量低階改 code 上，而應該扮演控制平面：

- 判斷方向
- 拆解任務
- 定義驗收
- 限制 scope
- 仲裁 reviewer finding
- 讀 diff 和測試結果
- 決定任務是否真的 close

coding agent 則應該扮演執行平面：

- 接受窄工單
- 修改指定範圍
- 跑測試與 smoke
- 回報 diff、驗證結果與風險

異質 reviewer 只負責懷疑：

- 找 edge case
- 找 contract risk
- 找 regressions
- 找測試缺口

但 reviewer 不直接指揮 executor，也沒有最終決策權。所有 finding 必須被 orchestrator 查證後才進入修復。

人類仍然是產品與風險的最後 owner：

- 決定產品行為是否正確
- 接受或拒絕剩餘風險
- 判斷商業與使用者影響
- 決定是否發布或合併

## 2. 標準角色分工

| 角色 | 建議工具 | 主要責任 | 不負責 |
| --- | --- | --- | --- |
| Human Owner | 人類工程師 / PM / Tech Lead | 最終產品驗收、風險接受、優先級、商業判斷 | 逐行盯 code、代替 agent 做所有整合 |
| Orchestrator | 最強推理模型，例如 Fable / Opus / GPT 類高推理模型 | 診斷、拆工單、定義 done、仲裁、收斂、讀 diff | 大量直接寫 code、盲信 reviewer、無限延伸 scope |
| Executor | Codex / coding agent / IDE agent | 根據窄工單改 code、跑測試、產出報告 | 自己定義完成、擴大 scope、修改禁區 |
| Reviewer | Gemini / AGY / 另一個異質模型 | aggressive review、找風險、找盲點 | 拍板、直接指揮修復、把假陽性變成新需求 |
| Objective Gates | CI / 測試 / smoke / 真實資料 / 使用者驗收 | 提供客觀證據 | 取代產品判斷 |

### 分流規則

| 任務類型 | 推薦流程 |
| --- | --- |
| 小而明確的單點修改 | 直接給 executor |
| 跨檔案、跨服務、需要驗收、需要部署或需要真正 close 的任務 | 走 orchestrator 流程 |
| 需要找風險、盲點、合約問題或 edge case | 加 reviewer |
| 涉及產品行為、商業判斷、資料風險、安全風險 | human owner 必須終審 |

## 3. 專案目錄模板

每個專案建議建立以下 AI 協作文件，讓長任務不依賴模型記憶。
整份 `ai-workflow/` 是自足的空白母版，新專案開案時整包複製到根目錄後填寫。
（操作手冊見 `WORKFLOW.md`，速查見 `USAGE.md`。）

```text
ai-workflow/
  00-spec.md
  01-plan.md
  02-risk-register.md
  03-gates.md
  memory.md
  handoff.md
  tickets/
    T-001-title.md
    T-002-title.md
  reports/
    T-001-report.md
    T-002-report.md
  reviews/
    T-001-review.md
    T-002-review.md
  decisions/
    ADR-001-title.md
```

### 文件用途

| 文件 | 用途 |
| --- | --- |
| `00-spec.md` | 專案目標、非目標、需求、驗收條件 |
| `01-plan.md` | 階段計畫、工單列表、依賴順序 |
| `02-risk-register.md` | 已知風險、風險 owner、處理狀態 |
| `memory.md` | 穩定事實、專案約定、重要上下文 |
| `handoff.md` | 任務交接、目前狀態、下一步 |
| `tickets/` | 給 executor 的窄工單 |
| `reports/` | executor 每輪執行回報 |
| `reviews/` | reviewer findings 與 evidence |
| `decisions/` | 重要技術決策紀錄 |

## 4. 開案流程

### Step 0: Human Owner 提供初始 brief

開案時不要直接叫 AI「幫我做完整專案」。先提供明確 brief。

```md
# Project Brief

## 背景
- 這個專案要解決什麼問題？
- 現在痛點是什麼？
- 有哪些使用者或系統會受影響？

## 目標
- 必須完成什麼？
- 成功時使用者可以做什麼？

## 非目標
- 這次明確不做什麼？
- 哪些重構、功能或優化不能順手加入？

## 限制
- 技術限制：
- 時間限制：
- 相容性限制：
- 安全或資料限制：

## 驗收
- 必須通過哪些測試？
- 必須完成哪些 smoke？
- 哪些產品行為需要人工看過？
```

### Step 1: Orchestrator 先診斷，不急著寫 code

Orchestrator 的第一輪任務是降低熵，而不是產生大量 diff。

輸出必須包含：

- 問題理解
- 假設清單
- 需要確認的未知數
- 風險區域
- 建議讀取的檔案
- 初步驗收條件
- 拆分後的窄工單

Orchestrator prompt：

```md
你是本專案的 AI tech lead / orchestrator。

請先不要寫 code。請根據 brief 和 repo 狀態，完成以下工作：

1. 重述目標與非目標。
2. 找出主要風險與未知數。
3. 判斷需要讀哪些檔案或跑哪些指令。
4. 將任務拆成可獨立驗收的窄工單。
5. 為每張工單定義：
   - scope
   - allowed files
   - forbidden files
   - acceptance criteria
   - required tests / smoke
   - expected report format
6. 標示哪些部分需要 human owner 決策。

限制：
- 不要擴大 scope。
- 不要把 reviewer finding 視為事實，必須要求 evidence。
- 不要只相信 executor 自稱完成，必須以 diff 和測試證據判斷。
```

### Step 2: 建立 SPEC

`00-spec.md` 是整個專案的 done definition，不是裝飾。

```md
# SPEC: <project-name>

## Problem
<要解決的問題>

## Goals
- [ ] <目標 1>
- [ ] <目標 2>

## Non-Goals
- <這次不做的事情>

## Users / Systems Affected
- <使用者或系統>

## Expected Behavior
- <使用者可觀察到的行為>

## Constraints
- <技術、資料、安全、相容性、時間限制>

## Acceptance Criteria
- [ ] 測試：
- [ ] smoke：
- [ ] 真實資料或真實檔案驗證：
- [ ] 文件更新：
- [ ] human owner 驗收：

## Release / Merge Gate
- [ ] CI pass
- [ ] review findings 已仲裁
- [ ] 無未解 P0/P1
- [ ] 剩餘風險已記錄並被接受
```

### Step 3: 建立 PLAN

`01-plan.md` 不追求漂亮，而是追求可執行、可收斂。

```md
# PLAN

## Current Phase
<Discovery / Implementation / Review / Stabilization / Release>

## Workstream

| Ticket | Owner | Status | Depends On | Gate |
| --- | --- | --- | --- | --- |
| T-001 | Executor | Pending | None | unit + smoke |
| T-002 | Executor | Pending | T-001 | integration |

## Stop Conditions
- 任務超出原 scope。
- 測試或 smoke 無法跑。
- executor 修改 forbidden files。
- reviewer finding 涉及產品決策。
- 發現 SPEC 需要改。

## Current Risks
- <風險與處理方式>
```

## 5. 工單設計原則

Executor 最適合執行低熵、邊界清楚的任務。不要給 executor 大而模糊的需求。

### 好工單特徵

- 只做一件事
- 明確列出 allowed files
- 明確列出 forbidden files
- 有客觀驗收條件
- 有必跑測試
- 有清楚回報格式
- 可以在失敗時回滾或重新切小

### 壞工單特徵

- 「順便整理一下」
- 「把整個系統修好」
- 「看哪裡需要改就改」
- 「自己判斷完成就好」
- 沒有測試或 smoke
- 沒有禁止碰的範圍

### 工單模板

```md
# Ticket T-<number>: <title>

## Objective
<這張工單只完成一件事>

## Context
- 相關背景：
- 相關 SPEC 條目：
- 前置工單：

## Scope
### Allowed
- <允許做的事>

### Not Allowed
- <禁止做的事>

## Files
### Allowed Files
- `<path>`

### Forbidden Files
- `<path>`

## Acceptance Criteria
- [ ] <條件 1>
- [ ] <條件 2>

## Required Verification
- [ ] `npm test`
- [ ] `pytest`
- [ ] `curl ...`
- [ ] manual smoke:

## Report Required
請回報：
1. 你改了什麼。
2. 實際修改的檔案。
3. 測試與 smoke 結果。
4. 未完成事項。
5. 剩餘風險。
6. 是否有任何 scope deviation。
```

## 6. Executor 執行規範

Executor 只接窄工單，不自己重寫專案方向。

Executor 必須遵守：

- 先讀相關檔案再改。
- 只碰 allowed files。
- 不做順手重構。
- 不引入未要求的新框架。
- 不把格式化改動擴散到無關檔案。
- 修改後必須跑指定驗證。
- 驗證無法跑時必須明確說原因。
- 回報 diff 重點，不只回報「完成」。

Executor prompt：

```md
你是本專案 executor。請只執行以下工單，不要擴大 scope。

工單：
<貼上 ticket>

執行規則：
- 先讀相關檔案與現有模式。
- 只修改 allowed files。
- 不碰 forbidden files。
- 不做未要求重構。
- 若發現工單設計有問題，先停止並回報。
- 完成後跑 required verification。

回報格式：
## Summary
## Files Changed
## Verification
## Diff Notes
## Risks / Follow-ups
## Scope Deviations
```

### Executor 回報模板

```md
# Report T-<number>

## Summary
- <完成了什麼>

## Files Changed
- `<path>`: <變更摘要>

## Verification
| Check | Result | Evidence |
| --- | --- | --- |
| `<command>` | Pass / Fail / Not Run | <輸出重點或原因> |

## Diff Notes
- <重要實作細節>

## Risks / Follow-ups
- <剩餘風險>

## Scope Deviations
- None
```

## 7. Reviewer 使用規範

Reviewer 的任務是 aggressive review，不是當 commander。

Reviewer 可以質疑：

- 邊界條件
- API contract
- 錯誤處理
- 安全性
- 資料一致性
- race condition
- 測試缺口
- 回歸風險

Reviewer 不能：

- 直接要求 executor 修改
- 把假設包裝成事實
- 引入新需求
- 直接擴大 scope
- 決定任務是否 close

Reviewer prompt：

```md
你是本專案的異質 reviewer。請只做風險審查，不要指揮實作。

輸入：
- SPEC
- ticket
- executor report
- diff / changed files
- test result

請輸出 findings，並依照以下格式：

## Findings

| ID | Severity | Claim | Evidence | Suggested Check |
| --- | --- | --- | --- | --- |
| R-001 | P1/P2/P3 | <你認為的問題> | <具體檔案、行為、測試缺口或邏輯證據> | <如何驗證> |

## Non-Blocking Observations
- <不阻擋 close 的建議>

## Questions
- <需要 human 或 orchestrator 判斷的問題>

規則：
- 沒有 evidence 的 finding 必須標成 hypothesis。
- 不要提出與 ticket 無關的新功能。
- 不要假設 executor report 為真，請看 diff 和測試證據。
```

## 8. Orchestrator 仲裁規範

Reviewer finding 不能直接進入修復。Orchestrator 必須先仲裁。

### 仲裁結果類型

| 結果 | 說明 | 下一步 |
| --- | --- | --- |
| Accepted | finding 為真，且在本 ticket scope 內 | 開窄修復工單 |
| Accepted but Deferred | finding 為真，但不是本輪 scope | 記到 risk register 或 backlog |
| Rejected | finding 是假陽性或 evidence 不足 | 記錄拒絕原因 |
| Needs Human Decision | 涉及產品、商業、安全或風險接受 | 交給 human owner |
| Needs More Evidence | 目前無法判斷 | 要求補測試、補資料、補 reproduction |

### 仲裁模板

```md
# Review Arbitration: T-<number>

| Finding | Decision | Reason | Action |
| --- | --- | --- | --- |
| R-001 | Accepted / Rejected / Deferred / Human | <原因> | <下一步> |

## Fix Tickets Created
- T-<number>: <title>

## Human Decisions Needed
- <問題>
```

Orchestrator prompt：

```md
你是 orchestrator。請仲裁 reviewer findings。

輸入：
- SPEC
- ticket
- executor report
- reviewer findings
- diff / test evidence

請逐條判斷：
1. finding 是否有 evidence。
2. 是否為真問題。
3. 是否屬於本 ticket scope。
4. 是否阻擋 close。
5. 若要修，請拆成一張窄修復工單。

規則：
- 不要盲信 reviewer。
- 不要讓假陽性擴大 scope。
- 不要讓 executor 自己定義 done。
- 只能根據 SPEC、diff、測試與可觀察行為判斷。
```

## 9. 每一輪標準循環

每張工單都跑同一個 loop。

```text
Human brief
  -> Orchestrator 診斷與拆工單
  -> Executor 執行窄工單
  -> Executor 跑驗證並回報
  -> Reviewer 找風險
  -> Orchestrator 仲裁 findings
  -> 必要時開修復工單
  -> Objective gates 通過
  -> Human owner 驗收
  -> close / commit / handoff / memory 更新
```

### 每輪 close 條件

一輪任務只有在以下條件滿足時才算 close：

- 工單 acceptance criteria 已滿足。
- required verification 已跑，或無法跑的原因被接受。
- diff 已被 orchestrator 看過。
- reviewer findings 已仲裁。
- P0/P1 沒有未處理。
- 剩餘風險已記錄。
- human owner 接受產品行為與風險。

## 10. 測試與 Smoke Gate

「agent 說完成」不是完成。完成必須有證據。

### Gate 分層

| Gate | 目的 | 例子 |
| --- | --- | --- |
| Static | 快速抓語法、型別、格式問題 | lint、typecheck、compile |
| Unit | 驗證單一函式或模組 | unit tests |
| Integration | 驗證模組互動 | API tests、DB tests |
| E2E / Smoke | 驗證真實使用路徑 | browser smoke、curl、真實檔案 |
| Manual Product Check | 驗證產品是否符合預期 | human owner 看 UI / 行為 |

### 驗證回報要求

每個驗證都要回報：

- 跑了什麼指令
- pass / fail / not run
- 關鍵輸出
- 如果沒跑，原因是什麼
- 如果 fail，是阻擋問題還是已知問題

不要接受：

- 「應該可以」
- 「看起來沒問題」
- 「我已經修好」
- 「沒有時間跑測試」
- 「因為只是小改所以不用驗證」

## 11. Scope 控制

大型 AI 任務最容易失敗在 scope creep，而不是能力不足。

### Scope 控制規則

- 每張工單只解一個問題。
- 每輪修改前先列 allowed files。
- 每輪修改後檢查實際 touched files。
- 發現需要改 SPEC 時停止，不要偷改。
- reviewer 提的新需求不能直接進修復。
- 格式化、重構、命名整理不可和功能修復混在一起。

### Scope deviation 處理

如果 executor 超出 scope：

1. Orchestrator 判斷是否必要。
2. 必要且合理：更新 ticket 或 SPEC。
3. 不必要：要求回退該部分變更。
4. 有風險：交 human owner 決策。

## 12. 外部記憶與交接

長任務不能靠模型上下文記憶。每輪結束都要更新穩定文件。

### `memory.md` 模板

```md
# Project Memory

## Stable Facts
- <已確認不太會變的事實>

## Architecture Notes
- <系統結構與重要限制>

## Conventions
- <命名、測試、錯誤處理、資料格式約定>

## Decisions
- <已決策事項與原因>

## Known Risks
- <未解風險>

## Do Not Repeat
- <已證明錯誤的方向或假 finding>
```

### `handoff.md` 模板

```md
# Handoff

## Current Status
- <目前做到哪裡>

## Completed
- <已完成工單>

## In Progress
- <進行中工單>

## Blocked
- <阻塞點>

## Next Recommended Step
- <下一步>

## Commands / Checks
- <重要指令>

## Open Decisions
- <需要 human owner 決策>
```

## 13. Commit 與 PR 規範

Commit 是收斂點，不是自動產物。

### Commit 前檢查

- [ ] SPEC 對應項目已完成。
- [ ] 測試與 smoke 已跑。
- [ ] diff 沒有無關改動。
- [ ] reviewer findings 已仲裁。
- [ ] risk register 已更新。
- [ ] human owner 接受。

### Commit 原則

- 一個 commit 對應一個清楚目的。
- 不把重構和 bug fix 混在一起。
- 不 commit 未驗證的大量 AI diff。
- commit message 說明使用者可觀察的改變或技術風險處理。

### PR 描述模板

```md
## Summary
- <主要改動>

## Verification
- [ ] <command / smoke>

## Review Notes
- <需要 reviewer 特別看的地方>

## Risks
- <剩餘風險與緩解>

## AI Workflow
- Orchestrator:
- Executor tickets:
- Reviewer findings:
- Human decisions:
```

## 14. 常見失敗模式

| 失敗模式 | 徵兆 | 修正方式 |
| --- | --- | --- |
| 單一模型硬扛所有事 | 一直改、一直報進度、但 close 不起來 | 拆出 orchestrator / executor / reviewer |
| Executor 自己定義 done | report 說完成，但測試沒跑或產品行為不對 | done definition 外部化 |
| Reviewer 沒仲裁 | finding 一出現就亂修，scope 越來越大 | orchestrator 逐條查證 |
| 工單太大 | diff 爆炸、改到無關檔案 | 切成窄工單 |
| 沒有禁區 | agent 順手重構或改核心 contract | allowed / forbidden files |
| 沒有 objective gate | 只靠文字報告判斷 | 測試、smoke、真實資料 |
| 沒有 handoff | 下一輪重新理解上下文 | 更新 memory / handoff |
| 人類過早放手 | 產品方向慢慢漂移 | human owner 終審 |

## 15. Token 與成本策略

省 token 的核心不是少叫模型，而是少重工。

### 成本配置

- Orchestrator 花 token 在判斷、拆解、仲裁與讀 diff。
- Executor 花 token 在局部實作與驗證。
- Reviewer 花 token 在找風險，不碰大範圍修復。
- Human owner 只看產品行為、風險與最終決策。

### 節省 token 的方法

- 用 SPEC / PLAN / MEMORY 保存穩定上下文。
- 每次只給 executor 必要檔案與工單。
- Reviewer 只看 diff、SPEC、ticket、report。
- Orchestrator 不重讀整個 repo，只讀變更與 evidence。
- 假 finding 直接拒絕，不讓 executor 修。
- 工單過大就切小，不硬跑。

## 16. 專案啟動 Checklist

開新專案時照這張表執行。

- [ ] 建立 `ai-workflow/`。
- [ ] 寫 `00-spec.md`。
- [ ] 寫 `01-plan.md`。
- [ ] 定義 human owner。
- [ ] 指定 orchestrator。
- [ ] 指定 executor。
- [ ] 指定 reviewer。
- [ ] 定義測試與 smoke gate。
- [ ] 定義 forbidden files / forbidden scope。
- [ ] 建立第一批窄工單。
- [ ] 每張工單都有 acceptance criteria。
- [ ] 每張工單都有 required verification。
- [ ] 每輪結束更新 report / review / arbitration / memory。

## 17. 單輪執行 Checklist

每張 ticket 都照這張表。

- [ ] Orchestrator 已確認 ticket scope。
- [ ] Executor 已讀必要檔案。
- [ ] Executor 只修改 allowed files。
- [ ] Executor 沒有做順手重構。
- [ ] Executor 已跑 required verification。
- [ ] Executor report 已完成。
- [ ] Reviewer 已基於 diff 和 evidence review。
- [ ] Orchestrator 已仲裁所有 findings。
- [ ] 必要修復已拆成新 ticket。
- [ ] Objective gates 已通過。
- [ ] Human owner 已接受產品行為。
- [ ] Memory / handoff 已更新。

## 18. 最小可用版本流程

如果專案很小，不需要建立完整資料夾，也至少保留以下四件事。

```md
## Goal
<這次只做什麼>

## Scope
Allowed:
- <允許>

Forbidden:
- <禁止>

## Done
- [ ] <測試或 smoke>
- [ ] <產品行為>
- [ ] <風險接受>

## Report
- changed files:
- verification:
- remaining risks:
```

## 19. 建議工作節奏

### 小任務

1. Human 寫最小 goal。
2. Executor 直接做。
3. 跑測試。
4. Human 看結果。

### 中型任務

1. Orchestrator 拆 2 到 5 張 ticket。
2. Executor 逐張完成。
3. Reviewer 只看高風險 ticket。
4. Orchestrator 仲裁。
5. Human 終審。

### 大型任務

1. 建完整 `ai-workflow/`。
2. 先 discovery，不寫 code。
3. 建 SPEC / PLAN / risk register。
4. 每輪只執行一張窄工單。
5. 每個 milestone 都做 review + smoke。
6. 每天或每個重要節點更新 handoff。
7. 發布前做最終 review 和 human acceptance。

## 20. 目標演進與 SPEC 變更

專案目標會邊做邊變,這是正常的,不是失敗。架構本來就吃得下——關鍵是**目標的改動要走 SPEC,受控地改,而不是讓 executor 偷偷漂**。

### 核心觀念

- `project-brief.md` 是**人類的粗略意圖**,不需要一開始就完美。把它磨到很細,等於搶了 Orchestrator 第一輪診斷的工作。
- `00-spec.md` 是**活的 done-definition**,可以改,但每次改都是一個「有意識、有紀錄」的動作。
- 不確定要什麼時,不要假裝能一次寫死 SPEC。用 `01-plan.md` 的 `Current Phase: Discovery`,先開探路工單(spike)去「學到東西」,學到後再把 SPEC 收硬。

### brief 誰來磨、在哪磨

| 你的狀態 | 建議 |
| --- | --- |
| 自己都還沒想清楚要什麼 | 先在 chat 用高階模型「想出聲」,逼出粗 brief(這是幫你釐清,不是產出最終規格) |
| 已經知道大方向 | 直接寫粗 brief,進 Claude Code 讓 Orchestrator 磨 |

關鍵差別:**chat 模型看不到 repo,Orchestrator 看得到。** 磨規格這件事,Orchestrator 貼著真實程式碼磨,天生比 chat 強。所以主線是:**手寫粗 brief → Claude Code 最高模型當 Orchestrator,貼著 repo 盤問、產出 SPEC。**

### 受控的 SPEC 變更流程

做到一半發現目標要變時:

```text
發現目標 / 範圍要改
  -> 停(不要讓 executor 順手改方向,那叫 scope creep,頭號死因)
  -> Orchestrator 重新診斷,更新 00-spec.md / 01-plan.md
  -> 在 decisions/ 記一張 ADR 或在 memory.md 記一行「為什麼改」
  -> 需要的話重開 / 調整 tickets
  -> 繼續下一輪循環
```

這正是 `01-plan.md` 的 Stop Condition「發現 SPEC 需要改」要觸發的動作。改了什麼、為什麼改,一定要留一行紀錄,下一輪任何 agent 讀 memory / handoff 才知道現況。

### 探索型專案的合法「邊做邊修」

1. 寫一份**刻意很薄**的 brief(只有大方向)。
2. Orchestrator 開幾張**探路工單**——目的是學到東西,不是交付功能。
3. 學到之後把 SPEC 收硬,進 Implementation phase。

這是「一邊修目標」的正確版本:**先探索、再定案**,而不是一路模糊到底、讓範圍無聲漂移。

## 21. 最終原則

這套流程的本質是工程紀律，不是神奇 prompt。

最強模型負責判斷，不負責苦工。

coding agent 負責執行，不負責定義完成。

reviewer 負責懷疑，不負責拍板。

測試與 smoke 負責提供客觀證據。

人類負責產品方向與最終責任。

當每個角色都放在正確位置，AI 協作才會更快、更穩、更省，也更容易真的交付。
