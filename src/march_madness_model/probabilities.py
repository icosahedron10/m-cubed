from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import math
import pandas as pd

from .data_models import Team


@dataclass
class SeedProbabilityModel:
    seed_matchup_probs: dict[tuple[int, int], float] | None = None
    seed_expected_wins: dict[int, float] | None = None
    latent_seed_ratings: Mapping[int, float] | None = None
    logistic_scale: float = 1.0
    baseline_blend: float = 0.7
    strength_weight: float = 0.15

    @classmethod
    def from_dataframes(
        cls,
        matchup_df: pd.DataFrame | None = None,
        expected_wins_df: pd.DataFrame | None = None,
        **kwargs,
    ) -> "SeedProbabilityModel":
        matchup_probs = None
        if matchup_df is not None:
            matchup_probs = {
                (int(row.seed_a), int(row.seed_b)): float(row.prob_seed_a_wins)
                for row in matchup_df.itertuples(index=False)
            }
        expected_wins = None
        if expected_wins_df is not None:
            expected_wins = {int(row.seed): float(row.expected_wins) for row in expected_wins_df.itertuples(index=False)}
        return cls(seed_matchup_probs=matchup_probs, seed_expected_wins=expected_wins, **kwargs)

    def seed_only_probability(self, seed_a: int, seed_b: int) -> float:
        if self.seed_matchup_probs and (seed_a, seed_b) in self.seed_matchup_probs:
            return self.seed_matchup_probs[(seed_a, seed_b)]
        if self.seed_matchup_probs and (seed_b, seed_a) in self.seed_matchup_probs:
            return 1.0 - self.seed_matchup_probs[(seed_b, seed_a)]
        return self.latent_seed_probability(seed_a, seed_b)

    def latent_seed_probability(self, seed_a: int, seed_b: int) -> float:
        ratings = self.latent_seed_ratings or {seed: (17 - seed) for seed in range(1, 17)}
        diff = (ratings[seed_a] - ratings[seed_b]) / max(self.logistic_scale, 1e-9)
        return 1.0 / (1.0 + math.exp(-diff))

    def blended_probability(self, team_a: Team, team_b: Team) -> float:
        baseline = self.seed_only_probability(team_a.seed, team_b.seed)
        strength_adjusted = self.latent_seed_probability(team_a.seed, team_b.seed)
        strength_adjusted = 1.0 / (1.0 + math.exp(-(math.log(baseline / (1 - baseline)) + self.strength_weight * (team_a.team_strength - team_b.team_strength))))
        p = self.baseline_blend * baseline + (1 - self.baseline_blend) * strength_adjusted
        return min(max(p, 0.0), 1.0)

    def matchup_probability(self, team_a: Team, team_b: Team) -> float:
        p = self.blended_probability(team_a, team_b)
        q = 1.0 - p
        return p / (p + q)
