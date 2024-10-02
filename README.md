# Pytest Automation Test

## 簡介

透過 Pytest 套件結合 Allure Report 套件達到自動化測試目的並產出 Test Report

並透過 Microsoft Teams Incoming Webhook 傳送 Adaptive Cards 做 Test Report Notification

利用 AWS Lambda 搭配 AWS DynamoDB 與 AWS S3 儲存測試失敗的資料

並透過前端網頁的 Navigation Bar 引導至不同專案的測試報告頁面

以及 DataTables 與 HighCharts 套件將測試失敗的數據做可視化呈現

## 測試方法

### 標準測試：測試 + 產生報告 + 資料上傳 AWS

```
cd /path/to/pytest-automation-test
python script/run_[project]_testing.py [test/prod]
```

### 單純測試：不產報告，結果只會輸出到 terminal

```
cd /path/to/pytest-automation-test

測試所有專案 + 所有案例 （包含 tests 資料夾底下所有案例）
pytest -v -s tests/ -m [test/prod] --env [test/prod]

測試指定專案內的所有案例
pytest -v -s tests/[project] -m [test/prod] --env [test/prod]

測試指定專案內的指定 API
pytest -v -s tests/[project]/test_xxx.py -m [test/prod] --env [test/prod]

參數控制
-v: terminal 的輸出更詳細，可以幫助理解跟除錯
-s: 將程式的標準輸出 (stdout) 印出來在 terminal 上，但不會被 allure 收集到，用於 debug
-m: 只測試有進行標記 (@pytest.mark) 的測試案例
```

### 單純測試 + 手動產生報告

```
cd /path/to/pytest-automation-test

將 allure 報告所需的測試結果 json 檔案存到指定資料夾
pytest -v -s tests/[project] -m [test/prod] --env [test/prod] --alluredir=./report/[project]/[env]/json

將過去測試的歷史記錄複製到指定資料夾
cp report/[project]/[env]/html/history/* report/[project]/[env]/json/history/

將測試說明檔複製到指定資料夾
cp configurations/[env]/[project]_environment.properties report/[project]/[env]/json/

透過 allure 程式將測試資料轉成測試報告，並透過 -o 指定輸出資料夾
/allure generate report/[project]/[env]/json -o report/[project]/[env]/html --clean
```

## 新增一個新 Project 的步驟

1. 在 `/api` 增加 Project 的檔案 (Ex: xxx_api.py) (Optional: 有需要重新寫的話才需新增)
2. 在 `/tests` 建立 Project 資料夾
3. 在 `/tests/[project]` 下建立 test files .py 檔
4. 在 `/testdata/env-[env]` 建立測試資料 excel 檔
5. 在 `/report` 建立 Project 資料夾
6. 在 `/report/[project]` 下建立 `[env]` 資料夾
7. 在 `/report/[project]/[env]` 下建立 `html`, `json`, `json/history`, `log` 共四個資料夾，並新增`.gitkeep` file
8. 在 `/script` 下建立對應的 project 執行 .py 檔
9. 在 `/configurations/[env]` 內增加對應的 allure 說明 .properties 檔
10. 在 `/configurations/[env]/config.yaml` 檔案內加入各專案的資料 (Host URL 跟 Access Key 等)
11. 在 `/configurations/teams_receiver.yaml` 檔案內增加此 Project 要在 Teams 通知的人員資料

## 為 Project 增加測試案例的步驟跟檢查

1. 在 `/tests/[project]` 下建立 `test_xxx.py` 檔 (務必要用 test 檔名開頭)
2. 在 `testdata` 的各個環境下放入測試資料
3. 可以開始針對各測試 test_xxx.py 檔案去寫 code

## config.yaml 檔案內的 Access Key 加解密

因為機敏性問題，程式內不能有明文的 api key 出現

因此在寫入 config 檔案前先用 python 做加密，在執行時用解密的去抓值

在 CMD 中用 python 來手動先處理資料加密的步驟

```
先開啟 python 執行環境
python

載入加解密套件
import cryptocode

加密
en_key = cryptocode.encrypt(key, pwd)

解密
de_key = cryptocode.decrypt(en_key, pwd)

用 print 就可以看到加密的字串，再放入 config 中
```

## 設定 Teams 的 webhook 步驟

1. 到 Teams 內的團隊
2. 點選右上角 「。。。」-「連接器」
3. 將「傳入 Webhook」的應用加入至團隊內
4. 給定名稱後建立，會拿到一串 URL
5. 將 URL 填入 `/configurations/teams_receiver.yaml` 的 URL 內
6. 將要通知的人加入到團隊內
7. 將要通知的人的資料填入 `/configurations/teams_receiver.yaml` （id 是 mail，name 是要顯示那個人在被 @ 時的字眼）

## 環境設定

### Set env file

1. 利用.env.example 在 pytest-automation-test 目錄下建立.env file
2. 利用.emv.js.example 在/web/js 建立 env.js file

### Allure

1. Install Java JRE （Allure report 是用 Java 建構的應用，需安裝才能執行產生 report 功能)

```
Install
$ sudo apt install default-jdk

Verify the installation
$ java --version
```

1. Install Allure
```
Download .deb file
$ wget https://github.com/allure-framework/allure2/releases/download/2.21.0/allure_2.21.0-1_all.deb

Install
$ sudo dpkg -i allure_2.21.0-1_all.deb

Verify the installation
$ allure --version
```

### Nginx

1. Install

```
$ sudo apt update
$ sudo apt install nginx
```

1. Set nginx

```
### add config file
$ sudo bash -c 'cat > /etc/nginx/conf.d/toolset.conf' << "EOF"
server {
    listen 80;
    listen [::]:80;
    root /home/ubuntu/pytest-automation-test/web;
    index index.html;
    server_name _;
    location / {
    try_files $uri $uri/ =404;
    }
    server_tokens off;
}
EOF

### 取消default站台
$ sudo unlink /etc/nginx/sites-enabled/default

### reload
$ sudo service nginx reload
```

## 參考資料

### 整體架構

https://medium.com/onedaysoftware/%E8%A1%97%E5%8F%A3%E6%94%AF%E4%BB%98-api-%E8%87%AA%E5%8B%95%E5%8C%96%E6%B8%AC%E8%A9%A6%E8%A7%A3%E6%B1%BA%E6%96%B9%E6%A1%88-ecf9ec0d0209
https://medium.com/onedaysoftware/%E9%97%9C%E6%96%BC%E8%A1%97%E5%8F%A3%E7%B7%9A%E4%B8%8A%E6%9C%8D%E5%8B%99%E7%9B%A3%E6%8E%A7%E7%9A%84%E9%82%A3%E4%BA%9B%E5%B0%8F%E4%BA%8B-2e0f1af2725e

### Nginx server

https://medium.com/%E4%B8%80%E5%80%8B%E4%BA%BA%E7%9A%84%E6%96%87%E8%97%9D%E5%BE%A9%E8%88%88/pm%E7%AD%86%E8%A8%98-%E9%80%8F%E9%81%8Enginx%E6%9E%B6%E8%A8%AD%E9%9D%9C%E6%85%8B%E7%B6%B2%E7%AB%99-1502c827024a

### Pytest, Allure

https://www.cnblogs.com/poloyy/category/1690628.html

### AWS Lambda, DynamoDB, S3

https://ithelp.ithome.com.tw/articles/10273715
