# WORKFLOW：實際怎麼跑

> 這份是「操作手冊」——每個角色的**開場怎麼講**,加上一個從開案到 close 的完整範例。
> 原理見 [`AI_COLLAB_DEVELOPMENT_GUIDE.md`](AI_COLLAB_DEVELOPMENT_GUIDE.md),速查見 [`USAGE.md`](USAGE.md)。

---

## 0. 母版 vs 專案副本

`ai-workflow/` 這份是**空白母版**,自足、可整包複製。用法:

- **母版**:保存在你的模板來源處,永遠保持空白,不在裡面填真實專案內容。
- **專案副本**:`cp -r ai-workflow` 到新專案根目錄後,在副本裡填寫。模型讀寫的是這個副本。

所有模型(orchestrator / executor / reviewer)都開在**同一個真實專案根目錄**,
不各自擁有資料夾。專案裡的 `ai-workflow/` 就是它們之間的**共享黑板**:它們不直接對話,靠檔案交接。

```
你的真實專案/
├── src/                  ← 實際 code
└── ai-workflow/          ← 從母版複製來,共享黑板
    ├── 00-spec.md        ← Orchestrator 寫
    ├── 03-gates.md       ← 開案時填本專案 gate 指令
    ├── tickets/          ← Orchestrator 寫,Executor 讀
    ├── reports/          ← Executor 寫
    ├── reviews/          ← Reviewer 寫 + Orchestrator 補仲裁
    ├── memory.md         ← 每輪更新
    └── handoff.md        ← 每輪更新
```

---

## 1. 開案(一次性):人類與 AI 的分工

> 一句話原則:**要瀏覽器 OAuth、花錢授權、產品判斷、接受風險的 → 人類;
> 可用檔案與 API 完成的機械步驟 → AI 代辦;LLM 額度只花在固定的呼叫點。**

| # | 事項 | 誰 | 說明 |
|---|---|---|---|
| 1 | 建新 repo:GitHub 上對母版按 **Use this template**(或 `cp -r ai-workflow` 進既有專案) | 人 | 產生的 repo 歷史是 squash 過的 `Initial commit` |
| 2 | 本機 `claude setup-token` → 設 repo secret `CLAUDE_CODE_OAUTH_TOKEN` | **人** | 瀏覽器 OAuth,AI 無法代辦;CI 與互動**共用**訂閱額度 |
| 3 | CodeRabbit App 授權涵蓋新 repo(`github.com/apps/coderabbitai` → Configure) | **人** | 網頁授權,AI 無法代辦 |
| 4 | 建 `protect-main` ruleset(必須走 PR + `scope-check` required + 禁 force-push,admin 可 bypass) | 人或 AI | AI 可用 API 照母版複製(PAT 需 Administration RW) |
| 5 | 開**金絲雀 PR**:實測 scope-check 會跑綠、CodeRabbit 會出現 review | AI | 0 Claude 額度;驗完關 PR、刪 branch |
| 6 | 填 `ai-workflow/project-brief.md`(背景/目標/非目標/限制/驗收) | **人** | 產品意圖只有人知道;這是整條 pipeline 的輸入 |
| 7 | 把 `ai-workflow/03-gates.md` 換成本專案真實 gate 指令 | AI 起草、人拍板 | Orchestrator 提議 lint/test/smoke,人確認每條真的能跑 |
| 8 | 首跑 **AI Orchestrator**:診斷 + 拆工單(產 00-spec/01-plan/tickets) | AI(opus) | 跑前後用 `/usage` 記額度,建立用量基準 |
| 9 | 審 plan PR(spec/plan/工單)後 merge | **人** | 工單的 Allowed Files 就是日後 scope-check 的執法依據,務必看過 |

若**只用本機互動模式**(不接 GitHub pipeline):只需 1、6、7,見 [`USAGE.md`](USAGE.md) 的「開案三步」。
進入每輪循環後的分工見 [`.github/README.md`](../.github/README.md) 的「每輪循環」表——人只按幾次按鈕加終審,其餘自動。

---

## 2. 三個角色的開場(可直接抄)

> `prompts/*.md` 是**你的 prompt 參考庫**;下面是你實際貼給模型的「開場訊息」。
> 每個角色是獨立 context——它不會記得你跟別人聊過什麼,需要的東西要整段貼進去。

### 2-1. Orchestrator 開場（第一輪:只讀不寫 code）

```md
你是本專案的 orchestrator,遵守 AI_COLLAB_DEVELOPMENT_GUIDE.md 與
ai-workflow/README.md 的角色分工。

請先讀 ai-workflow/project-brief.md 和相關 repo 結構,【先不要寫 code】。
然後照 ai-workflow/prompts/orchestrator.md 的 Prompt A：
1. 重述目標與非目標
2. 找出風險與未知數
3. 判斷要讀哪些檔
4. 拆成可獨立驗收的窄工單,每張定義 scope / allowed / forbidden /
   acceptance / required verification / report 格式
5. 標示哪些需要 human 決策

把結果寫進 ai-workflow/00-spec.md、01-plan.md、tickets/T-00X-*.md。
```

**期望產出**:spec、plan、一批 tickets。**不是 diff。**

### 2-2. Executor 開場（一次一張工單）

```md
你是本專案的 executor。工作目錄是這個專案根目錄,規則見
ai-workflow/prompts/executor.md。

請【只執行下面這張工單,不要擴大 scope】。開始前先讀工單列出的相關檔案,
理解現有寫法再改。

---
(把 ai-workflow/tickets/T-001-xxx.md 的內容整段貼在這裡)
---

執行規則：
- 只改 Allowed Files,絕對不碰 Forbidden Files
- 不做未要求的重構、不引入新框架、不擴散格式化改動
- 若發現工單本身有問題或做不到,先停下來回報,不要自己改方向
- 改完跑 Required Verification;跑不了要說明原因

完成後把回報寫進 ai-workflow/reports/T-001-report.md,格式照 executor.md：
Summary / Files Changed / Verification / Diff Notes / Risks / Scope Deviations
```

**重點**:1. 一次一張,close 了再給下一張 2. ticket 整段貼進去,別只給檔名 3. 要求先讀再改。

### 2-3. Reviewer 開場（只找風險,不指揮）

```md
你是本專案的異質 reviewer,規則見 ai-workflow/prompts/reviewer.md。
請【只做風險審查,不要指揮實作、不要提新功能】。

輸入：
- SPEC：ai-workflow/00-spec.md
- 工單：ai-workflow/tickets/T-001-xxx.md
- executor 回報：ai-workflow/reports/T-001-report.md
- 這張工單的 diff / changed files
- 測試結果

輸出 findings 到 ai-workflow/reviews/T-001-review.md,照 reviewer.md 的表格格式。
沒有 evidence 的 finding 標成 hypothesis;不要假設 executor report 為真,看 diff 和測試。
```

### 2-4. Orchestrator 仲裁（把 review 貼回去）

```md
你是 orchestrator,請仲裁下面的 reviewer findings(Prompt B)。
逐條判斷:有無 evidence / 是否為真 / 是否在本 ticket scope / 是否阻擋 close /
要修就拆成一張窄修復工單。

輸入:00-spec.md、ticket、report、下面的 review、diff/測試。
把仲裁結果寫進 ai-workflow/reviews/T-001-review.md 的 Arbitration 區。

---
(把 reviews/T-001-review.md 的 findings 貼進來)
---
```

---

## 3. 對照:給誰什麼

| 角色 | 開場給的東西 | 期望第一個動作 |
| --- | --- | --- |
| Orchestrator | `project-brief.md` + 架構 | **不寫 code**,診斷 + 拆工單 |
| Executor | 一張 `tickets/T-001.md` + 執行規則 | 先讀檔,再**只改指定範圍**,跑驗證 |
| Reviewer | SPEC + ticket + report + diff | 只輸出 findings,不指揮 |

一句話:給 Orchestrator 的是「問題」,給 Executor 的是「已經切好的答案邊界」。

### 每個角色的閱讀清單(控制噪音)

> Agent 不會被資料夾大小誤導,只會被「你塞進它 context 的東西」誤導。
> 噪音靠**窄的閱讀清單**控制,不是靠刪檔。每個角色只給下面這一小份:

| 角色 | 只需要讀 | **不要**給它 |
| --- | --- | --- |
| Orchestrator | `project-brief` `00-spec` `01-plan` `03-gates` `memory` `handoff` + 相關 repo 檔 | executor 的實作細節 |
| Executor | **一張 ticket(整段貼)** + 該 ticket 的 allowed files（ticket 的 Required Verification 已指向 `03-gates`) | 別的 ticket、reviews、整份 spec |
| Reviewer | `00-spec` `03-gates` + 那一張 ticket + 那一份 report + diff | 舊 report、別張 ticket |

只要這樣指定,`reports/` 堆再多舊報告也不干擾 executor——它根本沒讀到。
**唯二會出事**:①叫 agent「讀 `ai-workflow/` 看一下」→ 翻到過期檔當現況;
②`memory.md` / `handoff.md` 沒更新 → agent 只好去翻舊 report,被舊資訊帶偏。

### 兩類檔案:當下真相 vs 歷史存檔

- **當下真相**(小、永遠最新,agent 主要讀這些):`memory.md`、`handoff.md`、`01-plan.md`、`00-spec.md`
- **歷史存檔**(會變多,**給人查證用,不整包餵 agent**):`tickets/`、`reports/`、`reviews/`、`decisions/`

---

## 4. 完整範例:一輪從開案到 close

假設專案是「幫 API 加上 request rate limiting」。

**① Human** 填 `project-brief.md`:目標=防止單一 IP 濫用;非目標=不改認證邏輯;驗收=超過限額回 429 + 有測試。

**② Orchestrator**(開場 2-1,只讀不寫)產出:
- `00-spec.md`:Acceptance = 「同 IP 每分鐘 >100 次回 429」「有 unit + smoke」
- `tickets/T-001-add-rate-limiter.md`:
  - Allowed Files:`src/middleware/rateLimit.js`、`src/app.js`
  - Forbidden Files:`src/auth/*`
  - Required Verification:`npm test`、`curl` 連打 101 次看 429

**③ Human → Executor**(開場 2-2,貼 T-001 整段)。Executor:
- 讀 `src/app.js` 現有 middleware 寫法
- 新增 `rateLimit.js`,接到 `app.js`
- 跑 `npm test` pass、`curl` 第 101 次得到 429
- 寫 `reports/T-001-report.md`,Scope Deviations = None

**④ Human → Reviewer**(開場 2-3,附 diff)。Reviewer 寫 `reviews/T-001-review.md`:
- R-001 (P2):「重啟後計數歸零,分散式部署會失效」evidence=用記憶體 Map
- R-002 (P3):「429 沒帶 Retry-After header」

**⑤ Human → Orchestrator 仲裁**(開場 2-4)。結果寫回同檔 Arbitration 區:
- R-001 → **Accepted but Deferred**:真問題,但本輪非目標(單機夠用),記進 `02-risk-register.md`
- R-002 → **Accepted**:小且在 scope,開 `T-002-add-retry-after.md`

**⑥ Gates**:`npm test` pass、smoke 得到 429。✅

**⑦ Human 驗收**:行為符合預期,接受 R-001 的剩餘風險。

**⑧ Close(記憶蒸餾)**:把 report/review 裡「以後還需要記得的結論」蒸餾一兩行進
`memory.md`(「rate limit 用記憶體 Map,分散式部署待處理」)、更新 `handoff.md` 的
Current Status(「T-001 done;下一步 T-002」)、`01-plan.md` 把 T-001 標 Done。commit。

→ 接著回到 ③,把 T-002 給 Executor,同一個 loop 再跑一次。

---

## 5. 每輪 close 的記憶蒸餾訣竅(必做)

> 這一步決定了下一輪的噪音高低,不能省。

每輪 close 時:

1. **蒸餾**:把 `reports/`、`reviews/` 裡「以後還需要記得的結論」濃縮成一兩行,寫進 `memory.md`
   (穩定事實 / 已決策 / Do Not Repeat)。**不是複製整份報告,是留結論。**
2. **更新現況**:改 `handoff.md` 的 Current Status(做到哪、下一步)、`01-plan.md` 的工單狀態。
3. **存檔留著別動**:`reports/`、`reviews/`、`tickets/` 保留原樣,那是**給人查證的稽核軌跡,不是給 agent 讀的**。

這樣下一輪任何 agent 只要讀 `memory.md` + `handoff.md` 兩個小檔就懂現況,
**永遠不必去翻 20 份舊報告**,context 乾淨、省 token、也不會被舊狀態帶偏。

---

## 6. 常見誤區

- **同一個模型兼兩角**(自己拆工單、自己執行、自己說完成)→ 退回單一模型硬扛。角色的價值來自**獨立 context**。
- **一次丟多張工單** → diff 爆炸、難審。一次一張。
- **只給 executor 檔名不給 ticket 內容** → 它沒有邊界依據,會自由發揮。
- **reviewer finding 直接叫 executor 修** → 跳過仲裁,scope 失控。一律先仲裁。
- **叫 agent「讀 `ai-workflow/` 看一下」** → 它翻到過期 / 半成品檔當現況。永遠給窄的閱讀清單。
- **close 時不蒸餾 memory / handoff** → 下一輪 agent 得翻舊 report,被舊狀態帶偏。每輪必做(見 §5)。
