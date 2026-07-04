# Review T-001

> Reviewer findings + Orchestrator 仲裁，寫在同一檔。對象：PR #3（head branch `ticket/T-001`，commit `823d1e8`）。
> Reviewer：CodeRabbit（1 個 actionable inline comment + ast-grep 工具告警）。

## Reviewer Findings

| ID | Severity | Claim | Evidence | Suggested Check |
| --- | --- | --- | --- | --- |
| R-001 | P3（CodeRabbit 標 🟡 Minor） | `txtstat.py` 讀檔只 catch `OSError`，惡意/損壞的非 UTF-8 檔會在 `f.read()` 拋 `UnicodeDecodeError`，繞過 `error: <原因>` 路徑並印出 traceback。 | CodeRabbit 於 PR inline（discussion r3523008226）附腳本證明 `isinstance(e, OSError)` 為 False；Orchestrator 覆核：`UnicodeDecodeError` 為 `ValueError` 子類、非 `OSError`；對 `\xff\xfe...` 檔實跑 head 版程式印 traceback（exit=1）。 | 對含非 UTF-8 位元組的檔跑 `python3 txtstat.py bad.txt`，觀察是否走 `error:` 格式。 |
| R-002 | 資訊（ast-grep 工具告警，非 actionable） | `open(path, ...)` 的 `path` 來自變數/請求，恐有 path traversal（CWE-22），建議 validate/normalize。 | CodeRabbit `🧰 Tools → ast-grep` 附註於同一 inline，規則 `open-filename-from-request`。 | 檢視 `path` 來源是否跨越信任邊界。 |

### Non-Blocking Observations
- 錯誤訊息直接沿用 Python `OSError` 原文（含完整路徑），可讀性一般，但符合 SPEC D4 拍板（帶 OS 例外訊息）。已由 RK-003 追蹤，非本輪 finding。

### Questions
- 無。CodeRabbit 未提出需 human 判斷的問題。

---

## Orchestrator Arbitration

| Finding | Decision | Reason | Action |
| --- | --- | --- | --- |
| R-001 | Accepted | 真問題、有 evidence（已覆核）。`UnicodeDecodeError` 非 `OSError` 子類，惡意/損壞 UTF-8 檔會印 traceback 而非 `error: <原因>`，違反 SPEC **G2**「不可讀時印 `error:` 到 stderr」的訊息格式；屬 T-001 錯誤處理 scope（「不可讀」）內。修復僅一行（把 `UnicodeDecodeError` 併入 except tuple），低風險。 | 開窄修復工單 **T-003**；同步記 **RK-004** 到 risk register。非 P0/P1，未擋既定 gate（smoke 用合法 UTF-8），但建議 merge 前先跑 T-003 使 G2 完整。 |
| R-002 | Rejected | 假陽性。`path` 來自 `sys.argv[1]`，是本機 CLI 使用者自己提供的引數，**無信任邊界**、無網路/多租戶輸入；「讀使用者指定路徑的檔」正是本工具的目的（SPEC Non-Goals 已定調純本機 CLI、無外部系統）。CWE-22 不適用。 | 記錄拒絕原因，不開票、不擴大 scope。 |

### Fix Tickets Created
- T-003：txtstat.py 讀檔 except 併入 `UnicodeDecodeError`，使非 UTF-8 檔走 `error: <原因>` 路徑（窄修復，一行）。

### Human Decisions Needed
- 無新增。既有 RK-001（smoke `words` 已於 D1 拍板為 4，gate 已同步）、RK-002/RK-003（邊界語意與錯誤訊息格式，human 驗收確認）仍待 human owner 於終審時一併接受。

### Close 判斷
- R-001 為真但 P3、且不在 SPEC 列舉的 acceptance/gate（smoke/一般/空/不存在檔皆合法 UTF-8）之內，**不硬性阻擋 close**；惟已開 T-003，建議 merge 前先跑以求 G2 完整。
- R-002 假陽性，不阻擋。
- 其餘 gate（Static / Smoke）依 report 為綠；Unit gate 依設計留待 T-002。最終 merge 由 human owner 拍板。
