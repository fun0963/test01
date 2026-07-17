# 專案交接文件（給接手的 AI 助手）

> 這份文件說明「**打造這個模板 + pipeline**」這件事本身的進度，不是某個下游專案的 handoff。
> 若日後把本 repo 當純模板複製使用，可刪掉這個檔。
> 最後更新：2026-07-04（第二輪：靜態修理 workflow + 補蒸餾 workflow + 環境搬家處理）。

## 0. 一句話總結

我們做了一套**多模型 AI 協作開發模板**（`ai-workflow/`），並在 GitHub 上接了一條**半自動 pipeline**（`.github/workflows/`），讓 Orchestrator / Executor / Reviewer 三角色能經由手動觸發的 workflow 分階段執行，人類在 merge 前終審。**2026-07-04 已在 test01 沙盒用最小專案完整跑通一輪**（Orchestrator → plan PR → Executor → CodeRabbit + scope-check → 仲裁 → 終審 merge → Distill + tag），期間發現並修復一個紅燈（arbitration 白名單過窄）。

## 1. 兩個 repo 的角色

| Repo | 用途 | 狀態 |
|---|---|---|
| `fun0963/lcp10_workflow` | **母版 / template repo**（`is_template=true`）。也是我們的工作 repo。 | 有 `protect-main` ruleset；**無** secret |
| `fun0963/test01` | **測試沙盒**（2026-07-03 用「Use this template」重建，歷史是squash 過的 `Initial commit`，與 lcp10 無共同祖先——同步靠 cherry-pick，不能直接 push 同一份歷史） | 五條 workflow；有 `protect-main` ruleset（2026-07-04 由 API 照 lcp10 複製，id 18488543）；**無** secret |

本機工作目錄已搬家：現在是 `D:/AI_work_claude/lcp10_workflow/`（舊的 `C:/EE/Local_ai_claude/...` 已不存在）。
其下 `test01/` 子資料夾是本機複本，已加進 `.gitignore`，**不要** commit 進 lcp10。
（修理紀錄：`test01/` 的 origin 原本誤指向 lcp10_workflow，已改回 `fun0963/test01`。）

## 2. 架構（設計原則：plumbing 不用 LLM）

五角色：Human Owner（終審）/ Orchestrator（最強模型，診斷·拆單·仲裁）/ Executor（coding agent，窄工單）/ Reviewer（CodeRabbit，異質、免費、不吃 Claude 額度）/ Objective Gates（測試·smoke·scope-check）。

整條 pipeline 只有 **3 個點呼叫 Claude**，其餘全是純 script / GitHub 原生機制（0 token）：

| Workflow | 觸發 | 模型 | 做什麼 |
|---|---|---|---|
| `.github/workflows/ai-orchestrator.yml` | 手動 dispatch | **opus** | 讀 `ai-workflow/project-brief.md` → 產 `00-spec`/`01-plan`/`tickets/` → 推 `plan/*` branch |
| `.github/workflows/ai-executor.yml` | 手動 dispatch（輸入工單如 `T-001`） | **sonnet** | 只做該工單 → 推 `ticket/T-XXX` branch + `reports/` 報告 |
| `.github/workflows/ai-arbitration.yml` | 手動 dispatch（輸入 PR 編號） | **opus** | 讀 CodeRabbit findings → 仲裁 → 寫 `reviews/` + PR 留言 |
| `.github/workflows/ai-distill.yml` | 手動 dispatch（輸入剛 merge 的工單） | **haiku** | 打 `close/T-XXX` tag（純 script）→ 蒸餾 memory/handoff/01-plan → 推 `chore/distill-*` branch |
| `.github/workflows/scope-check.yml` | PR 自動 | **無（純 bash）** | diff 對照 **main 上的**工單 Allowed Files，超界則 fail（required check） |

角色開場、完整範例、每輪循環見 [`ai-workflow/WORKFLOW.md`](ai-workflow/WORKFLOW.md)；按鈕操作見 [`.github/README.md`](.github/README.md)。

## 3. 目前進度

**已完成 ✅**
- `ai-workflow/` 自足母版：指南、USAGE、WORKFLOW、prompts/（orchestrator·executor·reviewer·arbitration）、00-spec / 01-plan / 02-risk-register / 03-gates、memory / handoff / MINIMAL、tickets·reports·reviews·decisions 模板。
- 四條 workflow + `.github/README.md`，已 commit（`ec2f88f`）並 push 到 lcp10 與 test01。
- lcp10 設為 template repo；lcp10 建了 `protect-main` ruleset（必須走 PR、`scope-check` 必須綠、禁 force-push/刪除，admin 可 bypass）。
- **第二輪靜態修理（2026-07-04）**：
  - 三條 Claude workflow 補 `github_token: GITHUB_TOKEN`（否則沒裝 Claude GitHub App 時 action 啟動即掛）＋ 前置 git 身分 step（避免 CI 裡 `git commit` 撞 identity 錯誤）。
  - `ai-executor.yml` 加工單編號格式驗證（fail fast，防 `t-001` 這種輸入讓 scope-check 靜默略過）。
  - `scope-check.yml` 修三處：空清單檢查順序 bug（原本永遠不觸發）、`tr -d '\`'` 誤刪反斜線、awk 區塊結束條件；並把 pipeline 產物加入白名單（`reviews/<T>-review.md`、`02-risk-register.md`、**新增**的修復工單），否則仲裁 push 後 scope-check 必紅。
  - **補建 `ai-distill.yml`**（原待辦 5）：tag 用純 script，蒸餾用 haiku，產出推 `chore/distill-*` branch 由人開 PR。
  - `ai-arbitration.yml` 加 run summary 提醒：GITHUB_TOKEN push 不重新觸發 scope-check，需 Close/Reopen PR。
  - 本機：`test01/` 的 origin 從誤指 lcp10 改回 `fun0963/test01`；加 `.gitignore`；重裝 `gh` 2.96.0（環境搬家後遺失）。
  - 已推送：lcp10 `c82f113`（admin bypass 直推 main）、test01 `19d5938`（cherry-pick 到重建後的歷史上）。
  - test01 建立 `protect-main` ruleset（照 lcp10 設定由 API 複製）→ 原待辦「test01 沒有 ruleset」已清。
- **第三輪（2026-07-04，同日稍晚）**：
  - 使用者把 gh 登入換成 fine-grained PAT 並補齊權限（過程中誤刪過 Contents，已修）。目前 PAT 有：Contents / Workflows / Secrets / Administration / Actions / Pull requests（RW）。同一顆 PAT 同時是 GCM 的 git 憑證。
  - **test01 的 `CLAUDE_CODE_OAUTH_TOKEN` secret 已設好**（原待辦 1 的 test01 部分完成）。
  - **金絲雀 PR（test01 #1）驗證通過後關閉**：scope-check 首次在 Actions 實跑 → **綠**（非 ticket branch 略過路徑正確）；**CodeRabbit 有實際 review** → 涵蓋 test01 確認（原待辦 2 完成）。
  - 文件補「開案:人類與 AI 的分工」checklist（`ai-workflow/WORKFLOW.md` §1，USAGE 與 .github/README 有指路）。

- **第四輪（2026-07-04，冒煙測試完整跑通 ✅）**：在 test01 用最小專案（txtstat.py CLI）跑完整輪：
  - **Orchestrator（opus，約 4 分）**：拆出 T-001/T-002、產 spec/plan；還抓到 brief 撰寫者在 gate 裡的算術錯誤（words=3 應為 4），正確開 Open Decision 不硬湊 → plan PR #2 拍板 D1–D4 後 merge。
  - **Executor（sonnet，約 2.5 分）**：T-001 實作乾淨、diff 全在 Allowed Files 內、報告附真實證據與正當的 Unit gate Not-Run 理由 → PR #3。
  - **CodeRabbit + scope-check**：ticket branch 真白名單路徑綠燈。
  - **Arbitration（opus）**：🔴 首跑爆 `max-turns`（窄白名單致 16 次工具拒絕）→ 放寬 Bash + max-turns 40 後重跑 ✅。仲裁品質好：R-001（UnicodeDecodeError 未接）Accepted 並開窄修復票 T-003、R-002（路徑遍歷）正確判假陽性 Rejected。
  - **仲裁後 required check 卡 Expected** → 照文件 Close/Reopen 重觸發，scope-check 對仲裁產物（reviews/風險登記簿/新增 T-003）綠燈——第二輪修的白名單在實戰中驗證。
  - **終審 merge PR #3 → Distill（haiku，約 1.5 分）**：tag `close/T-001` 打好、蒸餾內容事實正確 → distill PR merge。
  - 全程 0 手動瀏覽器操作（除 secret/CodeRabbit 事前設定），每階段由 API 觸發。

- **第五輪（2026-07-05，T-003 + T-002 兩輪跑完，沙盒專案收官 ✅）**：
  - **T-003 輪**：Executor 一行修復 → PR #5 → CodeRabbit 0 finding → 仲裁**獨立實跑**非 UTF-8 案例驗證修復正確，但依 not-run 規則開 **O-001 擋 close**（Unit gate 必須項而 `tests/` 不存在、本票又禁動 tests/）→ 交 human 擇一。
  - **T-002 輪**（採仲裁建議方案 a，先補測試）：Executor 建 `tests/test_txtstat.py`（3 案例）→ PR #6 → CodeRabbit 2 個 trivial nit → 仲裁 R-001 排版 nit Rejected、R-002（空檔未斷言 stderr）Accepted 開追蹤票 **T-004**、branch 實測 Unit gate 綠、不擋 close → merge → Distill（`close/T-002`）。
  - **回頭關 T-003**：本機把 main 併入 `ticket/T-003`、實跑四項 gate 全綠（Unit 3 tests OK、Static、Smoke、非 UTF-8 邊界無 traceback）→ PR #5 留言記錄 O-001 決策與證據 → merge → Distill（`close/T-003`）。
  - 沙盒最終狀態：`main` + `close/T-001`~`close/T-003` 三個 tag，無殘留 branch；僅剩 T-004（trivial 追蹤票）未跑。
  - **實測差異紀錄**:本機 PAT push 到 PR branch 會自動觸發 scope-check(pull_request synchronize);CI 內 GITHUB_TOKEN push 不會,需 Close/Reopen。
  - 環境更新:這台機器 python3 = 3.13.9 可用(舊 handoff「python 被 gtkwave 綁架」問題不存在於新環境)。

- **第六輪（2026-07-17，T-004 收官 + 白名單收緊實彈驗證 ✅）**：
  - **先收緊再驗證**：Executor / Arbitration 的 Bash 從全開改為「通用底座（git/gh + coreutils）+ 本專案 gate 指令段（python3/printf）」，排除網路工具與套件安裝；Orchestrator / Distill 維持 `Bash(git:*)`（4 run 0 拒絕實證夠用）。YAML 註解標明開新案時只換 gate 段。
  - **T-004 輪當驗證彈**：Executor（20 turns）與 Arbitration（27 turns）各僅 2 次拒絕、自行調整完成，額度正常（$0.35 / $0.93）——收緊可用。若日後某 run 拒絕數飆高，從該 run log 對症補名單。
  - T-004 一行斷言 merge、`close/T-004` tag、蒸餾完成。仲裁這輪還把報告的 MD058 排版 in-place 修掉（Accepted 小項直接修，不另開票）。
  - 沙盒最終狀態：`main` + `close/T-001`~`close/T-004` 四個 tag，**所有工單清零**。

**待辦 / 阻塞 ⛔**
1. **[待辦] 訂閱側額度對照**：在互動 session 看 `/usage`，把四輪（≈$8.5 等值）佔週上限的百分比對照 §3.5 換算，外推 Pro 夠不夠。
2. **[待辦] lcp10 的 secret 未設**：目前只設了 test01。要在母版 lcp10 直接跑 workflow 時才需要：`gh secret set CLAUDE_CODE_OAUTH_TOKEN -R fun0963/lcp10_workflow`。
3. **[小事] PAT 效期**：fine-grained PAT 有到期日，到期時 git push / gh / API 全會一起失效——症狀是 403，別誤判成 repo 權限問題。

## 3.5 實測額度數據（2026-07-04~05，test01 三張工單，來源：run log 的 `total_cost_usd`）

> USD 為 **API 等值**；訂閱制實際扣的是額度（5hr 窗 + 週上限），數字當相對比例用，對照 `/usage` 換算。

| Run | 模型 | turns | Claude 執行時間 | API 等值 |
|---|---|---|---|---|
| Orchestrator 開案拆單 | opus | 18 | 3.2 分 | $0.88 |
| Executor T-001 | sonnet | 20 | 1.7 分 | $0.43 |
| **Arbitration T-001（失敗，事故）** | opus | 31 | 8.0 分 | **$2.35** |
| Arbitration T-001（重跑） | opus | 22 | 3.4 分 | $0.93 |
| Distill T-001 | haiku | 19 | 0.8 分 | $0.07 |
| Executor T-003 | sonnet | 22 | 1.2 分 | $0.40 |
| Arbitration T-003 | opus | 20 | 3.3 分 | $0.81 |
| Executor T-002 | sonnet | 22 | 1.5 分 | $0.35 |
| Arbitration T-002 | opus | 19 | 2.8 分 | $0.77 |
| Distill T-002 | haiku | 14 | 0.7 分 | $0.08 |
| Distill T-003 | haiku | 16 | 0.7 分 | $0.08 |
| Executor T-004（收緊白名單後） | sonnet | 20 | 1.0 分 | $0.35 |
| Arbitration T-004（收緊白名單後） | opus | 27 | 3.2 分 | $0.93 |
| Distill T-004 | haiku | 14 | 1.0 分 | $0.09 |
| **總計（14 runs / 4 張工單）** | | | ≈32 分 | **≈$8.53** |

**結論**：
- **穩態一輪（Executor+Arbitration+Distill）≈ $1.2–1.3**；開案拆單一次性 $0.88。
- **仲裁（opus）是成本大頭**，佔穩態一輪的 60%+；Distill（haiku）近乎免費（$0.07–0.08）。
- **事故很貴**：permission-denial 空轉那次 $2.35，是正常仲裁的 2.5–3 倍——`--max-turns` 護欄擋住了更糟的，但白名單設錯的代價真實存在。
- 粗估：**每週跑 10 輪工單 ≈ $13 等值 + 開案**；對照 `/usage` 的窗口/週上限百分比即可判斷 Pro 夠不夠。
- **收緊白名單後（T-004 輪）成本不變**（$1.37/輪，與全開時 $1.2–1.3 同級），每 run 約 2 次拒絕屬可吸收摩擦。

## 4. 建議的第一次冒煙測試順序（在 test01 上）

1. ~~設好 secret + 確認 CodeRabbit~~ ✅ 已完成（2026-07-04，金絲雀 PR 驗證過）。
2. 在 test01 填一個很小的 `ai-workflow/project-brief.md`（可直接推 main）。
3. Actions → **AI Orchestrator** → Run workflow。看它產出的 `plan/*` branch 品質；**跑前後用 `claude` 的 `/usage` 記錄額度消耗**（這是第一筆真實用量數據）。
4. 對 `plan/*` 開 PR、merge（把工單併進 main，scope-check 才讀得到）。
5. Actions → **AI Executor** → 輸入某張工單編號 → 產 `ticket/T-XXX`。
6. 開 PR → 觀察 CodeRabbit 與 scope-check 是否如預期。
7. Actions → **AI Arbitration** → 輸入 PR 編號 → 看仲裁留言 → 人工 merge。
8. 每一步紅燈就收集：workflow 名、紅色 step 名、最後 10–20 行 log，回報給協作的 AI 修 YAML。

## 5. 已知風險 / 注意事項

- **Executor 與 Arbitration 的 Bash 權限目前全開**（`--allowedTools "...,Bash"`）。Executor 因為要跑任意 gate 指令；Arbitration 原本用窄白名單（`git`/`gh pr`/`gh api`），首次實跑（2026-07-04，test01 PR #3）因複合指令與管線被拒 16 次、31 turns 爆掉 `--max-turns 30` 而失敗，故放寬為全開並把 max-turns 提到 40。跑順後兩者一起收緊。
- **Arbitration 依賴「CodeRabbit 已經 review 過該 PR」**：若 CodeRabbit 還沒貼 findings 就觸發仲裁，Claude 會拿到空的 review。順序上要等 CodeRabbit 完成再觸發。
- **仲裁 push 後 required check 會停在 Expected**：GITHUB_TOKEN 的 push 不觸發 pull_request workflow。解法＝PR 頁面 Close 再 Reopen（或 admin bypass merge）。已寫進 `.github/README.md` 已知眉角。
- **GITHUB_TOKEN 遞迴限制**：目前是半自動（人手動觸發每階段），所以還沒踩到「bot 動作不觸發下游 workflow」的坑。若之後要**全自動串接**，需改用 GitHub App token 或 PAT，並補回防迴圈 guard（`if github.actor != bot`、label 狀態機、queue 模式的 concurrency）。研究結論詳見對話歷史。
- **03-gates.md 是佔位**：`<...>` 要在每個真實專案開案時由 Orchestrator + Human 換成真實 lint/test/smoke 指令。
- **額度**：訂閱制按「5 小時窗 + 週上限（小時）」計，非 token；CI 與互動共用。跑 2–3 張工單後用 `/usage` 外推週消耗再決定 Pro 夠不夠、要不要升 Max 5x 或開 usage credits。

## 6. 尚未採用但研究過的選項

- **Gemini 免費 API 小工具**：刻意延後。免費 key 仍可用且 CI 合規，但 Pro 模型已移出免費層、配額被砍且不公布、免費層會拿去訓練。定位只適合「前處理/摘要」錦上添花，先量測 Claude 額度真的緊再加。加時：模型名做成可配置、用 Flash 家族、**同專案別開 billing**（一開免費層永久消失）。
- **全自動串接**：研究過 label 狀態機 + GitHub App token + push ruleset 路徑，因選「半自動起步」而暫緩。

## 7. 環境（2026-07-04 搬家後）

- 工作目錄：`D:\AI_work_claude\lcp10_workflow\`（舊 `C:\EE\...` 環境已不存在，`C:\iverilog` 也沒了——python 綁架問題應已消失，未驗證）。
- OS：Windows 11 / PowerShell（主）+ Git Bash。
- `gh` 2.96.0 已重裝於 `C:\Program Files\GitHub CLI\`（可能要重開 shell 才進 PATH），**尚未登入**（要用 gh CLI 才需要 `gh auth login`）。
- git 的 GitHub 憑證有效（GCM），push / API 都通——不要被「gh 未登入」誤導。
- `gh secret set` 若報 "not a git repository"，是因為不在 git 資料夾內跑——加 `-R fun0963/test01` 或用網頁設。
