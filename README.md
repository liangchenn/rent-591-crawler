# Rent-591 Crawler

簡易591租屋網房屋資料爬蟲

## Brief Description

- 向 rent591 網頁 API 發送資料請求
  - 請求headers中須包含 `csrf-token`，token 則由搜尋頁面取得
- 將 API 網址中的 `region` 改為 `regionid` 否則無法成功抓到正確區域資料
- 地區 (regionid) 則為 1 ~ 26 編號的代碼，分別對應不同縣市區域
- 透過 `firstRow` 參數來進行換頁，一頁的資料則為 30 筆
- 地區資料爬取完畢後會儲存至 `data/yyyymmdd/region-i.csv` 


## Example
- 以 `regionid=25` 為例
- 執行完畢於當前資料夾產生 `data/yyyymmdd/region-25.csv` 資料
  
```
$ python test.py
```

## Usage
- 抓取全部地區資料

```
$ python rent591crawl.py
```

## Data
- 資料欄位參考 `demo/region-24.csv`