from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd
import pulp


@dataclass
class OptimizationResult:
    lineup: pd.DataFrame
    total_cost: int
    total_expected_points: float
    method: str


def greedy_optimize(team_values: pd.DataFrame, budget: int = 100, roster_size: int | None = None) -> OptimizationResult:
    ordered = team_values.sort_values(["value_per_cost", "expected_points"], ascending=[False, False]).reset_index(drop=True)
    chosen = []
    cost = 0
    for row in ordered.itertuples(index=False):
        if cost + int(row.cost) > budget:
            continue
        chosen.append(row._asdict())
        cost += int(row.cost)
        if roster_size is not None and len(chosen) >= roster_size:
            break
    lineup = pd.DataFrame(chosen)
    return OptimizationResult(lineup=lineup, total_cost=int(lineup.cost.sum()) if not lineup.empty else 0, total_expected_points=float(lineup.expected_points.sum()) if not lineup.empty else 0.0, method="greedy")


def optimize_lineup(
    team_values: pd.DataFrame,
    budget: int = 100,
    roster_size: int | None = None,
    max_teams_per_seed: int | None = None,
) -> OptimizationResult:
    problem = pulp.LpProblem("march_madness_lineup", pulp.LpMaximize)
    indices = list(team_values.index)
    variables = {i: pulp.LpVariable(f"x_{i}", lowBound=0, upBound=1, cat="Binary") for i in indices}
    problem += pulp.lpSum(team_values.loc[i, "expected_points"] * variables[i] for i in indices)
    problem += pulp.lpSum(team_values.loc[i, "cost"] * variables[i] for i in indices) <= budget
    if roster_size is not None:
        problem += pulp.lpSum(variables.values()) == roster_size
    if max_teams_per_seed is not None:
        for seed, seed_df in team_values.groupby("seed"):
            problem += pulp.lpSum(variables[i] for i in seed_df.index) <= max_teams_per_seed
    problem.solve(pulp.PULP_CBC_CMD(msg=False))
    chosen_idx = [i for i, var in variables.items() if math.isclose(var.value(), 1.0)]
    lineup = team_values.loc[chosen_idx].sort_values("expected_points", ascending=False).reset_index(drop=True)
    return OptimizationResult(lineup=lineup, total_cost=int(lineup.cost.sum()), total_expected_points=float(lineup.expected_points.sum()), method="integer_programming")


def compare_greedy_vs_optimal(team_values: pd.DataFrame, **kwargs) -> pd.DataFrame:
    greedy = greedy_optimize(team_values, **kwargs)
    optimal = optimize_lineup(team_values, **kwargs)
    return pd.DataFrame(
        [
            {"method": greedy.method, "total_cost": greedy.total_cost, "total_expected_points": greedy.total_expected_points},
            {"method": optimal.method, "total_cost": optimal.total_cost, "total_expected_points": optimal.total_expected_points},
        ]
    )
