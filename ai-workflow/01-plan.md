# PLAN

> 不追求漂亮，追求可執行、可收斂。

## Current Phase
Implementation（brief 已夠明確，不需 Discovery spike；唯一未知數是 D1–D4，已記入 SPEC Open Decisions，不阻擋開工，只阻擋 smoke 宣告綠燈）。

## Workstream

| Ticket | Owner | Status | Depends On | Gate |
| --- | --- | --- | --- | --- |
| T-001 實作 txtstat.py CLI | Executor | Done | None | Static + Smoke |
| T-002 加 unittest 測試 | Executor | Done | T-001 | Unit |
| T-003 修復 UnicodeDecodeError | Executor | Done | T-001, T-002 | Smoke + Unit |

Status 建議值：Pending / In Progress / In Review / Blocked / Done。

依賴說明：T-002 的測試 import / 執行 `txtstat.py`，故依賴 T-001 先落地。兩張各自有獨立可驗收的 gate。

## Stop Conditions
- 任務超出原 scope（例如順手加旗標、支援多檔、讀 stdin）。
- 測試或 smoke 無法跑。
- executor 修改 forbidden files（`ai-workflow/`、`.github/`、另一張票的 allowed file）。
- reviewer finding 涉及產品決策（例如統計語意 D1–D4）。
- 發現 SPEC 需要改 → 停，回 Orchestrator 走受控 SPEC 變更。

## Current Risks
- R1（P1，阻擋 smoke）：Smoke gate 期望值 `words=3` 與輸入（4 字）矛盾 → SPEC D1，待 human。
- R2（P2）：`chars` / `lines` 邊界語意未定 → SPEC D2/D3，已給預設，先做後確認。
- R3（P3）：錯誤訊息格式主觀 → SPEC D4，human 驗收時看。
- 明細見 `02-risk-register.md`。

## Human Decisions Needed
- D1 拍板（怎麼修正 smoke gate 一致性）——這是唯一會擋住 close 的項目。
- D2/D3/D4 確認 Orchestrator 預設是否可接受。
