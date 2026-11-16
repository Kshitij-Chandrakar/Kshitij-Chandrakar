"""Checks for the contribution koi card renderer."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / ".github" / "scripts"))
from render_contribution_koi import render_svg  # noqa: E402


def test_render_svg_matches_reference_card() -> None:
    snapshot = {
        "contribution_history": {
            "observed_on": "2026-01-06",
            "days": [
                {"date": "2026-01-05", "contribution_count": 5},
                {"date": "2026-01-06", "contribution_count": 2},
            ],
        }
    }

    svg = render_svg(snapshot, b"GIF89a", "<h1>surface feeding for 2026-01-06</h1>", "octocat")

    assert "@octocat" in svg
    assert ">7</text>" in svg
    assert "SURFACE · new contribution" in svg
    assert "README.md" in svg
    assert "data:image/gif;base64,R0lGODlh" in svg
    assert svg.count("<rect") == 376
