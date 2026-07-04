# Report T-001

## Summary
- 新增單檔 CLI `txtstat.py`(repo 根目錄),依 SPEC 預設語意計算 lines/words/chars,成功時印 `lines=<L> words=<W> chars=<C>` 到 stdout(exit 0),失敗時印 `error: <原因>` 到 stderr(exit 1、stdout 無輸出)。未新增/修改任何測試檔。

## Files Changed
- `txtstat.py`(新建):純標準庫,提供 `compute_stats(text) -> (lines, words, chars)` 供 T-002 import,以及 `main()` / `if __name__ == "__main__":` 進入點。

## Verification
| Check | Result | Evidence |
| --- | --- | --- |
| `python3 -m py_compile txtstat.py` | Pass | exit=0,無輸出 |
| `python3 -m unittest discover -s tests -v` | Not Run | `tests/` 目錄尚不存在(建立測試是 T-002 的範圍,本工單 Not Allowed 建立測試檔),故 Unit gate 對本工單不適用 |
| Smoke:`printf 'hello world\nsecond line\n' > /tmp/smoke.txt && python3 txtstat.py /tmp/smoke.txt` | Pass | stdout=`lines=2 words=4 chars=24`,exit=0,與 `03-gates.md`(已依 D1 拍板更新)期望值一致,無矛盾 |
| Manual smoke:空檔 | Pass | `python3 txtstat.py /tmp/empty.txt` → stdout=`lines=0 words=0 chars=0`,exit=0 |
| Manual smoke:不存在檔 | Pass | `python3 txtstat.py /tmp/nope.txt` → stderr=`error: [Errno 2] No such file or directory: '/tmp/nope.txt'`,exit=1,stdout 空(以 `2>/dev/null` 確認無 stdout 輸出) |

## Diff Notes
- `compute_stats(text)`:`lines = len(text.splitlines())`、`words = len(text.split())`、`chars = len(text)`(code point 數,含換行),符合 SPEC D2/D3 已拍板之預設語意。
- 讀檔用 `open(path, "r", encoding="utf-8")`,任何 `OSError`(檔案不存在、無權限、是目錄等)一律印 `error: <exception message>`,對應 SPEC D4「帶上 OS 例外訊息」之預設。
- 額外處理了「未帶檔名參數」(`len(sys.argv) < 2`)的情況,印 `error: missing filename argument` 並 exit 1;此為 G2 錯誤語意的自然延伸(仍只讀 `sys.argv[1]`,未新增任何 CLI 旗標或多檔支援),非新增功能。
- 執行 `py_compile` 後產生的 `__pycache__/` 已清除,未提交。

## Risks / Follow-ups
- 尚未有自動化測試(依工單設計留給 T-002),目前僅靠上述手動 smoke 驗證,合併前應待 T-002 補上 `tests/test_txtstat.py` 並跑 Unit gate 全綠。
- 錯誤訊息格式直接沿用 Python `OSError` 訊息(如 `[Errno 2] No such file or directory: '...'`),內容含完整路徑字串,對外部使用者可讀性一般,但符合 SPEC D4 拍板結果,未做額外包裝。

## Scope Deviations
- None(D1 已於 SPEC/gate 中拍板為 `words=4`,實測輸出與 gate 期望一致,無需回報衝突)。
