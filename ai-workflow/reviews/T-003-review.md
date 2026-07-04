# Review T-003

> Reviewer findings + Orchestrator 仲裁，寫在同一檔。對象：PR #5（head branch `ticket/T-003`，commit `8314eb1`）。
> Reviewer：CodeRabbit（CHILL profile，Run ID `4e874f4d…`）——**No actionable comments generated**（🎉，0 個 inline finding）。
> T-003 本身即 PR #3 仲裁 R-001（Accepted）拆出的窄修復票，故本輪 Orchestrator 額外做獨立 scope-check + gate 覆核，不只轉述 reviewer。

## Reviewer Findings

| ID | Severity | Claim | Evidence | Suggested Check |
| --- | --- | --- | --- | --- |
| CR-000 | 資訊 | CodeRabbit 對本 PR「No actionable comments were generated」，Pre-merge checks 5/5 passed，估工 Trivial（~3 min）。 | `gh api .../pulls/5/comments`：僅一則 summary 留言，內文 `No actionable comments…`；`reviews` 陣列為空。 | 覆核 diff 是否真無問題（見下方 Orchestrator 獨立覆核）。 |
| O-001 | P1（gate） | Unit gate（`python3 -m unittest discover -s tests -v`）未跑。`03-gates.md` 列 Unit 為**必須/每張工單**，且 not-run 豁免規則僅適用「未觸及 `txtstat.py` 或 `tests/`」的工單；T-003 觸及 `txtstat.py`，故 Unit not-run **不被自動豁免**。 | repo 無 `tests/` 目錄（`ls tests` → No such file or directory；`git log --all -- tests/` 空）；`03-gates.md` L11、L30-36。 | 需 `tests/` 存在後才能跑；由 T-002 建立。 |
| O-002 | 資訊 | 本 PR 新增 `ai-workflow/reports/T-003-report.md`，落在 T-003「Forbidden Files（`ai-workflow/**`）」清單內，表面像 scope 越界。 | diff 新增該報告檔；T-003 ticket L22、L30。 | 判斷報告檔是否屬強制交付物而非越界改檔。 |
| O-003 | P3 | 本 PR 是否真正修好 RK-004（非 UTF-8 檔繞過 `error:` 路徑印 traceback，違反 G2）。 | RK-004（`02-risk-register.md` L12）；SPEC G2。 | 對 `printf '\xff\xfe'` 檔實跑，看是否走 `error:` 且無 traceback。 |

### Non-Blocking Observations
- diff 極小且精準：`txtstat.py` 僅第 20 行 `except OSError` → `except (OSError, UnicodeDecodeError)`，成功路徑、輸出格式、`compute_stats` 語意全未動。符合 T-003「只改這一處」。

### Questions
- 無新 CodeRabbit 問題。唯一待答為 O-001 的 Unit gate 排序（見 Human Decisions Needed）。

### Orchestrator 獨立覆核（不盲信 reviewer / report，實跑）
於 head `8314eb1` 本機實跑（非轉述 report）：

| Gate / Case | 指令 | 結果 | 證據 |
| --- | --- | --- | --- |
| Static | `python3 -m py_compile txtstat.py` | Pass | exit 0（`STATIC_OK`） |
| Smoke | `printf 'hello world\nsecond line\n' … txtstat.py` | Pass | stdout `lines=2 words=4 chars=24`、exit 0（符合 D1 拍板值） |
| 非 UTF-8 | `printf '\xff\xfe' > bad.txt; txtstat.py bad.txt` | Pass | stderr `error: 'utf-8' codec can't decode byte 0xff…`、exit 1、stdout 空、**無 traceback** |
| 回歸-不存在檔 | `txtstat.py /tmp/does-not-exist-xyz.txt` | Pass | stderr `error: [Errno 2] No such file…`、exit 1 |
| 回歸-空檔 | `txtstat.py /tmp/empty.txt` | Pass | stdout `lines=0 words=0 chars=0`、exit 0 |
| Unit | `python3 -m unittest discover -s tests -v` | **Not Run** | 無 `tests/` 目錄；見 O-001 |

---

## Orchestrator Arbitration

| Finding | Decision | Reason | Action |
| --- | --- | --- | --- |
| CR-000 | Rejected（無 finding 可仲裁） | CodeRabbit 0 actionable；Orchestrator 獨立覆核 diff 僅一行例外併入、其餘未動，無假陽性亦無漏報可駁。 | 記錄無 finding；不開票。 |
| O-001 | Needs Human Decision | Unit gate 為 `03-gates.md` 必須項，且本工單觸及 `txtstat.py`，依 not-run 規則 **not-run 不被自動豁免**；但 `tests/` 尚未存在、且 T-003 scope 明文禁動 `tests/**`，本票**無法自行補測試**。此為 merge 排序 / gate 缺口問題，非本 diff 缺陷。 | 交 human：建議先合 **T-002**（建立 `tests/` 與案例）使 Unit gate 可跑綠，或 human 明確接受本票 Unit not-run 為環境缺口。記入下方 Human Decisions；**擋 close（gate 未綠）**。 |
| O-002 | Rejected（非 scope deviation） | `ai-workflow/reports/T-003-report.md` 是 T-003「Report Required」強制交付物、也是 pipeline 既定產物；Forbidden Files 的 `ai-workflow/**` 意在禁止對既有工作流檔的重構/擴散，不含流程強制報告。executor report 亦標「Scope Deviations: None」，與覆核一致。 | 記錄拒絕原因；不開票、不擴大 scope。 |
| O-003 | Accepted（已驗證修復） | 獨立實跑非 UTF-8 檔：走 `error: …`、exit 1、無 traceback，SPEC **G2** 於邊界輸入下完整；根因（`UnicodeDecodeError` 為 `ValueError` 子類、非 `OSError`）已由本一行修復消除。 | 更新 `02-risk-register.md`：RK-004 → **Resolved (pending merge)**；merge 後移入 Closed Risks。 |

### Fix Tickets Created
- 無。PR #5 本身即修復票 T-003，diff 正確且已驗證，無新缺陷需拆票。唯一 gate 缺口（Unit）已由既有 **T-002** 覆蓋，不重複開票。

### Human Decisions Needed
- **Unit gate 排序（O-001）**：T-003 觸及 `txtstat.py` 但無法自建 `tests/`。請 human 擇一：(a) 先 merge/跑 **T-002** 建立 `tests/` 後再讓 Unit gate 走綠、再終審 T-003；或 (b) 明確接受本票 Unit not-run 為環境缺口。
- 既有待接受風險不變：RK-001（smoke `words` 已 D1 拍板為 4，gate 已同步，待形式接受）、RK-002 / RK-003（邊界語意與錯誤訊息格式，human 驗收確認）。
- 最終 merge 由 human owner 拍板。

### Close 判斷
- CR-000 無 finding；O-002 非越界；O-003 已修復並驗證 → 三者皆不擋 close。
- **O-001 擋 close**：Unit gate 依 `03-gates.md` 必須且未綠。本 diff 無缺陷，但 Release/Merge Gate 未齊。
- 結論：**修復內容本身可接受並已獨立驗證**，但**不建議在 Unit gate 綠燈前 merge**；建議先跑/合 **T-002**，或由 human 明確接受 Unit not-run。等待 human owner 終審。
