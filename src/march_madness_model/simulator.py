from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from .bracket import Bracket, round_name
from .pricing import get_seed_cost
from .probabilities import SeedProbabilityModel


class TournamentSimulator:
    def __init__(self, bracket: Bracket, probability_model: SeedProbabilityModel):
        self.bracket = bracket
        self.model = probability_model

    def _pick_winner(self, team_a, team_b, rng: np.random.Generator):
        p = self.model.matchup_probability(team_a, team_b)
        return team_a if rng.random() < p else team_b

    def _simulate_region(self, teams, region: str, rng):
        seed_map = {team.seed: team for team in teams}
        rounds = [[seed_map[a], seed_map[b]] for a, b in [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]]
        winners_by_round = []
        current = [self._pick_winner(game[0], game[1], rng) for game in rounds]
        winners_by_round.append(current)
        while len(current) > 1:
            next_round = []
            for idx in range(0, len(current), 2):
                next_round.append(self._pick_winner(current[idx], current[idx + 1], rng))
            current = next_round
            winners_by_round.append(current)
        return winners_by_round

    def simulate(self, n_simulations: int = 1000, random_seed: int | None = None) -> pd.DataFrame:
        rng = np.random.default_rng(random_seed)
        wins = defaultdict(float)
        reaches = defaultdict(lambda: defaultdict(float))
        teams = {team.name: team for team in self.bracket.teams}
        for _ in range(n_simulations):
            region_champs = {}
            for region, region_teams in self.bracket.teams_by_region().items():
                winners_by_round = self._simulate_region(region_teams, region, rng)
                for round_idx, round_winners in enumerate(winners_by_round, start=2):
                    label = round_name(round_idx)
                    for team in round_winners:
                        reaches[team.name][label] += 1
                        wins[team.name] += 1
                region_champs[region] = winners_by_round[-1][0]
            semis = self.bracket.semifinal_pairings(region_champs)
            final_teams = []
            for team_a, team_b in semis:
                winner = self._pick_winner(team_a, team_b, rng)
                reaches[winner.name][round_name(6)] += 1
                wins[winner.name] += 1
                final_teams.append(winner)
            champion = self._pick_winner(final_teams[0], final_teams[1], rng)
            reaches[champion.name][round_name(7)] += 1
            wins[champion.name] += 1
        rows = []
        for team in self.bracket.teams:
            expected_wins = wins[team.name] / n_simulations
            round_probs = {name: reaches[team.name][name] / n_simulations for name in [round_name(i) for i in range(2, 8)]}
            cost = get_seed_cost(team.seed)
            rows.append(
                {
                    "team_name": team.name,
                    "region": team.region,
                    "seed": team.seed,
                    "team_strength": team.team_strength,
                    "cost": cost,
                    "expected_wins": expected_wins,
                    "expected_points": expected_wins,
                    **round_probs,
                    "value_per_cost": expected_wins / cost,
                }
            )
        return pd.DataFrame(rows).sort_values(["expected_points", "seed"], ascending=[False, True]).reset_index(drop=True)
