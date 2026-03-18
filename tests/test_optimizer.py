import pandas as pd

from march_madness_model.optimizer import greedy_optimize, optimize_lineup


def test_optimizer_budget_and_roster_constraints():
    df = pd.DataFrame([
        {'team_name': 'A', 'seed': 1, 'cost': 25, 'expected_points': 4.0, 'value_per_cost': 0.16},
        {'team_name': 'B', 'seed': 2, 'cost': 23, 'expected_points': 3.8, 'value_per_cost': 0.165},
        {'team_name': 'C', 'seed': 5, 'cost': 19, 'expected_points': 2.5, 'value_per_cost': 0.131},
        {'team_name': 'D', 'seed': 8, 'cost': 14, 'expected_points': 1.9, 'value_per_cost': 0.136},
        {'team_name': 'E', 'seed': 12, 'cost': 7, 'expected_points': 1.2, 'value_per_cost': 0.171},
        {'team_name': 'F', 'seed': 16, 'cost': 1, 'expected_points': 0.1, 'value_per_cost': 0.1},
    ])
    result = optimize_lineup(df, budget=50, roster_size=3, max_teams_per_seed=1)
    assert result.total_cost <= 50
    assert len(result.lineup) == 3
    greedy = greedy_optimize(df, budget=50, roster_size=3)
    assert greedy.total_cost <= 50
