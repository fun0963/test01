# Ticket T-004: test_empty_file 補 stderr 斷言

> 好工單只做一件事、有明確禁區、有客觀驗收。
> 來源：PR #6 仲裁（`reviews/T-002-review.md` R-002 Accepted）。

## Objective
讓 `tests/test_txtstat.py` 的 `test_empty_file` 也斷言成功路徑 `stderr` 為空，使三案（一般檔/空檔/不存在檔）stderr 斷言風格一致。**只加這一行斷言，不做其他事。**

## Context
- 相關背景：CodeRabbit 於 PR #6 提出、Orchestrator 仲裁 Accepted 的真問題（🔵 Trivial / consistency）。
- 根因：`test_normal_file` 與 `test_nonexistent_file` 皆斷言 `result.stderr`，唯 `test_empty_file` 未驗證成功時 stderr 為空。
- 相關 SPEC 條目：**G3**（unittest 覆蓋三案）；Expected Behavior（成功路徑不寫 stderr）。
- 前置工單：T-002（已在 `ticket/T-002` / PR #6）。

## Scope
### Allowed
- 於 `tests/test_txtstat.py` 的 `test_empty_file`，在既有斷言後加 `self.assertEqual(result.stderr, "")`，沿用既有 `result` 變數與其他案相同風格。

### Not Allowed
- 不改 `txtstat.py`、不改其他測試案的邏輯。
- 不引入第三方測試框架（pytest 等），只用標準庫 `unittest`。
- 不動 `ai-workflow/**`、`.github/**` 或其他既有檔案。
- 不做未要求的重構或格式化擴散。

## Files
### Allowed Files
- `tests/test_txtstat.py`

### Forbidden Files
- `txtstat.py`
- `ai-workflow/**`、`.github/**`
- `README.md`、`PROJECT-HANDOFF.md`、`.gitignore`
- 其他任何既有檔案

## Acceptance Criteria
- [ ] `test_empty_file` 含 `self.assertEqual(result.stderr, "")`。
- [ ] `python3 -m unittest discover -s tests -v` 全綠（3 案不回歸）。

## Required Verification
> gate 指令權威來源是 `../03-gates.md`。
- [ ] `03-gates.md`：Unit —— `python3 -m unittest discover -s tests -v`

## Report Required
1. 你改了什麼。
2. 實際修改的檔案。
3. 測試結果（貼 `unittest -v` 輸出重點：跑幾個、全綠）。
4. 未完成事項。
5. 剩餘風險。
6. 是否有任何 scope deviation。
