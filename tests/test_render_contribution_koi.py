"""Checks for the contribution koi renderer."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / ".github" / "scripts"))
from render_contribution_koi import render_svg  # noqa: E402


def test_render_svg_embeds_koi_and_animates_active_days() -> None:
    calendar = {
        "totalContributions": 12,
        "weeks": [
            {
                "contributionDays": [
                    {"contributionCount": 0, "contributionLevel": "NONE", "weekday": 0},
                    {"contributionCount": 2, "contributionLevel": "SECOND_QUARTILE", "weekday": 1},
                ]
            }
        ],
    }

    svg = render_svg(calendar, b"GIF89a")

    assert "12 contributions in the last year" in svg
    assert "data:image/gif;base64,R0lGODlh" in svg
    assert svg.count('attributeName="x"') == 1
    assert "#006d32" in svg
