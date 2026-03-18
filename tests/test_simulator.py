import pandas as pd

from march_madness_model.bracket import Bracket
from march_madness_model.probabilities import SeedProbabilityModel
from march_madness_model.simulator import TournamentSimulator


def build_valid_frame():
    rows = []
    for region in ['East', 'West', 'South', 'Midwest']:
        for seed in range(1, 17):
            rows.append({'team_name': f'{region} {seed}', 'region': region, 'seed': seed, 'team_strength': 0.0})
    return pd.DataFrame(rows)


def test_simulation_reproducibility():
    bracket = Bracket.from_frame(build_valid_frame())
    model = SeedProbabilityModel()
    sim = TournamentSimulator(bracket, model)
    a = sim.simulate(n_simulations=200, random_seed=7)
    b = sim.simulate(n_simulations=200, random_seed=7)
    pd.testing.assert_frame_equal(a, b)
