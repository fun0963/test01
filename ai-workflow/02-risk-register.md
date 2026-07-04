# Risk Register

> 已知風險、風險 owner、處理狀態。剩餘風險必須被 Human Owner 明確接受。

## Active Risks

| ID | Severity | Risk | Impact | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RK-001 | P1 | Smoke gate 期望值 `words=3` 與輸入 `'hello world\nsecond line\n'`（實含 4 字）矛盾 | Smoke gate 無法宣告綠燈，擋 close | Human | 見 SPEC D1：擇一修正 gate 期望值(→`words=4`)或改 smoke 輸入為 3 字檔 | Open |
| RK-002 | P2 | `chars`/`lines` 邊界語意未定（尾端換行是否計、byte vs code point、無尾換行的行數） | 數值可能與 human 預期不符 | Orchestrator | 見 SPEC D2/D3，已給預設語意；human 驗收時確認 | Open |
| RK-003 | P3 | 錯誤訊息 `error: <原因>` 格式主觀 | 訊息可能不夠友善 | Human | 見 SPEC D4，預設帶 OS 例外訊息；human 驗收看 | Open |
| RK-004 | P3 | 非 UTF-8 / 損壞編碼檔會拋 `UnicodeDecodeError`（`ValueError` 子類，非 `OSError`），繞過 `error:` 路徑印 traceback，違反 G2 訊息格式 | 邊界輸入下錯誤輸出非預期格式（exit 仍為 1） | Orchestrator | T-003（PR #5）已把 `UnicodeDecodeError` 併入 except；Orchestrator 於 PR #5 仲裁獨立實跑非 UTF-8 檔確認走 `error:`、exit 1、無 traceback（`reviews/T-003-review.md` O-003） | **Resolved (pending merge)**——PR #5 merge 後移入 Closed Risks |

Severity：P0 阻擋發布 / P1 高 / P2 中 / P3 低。

## Accepted Risks
> Human Owner 已知並接受的剩餘風險。

- <風險>：接受人 <name>，日期 <YYYY-MM-DD>，理由 <為何可接受>。

## Closed Risks
- <已消除的風險與如何消除>
