# 使用說明（簡潔版）

完整原理見 [`AI_COLLAB_DEVELOPMENT_GUIDE.md`](AI_COLLAB_DEVELOPMENT_GUIDE.md),操作手冊見 [`WORKFLOW.md`](WORKFLOW.md)。
整份 `ai-workflow/` 就是可複製的自足模板。這份是「怎麼跑」的速查。

## 一、五個角色

| 角色 | 誰 | 只做 | 不做 |
| --- | --- | --- | --- |
| Human Owner | 你 | 產品驗收、風險接受、優先級 | 逐行盯 code |
| Orchestrator | 最強推理模型 | 拆工單、定義 done、仲裁、讀 diff | 大量寫 code |
| Executor | coding agent | 改 allowed files、跑驗證、回報 | 自己定義完成 |
| Reviewer | 另一個異質模型 | 找風險與盲點 | 拍板、指揮修復 |
| Objective Gates | 測試 / smoke | 提供客觀證據 | 取代產品判斷 |

## 二、開案三步

```bash
# 1. 複製整份母版到新專案根目錄
cp -r /path/to/ai-workflow ./ai-workflow
```

2. 填 `ai-workflow/project-brief.md`（背景 / 目標 / 非目標 / 限制 / 驗收），並把 `03-gates.md` 換成本專案真實 gate 指令。
3. 把 brief 貼給 Orchestrator，用 `prompts/orchestrator.md` 的 Prompt A：先診斷、拆工單，產出 `00-spec.md` 與 `01-plan.md`。**先不寫 code。**

## 三、每張工單的循環

```text
Orchestrator 拆窄工單 (tickets/)
  → Executor 執行 + 跑驗證 + 回報 (reports/)
  → Reviewer 找風險 (reviews/)
  → Orchestrator 仲裁 findings (reviews/ 同檔)
  → 必要時開修復工單
  → 測試 / smoke 通過
  → Human Owner 驗收
  → 更新 memory.md / handoff.md，close
```

每個角色貼對應的 prompt：
`prompts/executor.md` → `prompts/reviewer.md` → `prompts/orchestrator.md`（Prompt B 仲裁）。

## 四、任務分流

| 任務 | 怎麼跑 |
| --- | --- |
| 小而明確的單點修改 | 直接給 Executor，用 `MINIMAL.md` |
| 跨檔案 / 需驗收 / 需部署 | 走完整 Orchestrator 流程 |
| 需找風險、盲點、合約問題 | 加 Reviewer |
| 涉及產品、商業、資料、安全 | Human Owner 必須終審 |

## 五、close 前必須成立

- [ ] 工單 acceptance criteria 已滿足
- [ ] required verification 已跑（或原因被接受）
- [ ] diff 已被 Orchestrator 看過
- [ ] reviewer findings 已仲裁
- [ ] 無未解 P0/P1
- [ ] 剩餘風險已記錄並被接受
- [ ] Human Owner 接受產品行為

## 六、鐵則（最容易踩雷的地方）

1. **不要單一模型硬扛** — 分開 orchestrator / executor / reviewer。
2. **done 外部化** — 寫在 SPEC / 工單，不讓 executor 自己說「完成」。
3. **finding 要先仲裁** — reviewer 不能直接觸發修復。
4. **工單要窄** — 一張只做一件事，列 allowed / forbidden files。
5. **完成要有證據** — 不接受「應該可以」「看起來沒問題」。
6. **每輪更新 memory / handoff** — 長任務不靠模型記憶。
7. **人類終審** — 產品方向與最終責任在你手上。
