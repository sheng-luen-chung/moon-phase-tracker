#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timezone
import pytz
import ephem
from lunarcalendar import Converter, Solar
from math import degrees, cos, pi
from skyfield.api import load

# 1. 讀取經緯度與時區
LAT = os.getenv("LAT", "25.0330")
LON = os.getenv("LON", "121.5654")
TZ  = os.getenv("TZ",  "Asia/Taipei")

# 2. 當前時間（本地時區 → UTC）
local_tz  = pytz.timezone(TZ)
now_local = datetime.now(local_tz)
now_utc   = now_local.astimezone(timezone.utc)

# 3. Ephem 觀測者（僅用於月亮仰角 & 方位）
observer = ephem.Observer()
observer.lat  = LAT
observer.lon  = LON
observer.date = now_utc

moon = ephem.Moon(observer)
alt_deg = float(moon.alt) * 180.0/ephem.pi
az_deg  = float(moon.az)  * 180.0/ephem.pi

# 4. Skyfield 計算月相
ts  = load.timescale()
eph = load('de421.bsp')
t   = ts.from_datetime(now_utc)

earth   = eph['earth']
sun_sf   = eph['sun']
moon_sf  = eph['moon']

# 4.1 相位角 → 照亮度
phase_angle_deg = earth.at(t).observe(moon_sf).phase_angle(sun_sf).degrees
illum_pct       = (1 - cos(phase_angle_deg * pi/180)) / 2 * 100

# 4.2 黃經差判斷盈虧
e = earth.at(t)
lon_sun  = e.observe(sun_sf).apparent().ecliptic_latlon()[1].degrees
lon_moon = e.observe(moon_sf).apparent().ecliptic_latlon()[1].degrees
diff = (lon_moon - lon_sun) % 360

# 4.3 判斷月相名稱＋emoji
if illum_pct < 1:
    shape, emoji = "新月",   "🌑"
elif abs(diff - 90) < 5:
    shape, emoji = "上弦月", "🌓"
elif illum_pct < 50 and diff < 180:
    shape, emoji = "眉月",   "🌒"
elif abs(diff - 270) < 5:
    shape, emoji = "下弦月", "🌗"
elif illum_pct < 99 and diff < 180:
    shape, emoji = "盈凸月", "🌔"
elif illum_pct < 99 and diff > 180:
    shape, emoji = "殘月",   "🌖"
else:
    shape, emoji = "滿月",   "🌕"

# 5. 西曆＆陰曆
solar = Solar(now_local.year, now_local.month, now_local.day)
lunar = Converter.Solar2Lunar(solar)
lunar_str = f"{lunar.year}年{lunar.month}月{lunar.day}日"

# 6. 動態產生月相 SVG
svg_size = 120; r = 50; cx = cy = svg_size//2
p   = illum_pct / 100
arc = (1 - 2*p) if p <= 0.5 else (2*p - 1)
rx  = abs(r * arc)
svg = f'''
<svg width="{svg_size}" height="{svg_size}" viewBox="0 0 {svg_size} {svg_size}" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#222" />
  <ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r}" fill="#fff" />
  <ellipse cx="{cx + (r if p <= 0.5 else -r)}" cy="{cy}" rx="{rx}" ry="{r}" fill="#222" />
</svg>
'''

# 7. 星座判斷（改用太陽黃經／每 30° 一宮）
zodiac_names = [
    "白羊座","金牛座","雙子座","巨蟹座","獅子座","處女座",
    "天秤座","天蠍座","射手座","摩羯座","水瓶座","雙魚座"
]
zodiac_emojis = [
    "♈️","♉️","♊️","♋️","♌️","♍️",
    "♎️","♏️","♐️","♑️","♒️","♓️"
]
# 取得太陽黃經
sun = ephem.Sun(observer)
sun.compute(observer)
ecl = ephem.Ecliptic(sun)
sun_long = degrees(ecl.lon) % 360
idx = int(sun_long // 30)
zodiac, zodiac_emoji = zodiac_names[idx], zodiac_emojis[idx]

# 8. 節氣計算（地心太陽黃經，每 15° 一節氣）
jieqi_emojis = {
  "立春":"🌱","雨水":"💧","驚蟄":"⚡","春分":"🌸","清明":"🌿","穀雨":"🌾",
  "立夏":"☀️","小滿":"🌱","芒種":"🌾","夏至":"🌞","小暑":"🔥","大暑":"🌻",
  "立秋":"🍂","處暑":"🌤️","白露":"💧","秋分":"🍁","寒露":"❄️","霜降":"🌨️",
  "立冬":"⛄","小雪":"❄️","大雪":"☃️","冬至":"🌑","小寒":"🥶","大寒":"❄️"
}
jieqi_list = [
  "立春","雨水","驚蟄","春分","清明","穀雨",
  "立夏","小滿","芒種","夏至","小暑","大暑",
  "立秋","處暑","白露","秋分","寒露","霜降",
  "立冬","小雪","大雪","冬至","小寒","大寒"
]
idx_j = int(sun_long // 15)
curr_jieqi = jieqi_list[idx_j % 24]
curr_emoji  = jieqi_emojis[curr_jieqi]
jieqi_info  = f"<b>當前節氣：</b><span class=\"jieqi\">{curr_emoji} {curr_jieqi}</span>"

# 9. 仰角 & 方位 emoji
alt_emoji = "⬆️" if alt_deg>10 else "⬇️" if alt_deg< -10 else "↔️"
if 45<=az_deg<135:   az_emoji="➡️ 東"
elif 135<=az_deg<225: az_emoji="⬇️ 南"
elif 225<=az_deg<315: az_emoji="⬅️ 西"
else:                az_emoji="⬆️ 北"

# 10. 輸出 HTML
html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>月、星、節氣報告</title>
<style>
  body{{font-family:'Noto Sans TC',Arial,sans-serif;background:#181d2a;color:#f3f3f3}}
  .container{{max-width:480px;margin:40px auto;background:#232946;padding:32px;border-radius:16px}}
  h1{{text-align:center;color:#fff}}
  .moon-emoji{{font-size:2.5em;text-align:center}}
  .info{{line-height:1.8}}
  .jieqi{{
    color:#7fffd4;font-weight:bold
  }}
  .astro{{
    color:#ffd700;font-weight:bold
  }}
</style>
</head>
<body>
<div class="container">
  <h1>🌙 月相 &star; 星座 &star; 節氣</h1>
  <p class="moon-emoji">{emoji} {shape}</p>
  <pre style="color:#aaa">{svg}</pre>
  <div class="info">
    <div><b>時間：</b>{now_local.strftime('%Y-%m-%d %H:%M:%S')}</div>
    <div><b>陰曆：</b>{lunar_str}</div>
    <div><b>星座：</b><span class="astro">{zodiac_emoji} {zodiac}</span>（太陽黃經 {sun_long:.1f}°）</div>
    <div>{jieqi_info}（太陽黃經 {sun_long:.1f}°）</div>
    <div><b>月相：</b>{illum_pct:.1f}%</div>
    <div><b>月亮仰角：</b>{alt_deg:.1f}° {alt_emoji}</div>
    <div><b>月亮方位：</b>{az_deg:.1f}° {az_emoji}</div>
  </div>
</div>
</body>
</html>"""

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

# print("已更新 index.html！今日：", shape, emoji, "／星座：", zodiac, zodiac_emoji, "／節氣：", curr_jieqi)
