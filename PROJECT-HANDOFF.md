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

**待辦 / 阻塞 ⛔**
1. **[待辦] test01 沙盒還有兩張票可跑**：T-002（補 unittest）、T-003（except 併入 UnicodeDecodeError，一行修復）。跑法照每輪循環（Executor → PR → 仲裁 → merge → Distill）。跑完就是「2–3 張工單」的額度外推資料點。
2. **[待辦] 用 `/usage` 記錄本輪額度消耗**：本輪已知 arbitration 失敗那次燒掉約 $2.35 等值 opus 用量（log 有 total_cost_usd），其餘各 run 未逐一記錄——在互動 session 看 `/usage` 外推週消耗，決定 Pro 夠不夠。
3. **[待辦] 收緊 Executor / Arbitration 的 Bash 白名單**：現在兩者全開。等 T-002/T-003 也跑順、確認常用指令集合後再收。
4. **[待辦] lcp10 的 secret 未設**：目前只設了 test01。要在母版 lcp10 直接跑 workflow 時才需要：`gh secret set CLAUDE_CODE_OAUTH_TOKEN -R fun0963/lcp10_workflow`。
5. **[小事] PAT 效期**：fine-grained PAT 有到期日，到期時 git push / gh / API 全會一起失效——症狀是 403，別誤判成 repo 權限問題（本輪已踩過一次類似坑）。

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
