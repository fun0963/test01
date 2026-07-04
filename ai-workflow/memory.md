# Project Memory

> 長任務不能靠模型上下文記憶。每輪結束把穩定事實寫進來，讓下一輪不必重新理解。

## Stable Facts
- txtstat.py 單檔 CLI 實作完成，compute_stats(text) 基於 splitlines/split/len 實現，lines/words/chars 語義已於 SPEC D1-D4 拍板
- 讀檔採 open(path, "r", encoding="utf-8")，OSError 走 error: 路徑；UnicodeDecodeError 已由 T-003 併入 except tuple，非 UTF-8 檔走標準 error: 格式、無 traceback
- Smoke gate（words=4）符合預期；測試框架已實作（PR #6 test_txtstat.py：三案正常/空/不存在，Unit gate 綠燈）
- T-002（unittest 框架）已 merge 進 main；Unit gate 驗收完成；T-003（UnicodeDecodeError 修復）已 merge 進 main；T-004（test_empty_file stderr 斷言一致性）開為品質補強不阻擋

## Architecture Notes
- <系統結構與重要限制>

## Conventions
- <命名、測試、錯誤處理、資料格式約定>

## Decisions
- D1（smoke words=4）：已於 SPEC 與 03-gates.md 拍板，遺留 smoke-test 在 gate 中一並驗收
- D2-D4（chars/lines 邊界語意、錯誤訊息格式）：已依 Orchestrator 預設實作，human owner 於 T-001 merge 時確認

## Known Risks
- RK-002/RK-003：邊界語意與錯誤訊息格式，待 human 終審驗收

## Do Not Repeat
- Path traversal（R-002）：CLI 輸入來自 sys.argv[1]（使用者自行提供），無信任邊界；CWE-22 不適用於本機工具
- 勿包裝 OSError 訊息：SPEC D4 明確要求帶上 OS 例外訊息，直接傳遞符合預期
