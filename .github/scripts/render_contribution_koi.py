"""Render a GitHub-style card around git-koi's animated GIF."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any


COLORS = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]


def _behavior(preview_html: str, days: list[dict[str, Any]]) -> tuple[str, str]:
    match = re.search(r"<h1>(.+?) for ", preview_html)
    name = match.group(1).upper() if match else "CRUISE"
    quiet_days = 0
    for day in reversed(days):
        if int(day["contribution_count"]) > 0:
            break
        quiet_days += 1
    details = {
        "DEEP REST": f"{quiet_days} quiet days",
        "REST": f"{quiet_days} quiet days",
        "SURFACE FEEDING": "new contribution",
        "DART": "high activity",
        "CRUISE": "steady activity",
    }
    return name.replace(" FEEDING", ""), details.get(name, "live activity")


def _level(count: int, positive_counts: list[int]) -> int:
    if count == 0:
        return 0
    thresholds = [positive_counts[len(positive_counts) * part // 4] for part in (1, 2, 3)]
    return min(4, 1 + sum(count > threshold for threshold in thresholds))


def render_svg(snapshot: dict[str, Any], koi_gif: bytes, preview_html: str, login: str) -> str:
    """Build the profile card from git-koi's own account snapshot and outputs."""
    history = snapshot["contribution_history"]
    days = history["days"]
    observed_on = date.fromisoformat(history["observed_on"])
    total = sum(int(day["contribution_count"]) for day in days)
    behavior, behavior_detail = _behavior(preview_html, days)
    counts = {date.fromisoformat(day["date"]): int(day["contribution_count"]) for day in days}
    positive_counts = sorted(count for count in counts.values() if count > 0) or [1]
    final_sunday = observed_on - timedelta(days=(observed_on.weekday() + 1) % 7)
    first_sunday = final_sunday - timedelta(weeks=52)

    cells: list[str] = []
    for column in range(53):
        for row in range(7):
            day = first_sunday + timedelta(days=column * 7 + row)
            count = counts.get(day, 0) if day <= observed_on else 0
            cells.append(
                f'<rect x="{75 + column * 10}" y="{555 + row * 10}" width="8" height="8" '
                f'rx="2" fill="{COLORS[_level(count, positive_counts)]}"/>'
            )

    gif = base64.b64encode(koi_gif).decode("ascii")
    total_label_x = 60 + len(f"{total:,}") * 17
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="680" height="660" viewBox="0 0 680 660" role="img" aria-label="{total:,} contributions growing {login}'s koi">
<defs>
  <radialGradient id="pond" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#164a70"/><stop offset="1" stop-color="#061b32"/></radialGradient>
  <linearGradient id="avatar" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#2dd4bf"/><stop offset="1" stop-color="#2563eb"/></linearGradient>
  <filter id="shadow"><feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#000" flood-opacity=".45"/></filter>
  <clipPath id="pond-clip"><rect x="32" y="86" width="616" height="360" rx="18"/></clipPath>
</defs>
<rect x="12" y="12" width="656" height="636" rx="24" fill="#0d1117" stroke="#30363d" stroke-width="2" filter="url(#shadow)"/>
<circle cx="58" cy="50" r="20" fill="url(#avatar)" stroke="#8b949e"/>
<text x="88" y="59" fill="#f0f6fc" font-family="system-ui,sans-serif" font-size="25" font-weight="700">@{login}</text>
<rect x="543" y="31" width="101" height="38" rx="9" fill="#161b22" stroke="#30363d"/>
<text x="593" y="55" text-anchor="middle" fill="#8b949e" font-family="ui-monospace,monospace" font-size="14">README.md</text>
<rect x="32" y="86" width="616" height="360" rx="18" fill="url(#pond)" stroke="#1f6feb" stroke-opacity=".5"/>
<image href="data:image/gif;base64,{gif}" x="40" y="30" width="600" height="600" clip-path="url(#pond-clip)" style="image-rendering:pixelated"/>
<text x="42" y="505" fill="#f0f6fc" font-family="Georgia,serif" font-size="28" font-style="italic" font-weight="700">{total:,}</text>
<text x="{total_label_x}" y="505" fill="#8b949e" font-family="system-ui,sans-serif" font-size="17">contributions</text>
<rect x="430" y="472" width="214" height="44" rx="10" fill="#111827" stroke="#58a6ff" stroke-width="2"/>
<text x="537" y="500" text-anchor="middle" fill="#b6d8ff" font-family="system-ui,sans-serif" font-size="15" font-weight="700">{behavior} · {behavior_detail}</text>
<g>{''.join(cells)}</g>
</svg>'''


def main() -> None:
    """Read git-koi outputs and write the profile-card SVG."""
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("koi_gif", type=Path)
    parser.add_argument("preview", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8-sig"))
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", "Kshitij-Chandrakar")
    args.output.write_text(
        render_svg(snapshot, args.koi_gif.read_bytes(), args.preview.read_text(encoding="utf-8"), login),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
