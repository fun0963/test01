# ai-workflow

這是每個專案共用的 AI 協作開發模板,設計成**單一自足資料夾**:整份 `ai-workflow/`
複製到新專案根目錄即可開工,不依賴外層任何檔案。

- 設計原則、角色分工、完整說明見 [`AI_COLLAB_DEVELOPMENT_GUIDE.md`](AI_COLLAB_DEVELOPMENT_GUIDE.md)。
- 速查見 [`USAGE.md`](USAGE.md)。
- **實際操作(每個角色的開場怎麼講 + 從開案到 close 的完整範例)見 [`WORKFLOW.md`](WORKFLOW.md)。**

> 這份 `ai-workflow/` 是**空白母版**。複製後在新專案的副本裡填寫,不要把真實專案內容寫進母版。

## 核心角色（一句話版）

- **Human Owner**：產品方向與最終責任。
- **Orchestrator**（最強推理模型）：診斷、拆工單、定義 done、仲裁、讀 diff。
- **Executor**（coding agent）：只接窄工單、只改 allowed files、跑驗證、回報。
- **Reviewer**（異質模型）：只找風險，不拍板、不指揮。
- **Objective Gates**：測試 / smoke / 真實資料，提供客觀證據。

## 怎麼用這個模板

1. 把整個 `ai-workflow/` 複製到新專案根目錄。

   ```bash
   cp -r /path/to/this/ai-workflow ./ai-workflow
   ```

2. 填寫 `project-brief.md`（Human Owner 的初始 brief）。
3. 讓 Orchestrator 用 `prompts/orchestrator.md` 先診斷、拆工單，寫出 `00-spec.md`、`01-plan.md`；並和 Human 一起把 `03-gates.md` 的 gate 指令換成本專案真實指令。
4. 每張工單複製 `tickets/T-000-template.md` → `tickets/T-00X-<title>.md`。
5. 每輪跑一次標準循環（見下），把產物寫進 `reports/`、`reviews/`、`decisions/`。
6. 每輪結束更新 `memory.md` 與 `handoff.md`。

小專案不想建整個資料夾，就只用 `MINIMAL.md`。

## 標準循環

```text
Human brief
  -> Orchestrator 診斷與拆工單
  -> Executor 執行窄工單並跑驗證回報
  -> Reviewer 找風險
  -> Orchestrator 仲裁 findings
  -> 必要時開修復工單
  -> Objective gates 通過
  -> Human owner 驗收
  -> close / commit / handoff / memory 更新
```

## 目錄結構

```text
ai-workflow/
  AI_COLLAB_DEVELOPMENT_GUIDE.md  # 完整原理(隨資料夾一起帶著走)
  USAGE.md                        # 速查
  WORKFLOW.md                     # 操作手冊:角色開場 + 完整範例
  README.md                       # 本檔
  project-brief.md      # Step 0：Human Owner 初始 brief
  00-spec.md            # done definition
  01-plan.md            # 階段計畫、工單列表、依賴
  02-risk-register.md   # 風險登記
  03-gates.md           # Objective Gates:gate 指令權威來源
  memory.md             # 穩定事實 / 約定 / 已決策
  handoff.md            # 交接狀態、下一步
  MINIMAL.md            # 小專案最小流程
  Orchestrator啟動對話.md  # 可直接貼的 orchestrator 開場
  Executor啟動對話.md      # 可直接貼的 executor 開場
  prompts/              # 角色 prompt 參考庫
    orchestrator.md
    executor.md
    reviewer.md
    arbitration.md
  tickets/              # 給 executor 的窄工單
    T-000-template.md
  reports/              # executor 每輪回報
    T-000-report-template.md
  reviews/              # reviewer findings + 仲裁
    T-000-review-template.md
  decisions/            # 重要技術決策 (ADR)
    ADR-000-template.md
```

## 每輪 close 條件

- [ ] 工單 acceptance criteria 已滿足。
- [ ] required verification 已跑（或無法跑的原因被接受）。
- [ ] diff 已被 Orchestrator 看過。
- [ ] reviewer findings 已仲裁。
- [ ] P0/P1 沒有未處理。
- [ ] 剩餘風險已記錄。
- [ ] Human Owner 接受產品行為與風險。
