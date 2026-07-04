# Ticket T-003: txtstat.py 讀檔併入 UnicodeDecodeError 處理

> 好工單只做一件事、有明確禁區、有客觀驗收。
> 來源：PR #3 仲裁（`reviews/T-001-review.md` R-001 Accepted）。

## Objective
讓 `txtstat.py` 讀到**非 UTF-8 / 損壞編碼**的檔案時，走既有 `error: <原因>` 路徑（stderr、exit 1、stdout 無輸出），而非拋 `UnicodeDecodeError` 印出 traceback。**只改這一處例外處理，不做其他事。**

## Context
- 相關背景：CodeRabbit 於 PR #3 提出、Orchestrator 仲裁 Accepted 的真問題。
- 根因：`UnicodeDecodeError` 是 `ValueError` 子類、**非** `OSError`，故現行 `except OSError` 捕捉不到；`f.read()` 對非 UTF-8 位元組會拋出並繞過錯誤路徑。
- 相關 SPEC 條目：**G2**（不可讀時印 `error:` 到 stderr、exit 1、stdout 無輸出）；D4（錯誤訊息帶 OS/例外訊息）。
- 前置工單：T-001（已在 `ticket/T-001` / PR #3）。

## Scope
### Allowed
- 修改 `txtstat.py` 讀檔區塊的 `except`，把 `UnicodeDecodeError` 併入（例如 `except (OSError, UnicodeDecodeError) as e:`），維持既有 `print(f"error: {e}", file=sys.stderr)` 與 `sys.exit(1)` 行為不變。

### Not Allowed
- 不改變成功路徑、輸出格式、`compute_stats` 語意。
- 不加 CLI 旗標、不支援多檔、不讀 stdin、不引入第三方套件。
- 不動 `tests/**`、`ai-workflow/**`、`.github/**` 或其他既有檔案。
- 不做未要求的重構或格式化擴散。

## Files
### Allowed Files
- `txtstat.py`

### Forbidden Files
- `tests/**`、`ai-workflow/**`、`.github/**`
- `README.md`、`PROJECT-HANDOFF.md`、`.gitignore`
- 其他任何既有檔案

## Acceptance Criteria
- [ ] 對含非 UTF-8 位元組的檔（如 `printf '\xff\xfe' > bad.txt`）：stderr 印 `error: ...`、exit code 1、stdout 空，**無 traceback**。
- [ ] 既有行為不回歸：一般檔仍印 `lines=N words=N chars=N` exit 0；不存在檔仍印 `error:` exit 1；空檔仍 `lines=0 words=0 chars=0`。

## Required Verification
> gate 指令權威來源是 `../03-gates.md`。
- [ ] `03-gates.md`：Static —— `python3 -m py_compile txtstat.py`
- [ ] `03-gates.md`：Smoke —— `printf 'hello world\nsecond line\n' > /tmp/smoke.txt && python3 txtstat.py /tmp/smoke.txt`（預期 `lines=2 words=4 chars=24`）
- [ ] manual smoke（本工單特有）：非 UTF-8 檔一次，貼 exit code 與 stdout/stderr（應為 `error:`、無 traceback）。

## Report Required
1. 你改了什麼。
2. 實際修改的檔案。
3. Static / Smoke / 非 UTF-8 manual smoke 結果（含實際 stdout/stderr/exit code）。
4. 未完成事項。
5. 剩餘風險。
6. 是否有任何 scope deviation。
