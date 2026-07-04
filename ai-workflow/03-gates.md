# Objective Gates

> 客觀證據層(承重牆):「agent 說完成」不算完成,gate 綠了才算。
> 這是本專案 gate 指令的**唯一權威來源**——工單的 Required Verification 直接引用這裡,不要各自重寫。

## Gate 指令(權威來源)

| Gate | 指令 | 必須 | 何時跑 |
| --- | --- | --- | --- |
| Static | `python3 -m py_compile txtstat.py` | 是 | 每張工單 |
| Unit | `python3 -m unittest discover -s tests -v` | 是 | 每張工單 |
| Integration | 不適用（單檔 CLI，無外部系統） | 否 | — |
| Smoke / E2E | `printf 'hello world\nsecond line\n' > /tmp/smoke.txt && python3 txtstat.py /tmp/smoke.txt`（預期輸出 `lines=2 words=4 chars=24`） | 是 | close 前 |
| Manual Product Check | human owner 看輸出與錯誤訊息格式 | 是 | close 前 |

## 環境 / 前置

- 怎麼起服務：不需要，純 CLI，`python3` 直接執行。
- 怎麼備測試資料 / DB：測試內用 `tempfile` 自行產生，不留檔案。
- 需要的環境變數 / 憑證：無。

## Release / Merge Gate（總關卡）

- [ ] 上面所有「必須」gate 綠燈
- [ ] CI pass
- [ ] review findings 已仲裁
- [ ] 無未解 P0/P1
- [ ] 剩餘風險已記錄並被 human owner 接受

## 「Not Run」認定規則

只有以下明確原因可接受某個 gate not run,且必須寫在 report 的 Verification 欄:

- 此工單未觸及 `txtstat.py` 或 `tests/`（例如純文件工單），Static / Unit / Smoke 不適用。

除此之外一律視為**未通過**,不得 close。不接受「應該可以」「看起來沒問題」「只是小改所以不用驗」。
