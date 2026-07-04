# Project Brief

## 背景
- 這是 pipeline 冒煙測試用的最小真實專案：驗證 Orchestrator → Executor → Reviewer → 仲裁 → 蒸餾整條流程能跑通。
- 專案本身要解決的問題：提供一個零相依的文字檔統計小工具。
- 受影響對象：只有 pipeline 測試者。

## 目標
- 新增單檔 CLI `txtstat.py`（repo 根目錄）：`python3 txtstat.py <file>` 輸出該檔的行數、單字數、字元數，格式固定為 `lines=N words=N chars=N`（一行、空白分隔）。
- 檔案不存在或不可讀：印 `error: <原因>` 到 stderr，exit code 1。
- 附標準庫 unittest 測試 `tests/test_txtstat.py`：至少涵蓋一般檔、空檔、檔案不存在三個案例。

## 非目標
- 不支援多檔案、不加 CLI 旗標、不用任何第三方套件、不做打包發佈。
- 不重構 repo 其他檔案、不動 `ai-workflow/` 與 `.github/`。

## 限制
- 技術：Python 3.10+ 標準庫 only；單一實作檔 + 一個測試檔。
- 時間：這是冒煙測試，工單總數控制在 2–3 張內。
- 相容性：在 ubuntu-latest 的 `python3` 可直接執行。
- 安全或資料限制：無。

## 驗收
- `python3 -m unittest discover -s tests` 全綠。
- smoke：對一個兩行測試檔跑 `python3 txtstat.py`，輸出格式正確（`lines=2 words=3 chars=N`）。
- 人工看過：錯誤訊息與輸出格式合理。
