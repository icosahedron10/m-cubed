import math

from march_madness_model.data_models import Team
from march_madness_model.probabilities import SeedProbabilityModel


def test_probabilities_sum_to_one():
    model = SeedProbabilityModel(seed_matchup_probs={(1, 16): 0.99})
    a = Team('A', 'East', 1)
    b = Team('B', 'East', 16)
    p = model.matchup_probability(a, b)
    q = model.matchup_probability(b, a)
    assert math.isclose(p + q, 1.0, rel_tol=1e-9)


def test_strength_adjustment_changes_probabilities():
    model = SeedProbabilityModel(seed_matchup_probs={(8, 9): 0.5}, baseline_blend=0.5, strength_weight=0.5)
    a = Team('A', 'East', 8, team_strength=2.0)
    b = Team('B', 'East', 9, team_strength=-1.0)
    assert model.matchup_probability(a, b) > 0.5
