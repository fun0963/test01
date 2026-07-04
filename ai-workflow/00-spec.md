# SPEC: txtstat CLI（pipeline 冒煙測試）

> 這是整個專案的 done definition，不是裝飾。沒寫進 SPEC 的都不算驗收範圍。
> 本檔由 Orchestrator 第一輪診斷產出，來源：`project-brief.md` + repo 現況 + `03-gates.md`。

## Problem
需要一個零相依的最小真實專案，用來冒煙測試 Orchestrator → Executor → Reviewer → 仲裁 → 蒸餾整條 pipeline 是否跑得通。專案本身交付一個文字檔統計小工具 `txtstat.py`。

## Goals
- [ ] G1：新增單檔 CLI `txtstat.py`（repo 根目錄），`python3 txtstat.py <file>` 對存在且可讀的檔案印出 `lines=N words=N chars=N`（單行、單一空白分隔、以換行結尾），exit code 0。
- [ ] G2：檔案不存在或不可讀時，印 `error: <原因>` 到 **stderr**，exit code 1，且不印任何統計到 stdout。
- [ ] G3：新增標準庫 `unittest` 測試 `tests/test_txtstat.py`，至少涵蓋「一般檔」「空檔」「檔案不存在」三案。

## Non-Goals
- 不支援多檔案、不加任何 CLI 旗標（`-l`/`--help` 等）、不讀 stdin。
- 不使用任何第三方套件；不做打包 / 發佈 / setup.py。
- 不重構 repo 其他檔案；不動 `ai-workflow/`、`.github/`、`README.md`、`PROJECT-HANDOFF.md`。

## Users / Systems Affected
- 只有 pipeline 測試者。無正式使用者、無外部系統、無資料庫。

## Expected Behavior
- `python3 txtstat.py existing.txt` → stdout 一行 `lines=<L> words=<W> chars=<C>`，exit 0。
- `python3 txtstat.py missing.txt` → stderr `error: <原因>`，exit 1，stdout 無輸出。
- 空檔 → `lines=0 words=0 chars=0`，exit 0。

### 統計語意（Orchestrator 預設，標 ★ 者待 human 確認，見下方 Open Decisions）
- `words`：以任意空白切分並收合連續空白（`str.split()` 語意）。
- `lines`：以 `str.splitlines()` 的元素數計（「幾行文字」）。★ 對「最後一行無換行」的檔案，此語意與 `wc -l`（數 `\n`）會差 1。
- `chars`：讀進的文字長度，以 Unicode code point 計，**包含**換行字元。★ 是否含尾端換行 / 是否改用 byte 數待確認。
- 讀檔以文字模式 UTF-8 讀取。

## Constraints
- Python 3.10+ 標準庫 only；單一實作檔 `txtstat.py` + 單一測試檔 `tests/test_txtstat.py`。
- 在 ubuntu-latest 的 `python3` 可直接執行。
- 工單總數控制在 2–3 張（冒煙測試）。
- 測試資料一律用 `tempfile` 產生，不留檔案。

## Acceptance Criteria
- [ ] 測試：`python3 -m unittest discover -s tests -v` 全綠（見 `03-gates.md` Unit）。
- [ ] Static：`python3 -m py_compile txtstat.py` 通過（見 `03-gates.md` Static）。
- [ ] smoke：見 `03-gates.md` Smoke —— **注意：現行 gate 的期望值與輸入不一致（見 Open Decisions D1），須先由 human 拍板才能宣告 smoke 綠燈。**
- [ ] 真實檔案驗證：對一般檔 / 空檔 / 不存在檔各跑一次，行為符合 Expected Behavior。
- [ ] 文件更新：本 SPEC 與 tickets 已產出（不需額外 user 文件）。
- [ ] human owner 驗收：輸出格式與錯誤訊息合理。

## Open Decisions（需 human owner 拍板）
- **D1（阻擋 smoke）**：`03-gates.md` Smoke 的輸入 `printf 'hello world\nsecond line\n'` 實含 **4** 個單字（hello, world, second, line），但期望輸出寫 `words=3`，兩者矛盾。需擇一：(a) 把 gate 期望改成 `words=4`；(b) 把 smoke 輸入改成真正 3 個字的檔。`03-gates.md` 是 gate 權威來源，Orchestrator 不逕改，交 human 決定。
- **D2**：`chars` 是否計入尾端換行、以及用 code point 還是 byte。預設：含換行、用 code point。
- **D3**：`lines` 對「最後一行無換行」的檔案採 `splitlines()`（幾行文字）或 `wc -l`（數 `\n`）。預設：`splitlines()`。
- **D4**：`error:` 後的原因字串格式（用 OS error 原文 vs 自訂訊息）。預設：帶上 OS 例外訊息，格式 `error: <exception message>`。

## Release / Merge Gate
> 詳細 gate 指令與 not-run 規則見 `03-gates.md`。
- [ ] `03-gates.md` 所有「必須」gate 綠燈（D1 解決後 smoke 才算數）
- [ ] CI pass
- [ ] review findings 已仲裁
- [ ] 無未解 P0/P1
- [ ] 剩餘風險已記錄並被接受
