# 最小可用版本流程

> 專案很小、不需要整個 `ai-workflow/` 資料夾時，至少保留這四件事。
> 複製這一段到 issue、PR 描述或一個單檔即可。

```md
## Goal
<這次只做什麼>

## Scope
Allowed:
- <允許>

Forbidden:
- <禁止>

## Done
- [ ] <測試或 smoke>
- [ ] <產品行為>
- [ ] <風險接受>

## Report
- changed files:
- verification:
- remaining risks:
```

## 什麼時候升級到完整流程

出現以下任一情況，就從 MINIMAL 升級到完整 `ai-workflow/`：

- 需要跨檔案 / 跨服務改動。
- 需要多輪執行、需要交接。
- 需要 reviewer 找風險。
- 涉及產品行為、資料或安全風險，需要 human owner 終審。
