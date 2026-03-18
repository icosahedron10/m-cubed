import pandas as pd
import pytest

from march_madness_model.bracket import Bracket


def build_valid_frame():
    rows = []
    for region in ['East', 'West', 'South', 'Midwest']:
        for seed in range(1, 17):
            rows.append({'team_name': f'{region} {seed}', 'region': region, 'seed': seed, 'team_strength': 0.0})
    return pd.DataFrame(rows)


def test_bracket_validation_and_first_round_pairings():
    bracket = Bracket.from_frame(build_valid_frame())
    games = bracket.first_round_games()
    assert len(games) == 32
    east_games = [g for g in games if g[2] == 'East']
    assert [(a.seed, b.seed) for a, b, _, _ in east_games] == [(1,16),(8,9),(5,12),(4,13),(6,11),(3,14),(7,10),(2,15)]


def test_invalid_region_seed_set():
    frame = build_valid_frame()
    frame.loc[0, 'seed'] = 2
    with pytest.raises(ValueError):
        Bracket.from_frame(frame)
