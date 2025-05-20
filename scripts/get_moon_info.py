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

# 6. 動態產生 SVG 月相圖
# phase_pct: 0(新月)~100(滿月)
svg_size = 120
r = 50
cx = cy = svg_size // 2
phase = phase_pct / 100.0
# 決定陰影方向（上弦月/下弦月）
if phase <= 0.5:
    # 右邊亮（上弦月）
    sweep = 1
    arc = 1 - 2 * phase
else:
    # 左邊亮（下弦月）
    sweep = 0
    arc = 2 * phase - 1
# 亮面橢圓的 x 半徑
rx = abs(r * arc)
svg = f'''
<svg width="{svg_size}" height="{svg_size}" viewBox="0 0 {svg_size} {svg_size}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#222" />
  <ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r}" fill="#fff" />
  <ellipse cx="{cx + (r if phase <= 0.5 else -r)}" cy="{cy}" rx="{rx}" ry="{r}" fill="#222" />
</svg>
'''

# 7. 輸出 HTML
html = f"""
<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>月相報告</title>
    <style>
        body {{ font-family: 'Noto Sans TC', 'Microsoft JhengHei', Arial, sans-serif; background: #181d2a; color: #f3f3f3; margin: 0; padding: 0; }}
        .container {{ max-width: 480px; margin: 40px auto; background: #232946; border-radius: 16px; box-shadow: 0 4px 24px #0008; padding: 32px; }}
        h1 {{ text-align: center; font-size: 2.2em; margin-bottom: 0.2em; }}
        .moon {{ text-align: center; margin: 0.5em 0; }}
        .moon-emoji {{ font-size: 2.5em; }}
        .info {{ font-size: 1.2em; line-height: 2; }}
        .time {{ color: #a0a0a0; text-align: center; margin-bottom: 1em; }}
        @media (max-width: 600px) {{ .container {{ padding: 10px; }} }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>🌙 月相報告</h1>
        <div class=\"time\">更新時間：{now.strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div class=\"moon\">{svg}<div class=\"moon-emoji\">{shape}</div></div>
        <div class=\"info\">
            <div><b>西曆：</b>{now.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div><b>陰曆：</b>{lunar_str}</div>
            <div><b>月相：</b>{phase_pct:.1f}%</div>
            <div><b>仰角：</b>{alt_deg:.1f}°</div>
            <div><b>方位：</b>{az_deg:.1f}°</div>
            <div style='font-size:0.9em;color:#aaa;margin-top:1em;'>Powered by GitHub Actions &amp; Python</div>
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("已更新 index.html") 