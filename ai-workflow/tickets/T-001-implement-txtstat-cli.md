# Ticket T-001: 實作 txtstat.py CLI

> 好工單只做一件事、有明確禁區、有客觀驗收。

## Objective
新增單檔 CLI `txtstat.py`，對一個檔案印出 `lines=N words=N chars=N`，錯誤時印 `error: <原因>` 到 stderr 並 exit 1。**只做實作，不寫測試（測試是 T-002）。**

## Context
- 相關背景：pipeline 冒煙測試的最小交付物。
- 相關 SPEC 條目：G1、G2；統計語意見 `00-spec.md` Expected Behavior 與 Open Decisions D2/D3/D4（採 SPEC 預設）。
- 前置工單：無。

## Scope
### Allowed
- 建立 `txtstat.py`，用 `sys.argv[1]` 取檔名。
- 讀檔（UTF-8 文字模式），計算 lines / words / chars（依 SPEC 預設語意）。
- 成功：stdout 印一行 `lines=<L> words=<W> chars=<C>`（單一空白分隔、以換行結尾），exit 0。
- 失敗（檔案不存在 / 不可讀 / 是目錄等）：stderr 印 `error: <原因>`，exit 1，stdout 不得有輸出。
- 提供 `if __name__ == "__main__":` 進入點；建議把計算包成一個可被 T-002 import 的函式（例如 `compute_stats(text) -> (lines, words, chars)`）。

### Not Allowed
- 不加任何 CLI 旗標、不支援多檔、不讀 stdin。
- 不引入第三方套件。
- 不建立或修改測試檔（留給 T-002）。
- 不做未要求的重構或格式化擴散。
- 若覺得 SPEC D1（smoke 期望值矛盾）擋住你 → 停下回報，不要自行改 gate 或改語意去硬湊 `words=3`。

## Files
### Allowed Files
- `txtstat.py`（新建）

### Forbidden Files
- `tests/**`
- `ai-workflow/**`
- `.github/**`
- `README.md`、`PROJECT-HANDOFF.md`、`.gitignore`
- 其他任何既有檔案

## Acceptance Criteria
- [ ] `txtstat.py` 存在於 repo 根目錄，純標準庫。
- [ ] 對一個一般檔輸出格式為 `lines=N words=N chars=N`（單行、空白分隔）。
- [ ] 空檔輸出 `lines=0 words=0 chars=0`，exit 0。
- [ ] 不存在的檔：stderr 有 `error: ...`，exit code 1，stdout 空。
- [ ] 計算語意符合 SPEC 預設（words=`split()`、lines=`splitlines()`、chars=含換行的 code point 數）。

## Required Verification
> gate 指令權威來源是 `../03-gates.md`；這裡只挑本工單必跑哪幾個。
- [ ] `03-gates.md`：Static —— `python3 -m py_compile txtstat.py`
- [ ] `03-gates.md`：Smoke —— 影響使用路徑，須跑。**注意 D1：若實際輸出 `words=4` 與 gate 期望 `words=3` 不符，如實回報「輸出=X、gate 期望=Y、疑為 gate 期望值錯」，不要改程式湊數。**
- [ ] manual smoke（本工單特有）：另跑空檔與不存在檔各一次，貼 exit code 與 stdout/stderr。

## Report Required
請回報：
1. 你改了什麼。
2. 實際修改的檔案。
3. 測試與 smoke 結果（含實際 stdout/stderr/exit code）。
4. 未完成事項。
5. 剩餘風險。
6. 是否有任何 scope deviation。
