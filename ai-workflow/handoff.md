# Handoff

> 每輪結束或換人 / 換 session 時更新。目的是讓接手者不必重讀整個歷史。

## Current Status
- T-001 實作完成（PR #3 已 merge 進 main），smoke 全綠；T-003（UnicodeDecodeError 修復）已開票；待 T-002 補測試

## Completed
- T-001：txtstat.py CLI 實作完成，通過 static + smoke gate

## In Progress
- T-003：txtstat.py except 併入 UnicodeDecodeError（窄修復）
- T-002：補充 unittest 測試框架

## Blocked
- <阻塞點與需要誰處理>

## Next Recommended Step
- 優先執行 T-003（窄修復 UnicodeDecodeError），使 G2 格式完整，建議 T-002 測試前先跑；後接 T-002 補 unittest

## Commands / Checks
- <重要指令：如何跑測試、smoke、啟動服務>

## Open Decisions
- <需要 human owner 決策的事項>
