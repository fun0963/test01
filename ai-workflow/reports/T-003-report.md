# Report T-003

## Summary
- 把 `txtstat.py` 讀檔區塊的 `except OSError as e:` 改為 `except (OSError, UnicodeDecodeError) as e:`，讓非 UTF-8 / 損壞編碼的檔案改走既有 `error: <原因>` / stderr / exit 1 路徑，不再拋出未捕捉的 `UnicodeDecodeError` traceback。成功路徑、輸出格式、`compute_stats` 語意均未變動。

## Files Changed
- `txtstat.py`：第 20 行 `except` clause 由 `OSError` 擴充為 `(OSError, UnicodeDecodeError)`，其餘不變。

## Verification
| Check | Result | Evidence |
| --- | --- | --- |
| `python3 -m py_compile txtstat.py` | Pass | 無輸出、exit 0（`echo "STATIC_OK"` 有印出） |
| Smoke：`printf 'hello world\nsecond line\n' > /tmp/smoke.txt && python3 txtstat.py /tmp/smoke.txt` | Pass | stdout：`lines=2 words=4 chars=24` |
| 非 UTF-8 manual smoke：`printf '\xff\xfe' > /tmp/bad.txt && python3 txtstat.py /tmp/bad.txt` | Pass | exit code = 1；stdout 空；stderr = `error: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`；無 traceback |
| 回歸：不存在檔 `python3 txtstat.py /tmp/does-not-exist.txt` | Pass | exit code = 1；stdout 空；stderr = `error: [Errno 2] No such file or directory: '/tmp/does-not-exist.txt'` |
| 回歸：空檔 `python3 txtstat.py /tmp/empty.txt` | Pass | stdout = `lines=0 words=0 chars=0` |
| `python3 -m unittest discover -s tests -v`（03-gates.md 列為每張工單必須） | Not Run | repo 目前無 `tests/` 目錄（`ls tests` → `No such file or directory`；`git log --all -- tests/` 無任何紀錄），非本工單改動造成，也非本工單 Allowed Files 範圍。此為既有環境缺口，非本次 scope deviation。 |

## Diff Notes
- 僅擴充例外型別 tuple，`print(f"error: {e}", file=sys.stderr)` 與 `sys.exit(1)` 行為完全沿用既有程式碼，未新增分支或訊息格式。

## Risks / Follow-ups
- `tests/` 目錄在整個 repo 歷史中皆不存在，導致 Unit gate 長期無法執行；建議另開工單補上單元測試目錄與案例（包含本次 UnicodeDecodeError case），非本工單範圍故未處理。

## Scope Deviations
- None
