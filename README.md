# 月相觀測

這個專案使用 GitHub Actions 每 10 分鐘自動更新當前所在地的月相資訊，包括：
- 月相形狀和百分比
- 月亮在天空中的位置（仰角和方位）
- 西曆日期時間
- 中國陰曆日期

## 最新月相報告
[點此查看](MOON_REPORT.md)

## 設定說明

本專案需要設定以下 GitHub Secrets：
- `LAT`: 緯度（預設：25.0330，台北）
- `LON`: 經度（預設：121.5654，台北）
- `TZ`: 時區（預設：Asia/Taipei）

## 技術細節

- 使用 Python 3.9
- 使用 pyephem 計算天文位置
- 使用 lunarcalendar 轉換陰曆日期
- 使用 GitHub Actions 自動化更新 