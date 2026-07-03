# lcp10_workflow — AI 協作開發模板

多模型分工的 AI 協作開發架構:**Orchestrator**(最強模型,判斷/拆單/仲裁)、
**Executor**(coding agent,窄工單執行)、**Reviewer**(異質模型,只找風險)、
**Objective Gates**(測試/smoke/scope-check,客觀證據)、**Human Owner**(終審)。

| 想看什麼 | 去哪裡 |
|---|---|
| 完整原理與角色分工 | [`ai-workflow/AI_COLLAB_DEVELOPMENT_GUIDE.md`](ai-workflow/AI_COLLAB_DEVELOPMENT_GUIDE.md) |
| 速查 | [`ai-workflow/USAGE.md`](ai-workflow/USAGE.md) |
| 操作手冊(角色開場 + 完整範例) | [`ai-workflow/WORKFLOW.md`](ai-workflow/WORKFLOW.md) |
| GitHub 半自動 pipeline 怎麼按 | [`.github/README.md`](.github/README.md) |

## 開新專案

`ai-workflow/` 是自足的空白母版:

```bash
cp -r ai-workflow /path/to/新專案/ai-workflow
cp -r .github    /path/to/新專案/.github     # 要用 GitHub 半自動 pipeline 才需要
```

之後照 [`ai-workflow/WORKFLOW.md`](ai-workflow/WORKFLOW.md):填 `project-brief.md` →
填 `03-gates.md` 的真實 gate 指令 → Orchestrator 診斷拆單 → 每張工單跑
executor → review → 仲裁 → 人工終審的循環。

> 本 repo 同時是母版:請在**副本**裡填真實專案內容,保持母版空白。
