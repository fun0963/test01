# Report T-002

## Summary
- 新增 `tests/test_txtstat.py`（純標準庫 `unittest`），涵蓋一般檔、空檔、檔案不存在三案，透過 `subprocess` 執行 `python3 txtstat.py <path>` 驗證 stdout/stderr/exit code，貼近實際使用路徑。
- 未修改 `txtstat.py`。

## Files Changed
- `tests/test_txtstat.py`（新建）：三個測試案例，皆用 `tempfile` 產生測試資料，測完刪除，不殘留檔案。
- `tests/__init__.py`（新建，空檔）：讓 `tests/` 成為 package，供 `unittest discover` 使用。

## Verification
| Check | Result | Evidence |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -v` | Pass | `test_empty_file ... ok` / `test_nonexistent_file ... ok` / `test_normal_file ... ok`，`Ran 3 tests in 0.052s` / `OK` |
| `python3 -m py_compile txtstat.py` | Pass | 無輸出，exit 0（`txtstat.py` 未改動，本步驟僅確認仍可編譯） |

執行中產生的 `__pycache__/` 目錄（`txtstat.cpython-312.pyc`、`tests/__pycache__/`）在 commit 前已刪除，未加入版本控制。

## Diff Notes
- 三案測試皆走 `subprocess.run([sys.executable, TXTSTAT_PATH, path], capture_output=True, text=True)`，符合工單建議「至少錯誤案用它驗 exit code」，這裡三案都採用同一驅動方式以保持一致。
- 一般檔案案例內容為 `"hello world\nsecond line\n"`，與 `03-gates.md` Smoke gate 使用的樣本一致，預期 `lines=2 words=4 chars=24`，直接斷言 stdout 字串。
- 空檔案案例斷言 `lines=0 words=0 chars=0`、exit 0。
- 檔案不存在案例：用 `tempfile.TemporaryDirectory()` 產生一個目錄，組出目錄內一個「不存在」的檔名（目錄本身測完會自動清除），斷言 exit code 1、stderr 含 `error:`、stdout 為空字串。
- 測試中用 `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` 定位 repo root 以取得 `txtstat.py` 的絕對路徑，避免相依於執行時的當前工作目錄。

## Risks / Follow-ups
- 三個測試都沒有揭露 `txtstat.py` 的 bug，實際輸出與工單預期完全一致，無需額外仲裁票。
- 測試目前只涵蓋工單要求的三案（一般檔/空檔/不存在），未涵蓋其他 edge case（例如無讀取權限、非 UTF-8 編碼內容等），非本票範圍。

## Scope Deviations
- None
