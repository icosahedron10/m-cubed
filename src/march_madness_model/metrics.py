from __future__ import annotations

import pandas as pd


def expected_wins_per_cost(results: pd.DataFrame) -> pd.DataFrame:
    frame = results.copy()
    frame["value_per_cost"] = frame["expected_wins"] / frame["cost"]
    return frame.sort_values("value_per_cost", ascending=False)


def seed_value_summary(results: pd.DataFrame) -> pd.DataFrame:
    return (
        results.groupby("seed", as_index=False)
        .agg(expected_wins=("expected_wins", "mean"), cost=("cost", "mean"), value_per_cost=("value_per_cost", "mean"))
        .sort_values("value_per_cost", ascending=False)
    )


def compare_models(seed_only_results: pd.DataFrame, adjusted_results: pd.DataFrame) -> pd.DataFrame:
    merged = seed_only_results[["team_name", "expected_points"]].merge(
        adjusted_results[["team_name", "expected_points"]], on="team_name", suffixes=("_seed_only", "_adjusted")
    )
    merged["delta"] = merged["expected_points_adjusted"] - merged["expected_points_seed_only"]
    return merged.sort_values("delta", ascending=False)
