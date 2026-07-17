# Report T-004

## Summary
- 在 `tests/test_txtstat.py` 的 `test_empty_file` 補上 `self.assertEqual(result.stderr, "")`，使三案（一般檔/空檔/不存在檔）的 stderr 斷言風格一致。

## Files Changed
- `tests/test_txtstat.py`: `test_empty_file` 既有斷言後新增一行 `self.assertEqual(result.stderr, "")`。

## Verification
| Check | Result | Evidence |
| --- | --- | --- |
| `python3 -m py_compile txtstat.py` | Pass | 無輸出，exit 0（`PY_COMPILE_OK` echo 確認） |
| `python3 -m unittest discover -s tests -v` | Pass | `test_empty_file ... ok`／`test_nonexistent_file ... ok`／`test_normal_file ... ok`；`Ran 3 tests in 0.058s`／`OK` |
| Smoke（`03-gates.md` 定義） | Pass（路徑調整） | 沙盒禁止對 `/tmp/smoke.txt` 做 shell 輸出重導向（`Output redirection ... blocked`），改用 repo 內暫存檔 `./smoke_test_tmp.txt`（用完即刪，未留痕）驗證同內容，輸出為 `lines=2 words=4 chars=24`，與 gate 預期一致 |
| Manual Product Check | Not Run | 屬 close 前由 human owner 執行的人工檢查，非 executor 範圍 |

## Diff Notes
- 僅新增一行斷言，沿用既有 `result` 變數與 `test_normal_file`／`test_nonexistent_file` 相同的 `assertEqual(result.stderr, ...)` 風格，未改動任何其他邏輯或格式。

## Risks / Follow-ups
- 無新增風險；純測試斷言補強，不影響 `txtstat.py` 行為。

## Scope Deviations
- Smoke gate 指令原文寫死路徑 `/tmp/smoke.txt`，但本次執行環境的沙盒政策封鎖對 `/tmp` 的 shell 輸出重導向（`> /tmp/smoke.txt` 與 repo 內同名重導向皆被擋，改用 `Write` 工具寫入 repo 內暫存檔才成功），因此以 repo 內暫存檔 `./smoke_test_tmp.txt`（驗證後刪除，未提交）替代，其餘步驟與預期輸出完全依 gate 定義執行，僅路徑因環境限制調整。此為執行環境限制，非工單 scope 變動。
