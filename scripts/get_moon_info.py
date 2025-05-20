#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import pytz
import ephem
from lunarcalendar import Converter, Solar
from math import degrees

# 1. 讀取環境變數：經緯度與時區
LAT = os.getenv("LAT", "25.0330")    # 預設台北
LON = os.getenv("LON", "121.5654")
TZ  = os.getenv("TZ",  "Asia/Taipei")

# 2. 當前時間（本地時區）
local_tz = pytz.timezone(TZ)
now = datetime.now(local_tz)

# 3. 設定觀測者並計算月相＆天文位置
observer = ephem.Observer()
observer.lat = LAT
observer.lon = LON
observer.date = now

moon = ephem.Moon(observer)
phase_pct = moon.phase               # 月亮照亮百分比
alt_deg   = float(moon.alt) * 180.0/ephem.pi  # 月亮仰角（度）
az_deg    = float(moon.az)  * 180.0/ephem.pi  # 月亮方位（度）

# 4. 判斷月相形狀
def shape_name(phase):
    if phase < 1:
        return "🌑 新月"
    if phase < 25:
        return "🌒 蛾眉月"
    if phase < 50:
        return "🌓 上弦月"
    if phase < 75:
        return "🌔 盈凸月"
    if phase < 99:
        return "🌕 滿月"
    return "🌖 殘月"

shape = shape_name(phase_pct)

# 5. 西曆 & 陰曆
solar = Solar(now.year, now.month, now.day)
lunar = Converter.Solar2Lunar(solar)
lunar_str = f"{lunar.year}年{lunar.month}月{lunar.day}日"

# 6. 動態產生月相 SVG
svg_size = 120
r = 50
cx = cy = svg_size // 2
p = phase_pct / 100.0
arc = (1 - 2*p) if p <= 0.5 else (2*p - 1)
rx = abs(r * arc)
svg = f'''
<svg width="{svg_size}" height="{svg_size}" viewBox="0 0 {svg_size} {svg_size}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#222" />
  <ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r}" fill="#fff" />
  <ellipse cx="{cx + (r if p <= 0.5 else -r)}" cy="{cy}" rx="{rx}" ry="{r}" fill="#222" />
</svg>
'''

# 7. 星座判斷與 emoji
zodiac_list = [
    (120, ("摩羯座", "♑️")), (219, ("水瓶座", "♒️")), (321, ("雙魚座", "♓️")),
    (420, ("牡羊座", "♈️")), (521, ("金牛座", "♉️")), (621, ("雙子座", "♊️")),
    (722, ("巨蟹座", "♋️")), (823, ("獅子座", "♌️")), (923, ("處女座", "♍️")),
    (1023, ("天秤座", "♎️")), (1122, ("天蠍座", "♏️")), (1222, ("射手座", "♐️")),
    (1231, ("摩羯座", "♑️"))
]
md = now.month * 100 + now.day
for edge, (name, emoji) in zodiac_list:
    if md <= edge:
        zodiac, zodiac_emoji = name, emoji
        break

# 8. 節氣計算（地心太陽黃經）
jieqi_emojis = {
    "立春":"🌱","雨水":"💧","驚蟄":"⚡","春分":"🌸","清明":"🌿","穀雨":"🌾",
    "立夏":"☀️","小滿":"🌱","芒種":"🌾","夏至":"🌞","小暑":"🔥","大暑":"🌻",
    "立秋":"🍂","處暑":"🌤️","白露":"💧","秋分":"🍁","寒露":"❄️","霜降":"🌨️",
    "立冬":"⛄","小雪":"❄️","大雪":"☃️","冬至":"🌑","小寒":"🥶","大寒":"❄️"
}
jieqi_list = [
    "春分","清明","穀雨","立夏","小滿","芒種",
    "夏至","小暑","大暑","立秋","處暑","白露",
    "秋分","寒露","霜降","立冬","小雪","大雪",
    "冬至","小寒","大寒","立春","雨水","驚蟄"
]

sun = ephem.Sun(observer)
sun.compute(observer)
ecl = ephem.Ecliptic(sun)
ecl_long = degrees(ecl.lon) % 360

idx = int(ecl_long // 15)
curr_jieqi = jieqi_list[idx]
curr_emoji  = jieqi_emojis[curr_jieqi]
jieqi_info = f"<b>當前節氣：</b><span class=\"jieqi\">{curr_emoji} {curr_jieqi}</span>（太陽黃經 {ecl_long:.2f}°）"

# 9. 仰角與方位 emoji
alt_emoji = "⬆️" if alt_deg > 10 else "⬇️" if alt_deg < -10 else "↔️"
if 45 <= az_deg < 135:
    az_emoji = "➡️ 東"
elif 135 <= az_deg < 225:
    az_emoji = "⬇️ 南"
elif 225 <= az_deg < 315:
    az_emoji = "⬅️ 西"
else:
    az_emoji = "⬆️ 北"

# 10. 輸出 HTML
html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>月相報告</title>
  <style>
    body {{ font-family:'Noto Sans TC',Arial,sans-serif;background:#181d2a;color:#f3f3f3;margin:0;padding:0 }}
    .container {{ max-width:480px;margin:40px auto;background:#232946;border-radius:16px;box-shadow:0 4px 24px #0008;padding:32px }}
    h1 {{ text-align:center;font-size:2.2em;margin-bottom:0.2em }}
    .moon {{ text-align:center;margin:0.5em 0 }}
    .moon-emoji {{ font-size:2.5em }}
    .info {{ font-size:1.2em;line-height:2 }}
    .time {{ color:#a0a0a0;text-align:center;margin-bottom:1em }}
    .astro {{ color:#ffd700;font-weight:bold }}
    .jieqi {{ color:#7fffd4;font-weight:bold }}
    @media(max-width:600px) {{ .container{{padding:10px}} }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🌙 月相報告</h1>
    <div class="time">更新時間：{now.strftime('%Y-%m-%d %H:%M:%S')}</div>
    <div class="moon">{svg}<div class="moon-emoji">{shape}</div></div>
    <div class="info">
      <div><b>西曆：</b>{now.strftime('%Y-%m-%d %H:%M:%S')}</div>
      <div><b>陰曆：</b>{lunar_str}</div>
      <div><b>星座：</b><span class="astro">{zodiac_emoji} {zodiac}</span></div>
      <div>{jieqi_info}</div>
      <div><b>月相：</b>{phase_pct:.1f}%</div>
      <div><b>仰角：</b>{alt_deg:.1f}° {alt_emoji}</div>
      <div><b>方位：</b>{az_deg:.1f}° {az_emoji}</div>
      <div style="font-size:0.9em;color:#aaa;margin-top:1em;">
        Powered by GitHub Actions &amp; Python
      </div>
    </div>
  </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# print("已更新 index.html —— 當前節氣應正確顯示為「小滿」。")
