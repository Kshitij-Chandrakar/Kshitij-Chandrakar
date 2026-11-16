"""Render a GitHub contribution grid whose active days feed an embedded koi GIF."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any


COLORS = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}


def render_svg(calendar: dict[str, Any], koi_gif: bytes) -> str:
    """Build the animated SVG from a GitHub contribution calendar."""
    weeks = calendar["weeks"]
    total = int(calendar["totalContributions"])
    days = [day for week in weeks for day in week["contributionDays"]]
    active = [day for day in days if int(day["contributionCount"]) > 0]
    fish_size = min(256, 150 + total * 106 // 500)
    fish_x = 615 + (256 - fish_size) // 2
    fish_y = 28 + (256 - fish_size) // 2
    gif = base64.b64encode(koi_gif).decode("ascii")

    cells: list[str] = []
    moving: list[str] = []
    active_index = 0
    for column, week in enumerate(weeks):
        for day in week["contributionDays"]:
            x = 40 + column * 10
            y = 112 + int(day["weekday"]) * 10
            level = str(day["contributionLevel"])
            color = COLORS.get(level, COLORS["NONE"])
            cells.append(f'<rect x="{x}" y="{y}" width="8" height="8" rx="2" fill="{color}"/>')
            if int(day["contributionCount"]) > 0:
                phase = (active_index * 12 / max(1, len(active)))
                moving.append(
                    f'<rect x="{x}" y="{y}" width="8" height="8" rx="2" fill="{color}">' 
                    f'<animate attributeName="x" values="{x};675;675;{x}" keyTimes="0;.08;.1;1" '
                    f'dur="12s" begin="-{phase:.2f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="y" values="{y};150;150;{y}" keyTimes="0;.08;.1;1" '
                    f'dur="12s" begin="-{phase:.2f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.02;.1;1" '
                    f'dur="12s" begin="-{phase:.2f}s" repeatCount="indefinite"/>'
                    "</rect>"
                )
                active_index += 1

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300" role="img" aria-label="{total} contributions feeding a growing koi">
<rect width="900" height="300" rx="18" fill="#0d1117"/>
<text x="40" y="58" fill="#f0f6fc" font-family="system-ui,sans-serif" font-size="22" font-weight="600">My contributions feed this koi</text>
<text x="40" y="84" fill="#8b949e" font-family="system-ui,sans-serif" font-size="14">{total} contributions in the last year</text>
<g>{''.join(cells)}</g>
<path d="M575 92 C610 108 620 132 648 147" fill="none" stroke="#30363d" stroke-width="2" stroke-dasharray="5 7"/>
<g>{''.join(moving)}</g>
<g transform="translate({fish_x} {fish_y})">
  <image href="data:image/gif;base64,{gif}" width="{fish_size}" height="{fish_size}"/>
  <animateTransform attributeName="transform" additive="sum" type="scale" values="1;1.035;1" dur="1.2s" repeatCount="indefinite"/>
</g>
<text x="743" y="286" text-anchor="middle" fill="#8b949e" font-family="system-ui,sans-serif" font-size="13">grows with real GitHub activity</text>
</svg>'''


def main() -> None:
    """Read GitHub data and the koi GIF, then write the animated SVG."""
    parser = argparse.ArgumentParser()
    parser.add_argument("calendar", type=Path)
    parser.add_argument("koi_gif", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.calendar.read_text(encoding="utf-8-sig"))
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    args.output.write_text(render_svg(calendar, args.koi_gif.read_bytes()), encoding="utf-8")


if __name__ == "__main__":
    main()
