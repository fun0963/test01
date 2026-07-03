# Arbitration 說明

> Reviewer finding 不能直接進入修復。Orchestrator 必須先仲裁，結果寫進 `reviews/T-XXX-review.md`。
> 仲裁用的 prompt 見 [`orchestrator.md`](orchestrator.md) 的 Prompt B。

## 仲裁結果類型

| 結果 | 說明 | 下一步 |
| --- | --- | --- |
| Accepted | finding 為真，且在本 ticket scope 內 | 開窄修復工單 |
| Accepted but Deferred | finding 為真，但不是本輪 scope | 記到 risk register 或 backlog |
| Rejected | finding 是假陽性或 evidence 不足 | 記錄拒絕原因 |
| Needs Human Decision | 涉及產品、商業、安全或風險接受 | 交給 human owner |
| Needs More Evidence | 目前無法判斷 | 要求補測試、補資料、補 reproduction |

## 仲裁輸出格式

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
