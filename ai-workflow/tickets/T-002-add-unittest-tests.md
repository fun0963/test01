# Ticket T-002: 加 unittest 測試

> 好工單只做一件事、有明確禁區、有客觀驗收。

## Objective
新增 `tests/test_txtstat.py`，用標準庫 `unittest` 覆蓋「一般檔」「空檔」「檔案不存在」三案。**只加測試，不改 `txtstat.py`。**

## Context
- 相關背景：pipeline 冒煙測試的驗收證據層。
- 相關 SPEC 條目：G3；驗收語意見 `00-spec.md` Expected Behavior。
- 前置工單：T-001（測試需要 `txtstat.py` 已存在）。

## Scope
### Allowed
- 建立 `tests/test_txtstat.py`（必要時建立 `tests/` 目錄；若需要可加空的 `tests/__init__.py`）。
- 用 `tempfile` 產生測試資料，測完不留檔。
- 至少三個測試：
  1. 一般檔：已知內容 → 斷言 `lines/words/chars` 數值與 exit 0、輸出格式。
  2. 空檔 → 斷言 `lines=0 words=0 chars=0`、exit 0。
  3. 檔案不存在 → 斷言 exit code 1、stderr 含 `error:`、stdout 空。
- 驅動方式擇一：import `txtstat` 的函式直接斷言，或用 `subprocess` 跑 `python3 txtstat.py` 斷言 stdout/stderr/exit code（後者更貼近使用路徑，建議至少錯誤案用它驗 exit code）。

### Not Allowed
- 不修改 `txtstat.py`。若測試揭露 bug → 停下回報，交 Orchestrator 仲裁後開修復票，不要自己在本票改實作。
- 不引入第三方測試框架（pytest 等），只用標準庫 `unittest`。
- 不做未要求的重構。

## Files
### Allowed Files
- `tests/test_txtstat.py`（新建）
- `tests/__init__.py`（若需要，新建空檔）

### Forbidden Files
- `txtstat.py`
- `ai-workflow/**`
- `.github/**`
- `README.md`、`PROJECT-HANDOFF.md`、`.gitignore`
- 其他任何既有檔案

## Acceptance Criteria
- [ ] `tests/test_txtstat.py` 存在，純標準庫 `unittest`。
- [ ] 至少涵蓋一般檔 / 空檔 / 檔案不存在三案。
- [ ] 測試自產資料（`tempfile`），執行後不殘留檔案。
- [ ] `python3 -m unittest discover -s tests -v` 全綠。

## Required Verification
> gate 指令權威來源是 `../03-gates.md`；這裡只挑本工單必跑哪幾個。
- [ ] `03-gates.md`：Unit —— `python3 -m unittest discover -s tests -v`
- [ ] `03-gates.md`：Static —— 若 import `txtstat`，順帶確認 `python3 -m py_compile txtstat.py` 仍過（不改它）。

## Report Required
請回報：
1. 你改了什麼。
2. 實際修改的檔案。
3. 測試結果（貼 `unittest -v` 輸出重點：跑幾個、全綠）。
4. 未完成事項。
5. 剩餘風險（例如若某案依賴 D1–D4 未定語意）。
6. 是否有任何 scope deviation。
