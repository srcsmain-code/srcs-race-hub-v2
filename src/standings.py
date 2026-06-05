from __future__ import annotations

import pandas as pd

POINTS = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


def calculate_driver_standings(results: list[dict]) -> pd.DataFrame:
    rows = []
    for result in results:
        driver = result.get("driver")
        position = result.get("finish_position")
        fastest_lap = bool(result.get("fastest_lap_point", False))
        points = POINTS.get(position, 0) + (1 if fastest_lap and position and position <= 10 else 0)
        rows.append({"driver": driver, "points": points, "wins": 1 if position == 1 else 0})

    if not rows:
        return pd.DataFrame(columns=["driver", "points", "wins"])

    frame = pd.DataFrame(rows)
    return (
        frame.groupby("driver", as_index=False)
        .agg({"points": "sum", "wins": "sum"})
        .sort_values(["points", "wins"], ascending=False)
    )
