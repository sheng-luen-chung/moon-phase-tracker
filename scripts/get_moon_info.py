#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timezone
import pytz
import ephem
from lunarcalendar import Converter, Solar
from math import degrees

# 1. 讀取經緯度與時區
LAT = os.getenv("LAT", "25.0330")
LON = os.getenv("LON", "121.5654")
TZ  = os.getenv("TZ",  "Asia/Taipei")

# 2. 當前時間（本地 → UTC）
local_tz  = pytz.timezone(TZ)
now_local = datetime.now(local_tz)
now_utc   = now_local.astimezone(timezone.utc)

# 3. Ephem 觀測者（僅作月亮仰角 & 方位）
observer = ephem.Observer()
observer.lat  = LAT
observer.lon  = LON
observer.date = now_utc

moon = ephem.Moon(observer)
alt_deg = float(moon.alt) * 180.0/ephem.pi
az_deg  = float(moon.az)  * 180.0/ephem.pi

# 4. Ephem 計算月相（不需下載外部星曆檔）
# 4.2 照亮度百分比（moon.phase 回傳 0–100 的百分比）
illum_pct = float(moon.phase)
# 4.3 黃經差判斷盈虧（moon/sun 已由 observer 計算，直接轉換黃道座標）
sun = ephem.Sun(observer)
moon_ecl = ephem.Ecliptic(moon)
sun_ecl  = ephem.Ecliptic(sun)
lon_moon = degrees(moon_ecl.lon) % 360
lon_sun  = degrees(sun_ecl.lon)  % 360
diff = (lon_moon - lon_sun) % 360

# 4.4 判斷月相名稱與 emoji
# 月相名稱用照亮度分辨凸月/弦月，避免 60% 以上的月亮被標成精確下弦月。
waxing = diff < 180
if illum_pct < 1:
    shape, emoji = "新月",   "🌑"
elif illum_pct > 99:
    shape, emoji = "滿月",   "🌕"
elif waxing:
    if illum_pct < 45:
        shape, emoji = "娥眉月", "🌒"
    elif illum_pct <= 55:
        shape, emoji = "上弦月", "🌓"
    else:
        shape, emoji = "盈凸月", "🌔"
else:
    if illum_pct > 55:
        shape, emoji = "虧凸月", "🌖"
    elif illum_pct >= 45:
        shape, emoji = "下弦月", "🌗"
    else:
        shape, emoji = "殘月",   "🌘"

# 5. 西曆 & 陰曆
solar = Solar(now_local.year, now_local.month, now_local.day)
lunar = Converter.Solar2Lunar(solar)
lunar_str = f"{lunar.year}年{lunar.month}月{lunar.day}日"

# 6. 動態產生月相 SVG
def crescent_path(cx, cy, r, side, amount):
    """Return a clipped crescent path for amount <= 0.5."""
    rx = max(r * abs(1 - 2 * amount), 0.01)
    if side == "right":
        return (
            f"M {cx} {cy-r} "
            f"A {r} {r} 0 0 1 {cx} {cy+r} "
            f"A {rx:.2f} {r} 0 0 0 {cx} {cy-r} Z"
        )
    return (
        f"M {cx} {cy-r} "
        f"A {r} {r} 0 0 0 {cx} {cy+r} "
        f"A {rx:.2f} {r} 0 0 1 {cx} {cy-r} Z"
    )


def render_moon_svg(illum_pct, diff):
    svg_size = 120
    r = 50
    cx = cy = svg_size // 2
    p = max(0, min(1, illum_pct / 100))
    waxing = diff < 180
    lit_side = "right" if waxing else "left"
    shadow_side = "left" if waxing else "right"
    dark = "#111820"
    lit = "#d8dec6"

    if p <= 0.01:
        phase_layers = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{dark}" />'
    elif p >= 0.99:
        phase_layers = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#moon-lit)" />'
    elif p <= 0.5:
        phase_layers = (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{dark}" />'
            f'<path d="{crescent_path(cx, cy, r, lit_side, p)}" fill="url(#moon-lit)" />'
        )
    else:
        phase_layers = (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#moon-lit)" />'
            f'<path d="{crescent_path(cx, cy, r, shadow_side, 1 - p)}" fill="{dark}" />'
        )

    return f'''
<svg class="moon-svg" width="{svg_size}" height="{svg_size}" viewBox="0 0 {svg_size} {svg_size}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{shape}，照亮度 {illum_pct:.1f}%">
  <defs>
    <radialGradient id="moon-lit" cx="35%" cy="30%" r="75%">
      <stop offset="0%" stop-color="#f3f0d2" />
      <stop offset="60%" stop-color="{lit}" />
      <stop offset="100%" stop-color="#aebca7" />
    </radialGradient>
    <clipPath id="moon-disc">
      <circle cx="{cx}" cy="{cy}" r="{r}" />
    </clipPath>
  </defs>
  <g clip-path="url(#moon-disc)">
    {phase_layers}
    <circle cx="38" cy="45" r="5" fill="#7a866e" opacity="0.35" />
    <circle cx="68" cy="37" r="3" fill="#7a866e" opacity="0.28" />
    <circle cx="78" cy="66" r="4" fill="#7a866e" opacity="0.32" />
    <circle cx="47" cy="76" r="3" fill="#7a866e" opacity="0.25" />
  </g>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0a0f16" stroke-width="4" />
</svg>
'''


svg = render_moon_svg(illum_pct, diff)

# 7. 星座判斷（依太陽黃經，每 30° 一宮）
zodiac_names = [
    "白羊座","金牛座","雙子座","巨蟹座","獅子座","處女座",
    "天秤座","天蠍座","射手座","摩羯座","水瓶座","雙魚座"
]
zodiac_emojis = [
    "♈️","♉️","♊️","♋️","♌️","♍️",
    "♎️","♏️","♐️","♑️","♒️","♓️"
]
# 取得地心太陽黃經
sun_ecl = ephem.Ecliptic(ephem.Sun(observer)).lon
sun_long = degrees(sun_ecl) % 360
z_idx = int(sun_long // 30)
zodiac, zodiac_emoji = zodiac_names[z_idx], zodiac_emojis[z_idx]

# 8. 節氣計算（依太陽黃經，每 15° 一節氣）
jieqi_list = [
    "春分","清明","穀雨","立夏","小滿","芒種",
    "夏至","小暑","大暑","立秋","處暑","白露",
    "秋分","寒露","霜降","立冬","小雪","大雪",
    "冬至","小寒","大寒","立春","雨水","驚蟄"
]
jieqi_emojis = {
    "春分":"🌸","清明":"🌿","穀雨":"🌾","立夏":"☀️","小滿":"🌱","芒種":"🌾",
    "夏至":"🌞","小暑":"🔥","大暑":"🌻","立秋":"🍂","處暑":"🌤️","白露":"💧",
    "秋分":"🍁","寒露":"❄️","霜降":"🌨️","立冬":"⛄","小雪":"❄️","大雪":"☃️",
    "冬至":"🌑","小寒":"🥶","大寒":"❄️","立春":"🌱","雨水":"💧","驚蟄":"⚡"
}
j_idx = int(sun_long // 15)
curr_jieqi = jieqi_list[j_idx % 24]
curr_emoji  = jieqi_emojis[curr_jieqi]
jieqi_info  = f"<b>當前節氣：</b><span class=\"jieqi\">{curr_emoji} {curr_jieqi}</span>"

# 9. 月亮仰角 & 方位 emoji
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
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>月相・星座・節氣報告</title>
<style>
  body {{ font-family:'Noto Sans TC',Arial,sans-serif;background:#181d2a;color:#f3f3f3;margin:0;padding:0 }}
  .container {{ max-width:480px;margin:40px auto;background:#232946;padding:32px;border-radius:16px }}
  h1 {{ text-align:center;color:#fff }}
  .moon-emoji {{ font-size:2.5em;text-align:center;margin:8px 0 }}
  .info {{ line-height:1.8;color:#ddd }}
  .astro {{ color:#ffd700;font-weight:bold }}
  .jieqi {{ color:#7fffd4;font-weight:bold }}
</style>
</head>
<body>
<div class="container">
  <h1>🌙 月相＆星座＆節氣</h1>
  <div class="moon-emoji">{emoji} {shape}</div>
  <div>{svg}</div>
  <div class="info">
    <div><b>時間：</b>{now_local.strftime('%Y-%m-%d %H:%M:%S')}</div>
    <div><b>陰曆：</b>{lunar_str}</div>
    <div><b>星座：</b><span class="astro">{zodiac_emoji} {zodiac}</span>（黃經 {sun_long:.1f}°）</div>
    <div>{jieqi_info}（黃經 {sun_long:.1f}°）</div>
    <div><b>月相：</b>{illum_pct:.1f}%</div>
    <div><b>仰角：</b>{alt_deg:.1f}° {alt_emoji}</div>
    <div><b>方位：</b>{az_deg:.1f}° {az_emoji}</div>
  </div>
</div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# print(f"已更新 index.html → 月相：{shape}{emoji}，星座：{zodiac}{zodiac_emoji}，節氣：{curr_jieqi}")
