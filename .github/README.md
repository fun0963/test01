# GitHub 半自動 pipeline 使用說明

角色與流程的完整說明見 [`../ai-workflow/WORKFLOW.md`](../ai-workflow/WORKFLOW.md)。
這裡只講「按鈕怎麼按」。設計原則:**plumbing 不用 LLM**(scope-check、branch、tag 全是純 script),
只有三個階段呼叫 Claude,且各自固定模型等級。

## 一次性設定(新 repo 才需要)

1. 本機跑 `claude setup-token`(瀏覽器 OAuth,用你的訂閱,效期一年)。
2. 把 token 存進 repo secret:`gh secret set CLAUDE_CODE_OAUTH_TOKEN`(貼上 token)。
3. 確認 CodeRabbit GitHub App 已涵蓋本 repo(Reviewer 階段靠它,免費、不吃 Claude 額度)。

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
| ⑧ 蒸餾 | merge 後更新 memory/handoff(暫時在本機互動 session 做;之後補 haiku workflow) | 你/Claude haiku |

## 額度提醒

- CI 用量和你的互動用量**共用同一份訂閱額度**;跑完前 2–3 張工單用 `/usage` 看消耗再外推。
- 每條 workflow 已設 `--max-turns` 與 `timeout-minutes` 防單次爆量;`concurrency: ai-pipeline` 確保一次只跑一個階段。

## 防護層

- `scope-check`(required check):diff 對照**main 上的**工單 Allowed Files,executor 改不了自己的邊界。
- main ruleset:必須走 PR、scope-check 綠、禁 force-push。
- claude-code-action 內建:不能改 `.github/workflows/`、不能 force-push、只能推自己的 branch。
