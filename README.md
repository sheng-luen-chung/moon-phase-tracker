# 月相觀測

這個專案使用 GitHub Actions 每 10 分鐘產生並部署最新的月相、星座與節氣報告。頁面採手機優先設計，重點是讓使用者先看懂今天月亮的狀態，再逐步查看觀測與天文細節。

## 最新月相報告

[https://sheng-luen-chung.github.io/moon-phase-tracker/](https://sheng-luen-chung.github.io/moon-phase-tracker/)

若瀏覽器顯示舊內容，可以強制重新整理，或在網址後加上快取參數，例如：

```text
https://sheng-luen-chung.github.io/moon-phase-tracker/?v=latest
```

## 報告內容

- 今日月相名稱與照明率
- 月亮是否可見、仰角與觀察方向
- 亮面方向的觀察說明
- 月相進度條
- 陰曆日期、星座、節氣
- 太陽、地球、月亮相對位置示意圖
- 可展開的進階天文數值

## 設定說明

本專案可透過 GitHub Actions 環境變數或 Secrets 設定觀測位置：

- `LAT`: 緯度（預設：25.0330，台北）
- `LON`: 經度（預設：121.5654，台北）
- `TZ`: 時區（預設：Asia/Taipei）

## 更新方式

GitHub Actions 會每 10 分鐘執行 `scripts/get_moon_info.py`，產生最新的 `index.html`，並直接部署到 GitHub Pages。

自動更新不會再 commit/push `index.html` 回 repository，因此 Git 歷史不會累積每 10 分鐘一筆的自動更新 commit，本機也不需要為了同步最新時間資料而頻繁 pull。

## 技術細節

- 使用 Python 3.9
- 使用 ephem 計算天文位置
- 使用 lunarcalendar 轉換陰曆日期
- 使用 GitHub Actions 部署 GitHub Pages
