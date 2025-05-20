#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import pytz
import ephem
from lunarcalendar import Converter, Solar

# 1. 讀取環境變數：經緯度與時區
LAT = os.getenv("LAT", "25.0330")    # 預設台北
LON = os.getenv("LON", "121.5654")
TZ  = os.getenv("TZ",  "Asia/Taipei")

# 2. 當前時間（本地時區）
local_tz = pytz.timezone(TZ)
now = datetime.now(local_tz)

# 3. 計算月相＆天文位置
observer = ephem.Observer()
observer.lat = LAT
observer.lon = LON
observer.date = now

moon = ephem.Moon(observer)
phase_pct = moon.phase                # 0–100%，月亮被照亮的百分比
alt_deg  = float(moon.alt) * 180.0/ephem.pi   # 仰角（度）
az_deg   = float(moon.az)  * 180.0/ephem.pi   # 方位（度）

# 4. 判斷「形狀」名稱
def shape_name(phase):
    if phase < 1:   return "🌑 新月"
    if phase < 25:  return "🌒 蛾眉月"
    if phase < 50:  return "🌓 上弦月"
    if phase < 75:  return "🌔 盈凸月"
    if phase < 99:  return "🌕 滿月"
    return "🌖 殘月"

shape = shape_name(phase_pct)

# 5. 西曆 & 陰曆
solar = Solar(now.year, now.month, now.day)
lunar = Converter.Solar2Lunar(solar)
lunar_str = f"{lunar.year}年{lunar.month}月{lunar.day}日"

# 6. 輸出 Markdown
md = f"""
## 月相報告（{now.strftime('%Y-%m-%d %H:%M:%S')}）

- **西曆**：{now.strftime('%Y-%m-%d %H:%M:%S')}
- **陰曆**：{lunar_str}
- **月相**：{phase_pct:.1f}% ({shape})
- **仰角**：{alt_deg:.1f}°
- **方位**：{az_deg:.1f}°
"""

with open("MOON_REPORT.md", "w", encoding="utf-8") as f:
    f.write(md)
print("已更新 MOON_REPORT.md") 