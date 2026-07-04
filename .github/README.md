# GitHub 半自動 pipeline 使用說明

角色與流程的完整說明見 [`../ai-workflow/WORKFLOW.md`](../ai-workflow/WORKFLOW.md)。
這裡只講「按鈕怎麼按」。設計原則:**plumbing 不用 LLM**(scope-check、branch、tag 全是純 script),
只有四個階段呼叫 Claude,且各自固定模型等級(opus / sonnet / opus / haiku)。

## 一次性設定(新 repo 才需要)

1. 本機跑 `claude setup-token`(瀏覽器 OAuth,用你的訂閱,效期一年)。
2. 把 token 存進 repo secret:`gh secret set CLAUDE_CODE_OAUTH_TOKEN`(貼上 token)。
3. 確認 CodeRabbit GitHub App 已涵蓋本 repo(Reviewer 階段靠它,免費、不吃 Claude 額度)。

> 不需要安裝 Claude GitHub App:workflow 已明確傳 `github_token`(GITHUB_TOKEN),
> 不走 App 的 OIDC 交換。

完整的開案「人類 vs AI」分工 checklist(含金絲雀 PR 驗證、誰能代辦什麼)見
[`../ai-workflow/WORKFLOW.md`](../ai-workflow/WORKFLOW.md) §1。

## 每輪循環(半自動:每階段你按一次)

| 步驟 | 動作 | 誰跑 / 模型 |
|---|---|---|
| ① 開案/拆工單 | Actions → **AI Orchestrator** → Run workflow | Claude opus |
| ② 審計畫 | 用 run summary 的連結對 `plan/*` branch 開 PR,自己看過後 merge | 你 |
| ③ 執行工單 | Actions → **AI Executor** → 輸入 `T-001` | Claude sonnet |
| ④ 開 PR | 用 run summary 的連結對 `ticket/T-001` 開 PR | 你(一鍵) |
| ⑤ Review | CodeRabbit 自動審;**scope-check** 自動驗 diff 沒超出工單範圍 | 自動(0 Claude 額度) |
| ⑥ 仲裁 | Actions → **AI Arbitration** → 輸入 PR 編號 | Claude opus |
| ⑦ 終審 | 看仲裁留言,接受風險就 merge(這一下就是 human gate) | 你 |
| ⑧ 蒸餾 | Actions → **AI Distill** → 輸入 `T-001`:打 `close/T-001` tag(純 script)+ 蒸餾 memory/handoff/01-plan → 對 `chore/distill-*` 開 PR、看過 merge | Claude haiku |

## 額度提醒

- CI 用量和你的互動用量**共用同一份訂閱額度**;跑完前 2–3 張工單用 `/usage` 看消耗再外推。
- 每條 workflow 已設 `--max-turns` 與 `timeout-minutes` 防單次爆量;`concurrency: ai-pipeline` 確保一次只跑一個階段。

## 防護層

- `scope-check`(required check):diff 對照**main 上的**工單 Allowed Files,executor 改不了自己的邊界。
  pipeline 自身產物自動放行:`reports/<T>-report.md`、`reviews/<T>-review.md`、`02-risk-register.md`、
  **新增**的修復工單(修改既有工單仍會擋)。
- main ruleset:必須走 PR、scope-check 綠、禁 force-push。
- claude-code-action 內建:不能改 `.github/workflows/`、不能 force-push、只能推自己的 branch。

## 已知眉角

- **仲裁 push 後 scope-check 不會自動重跑**:GITHUB_TOKEN 的 push 不觸發下游 workflow,
  required check 會停在 Expected。到 PR 頁面 **Close 再 Reopen** 一次即可重新觸發(run summary 也會提醒)。
- **PR 裡若出現「新增的工單檔」**(仲裁拆的修復工單),終審時多看一眼它的 Allowed Files 合不合理——
  它 merge 後就是下一輪 scope 的邊界。
