from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from .data_models import Team

FIRST_ROUND_SEED_PAIRS = [
    (1, 16),
    (8, 9),
    (5, 12),
    (4, 13),
    (6, 11),
    (3, 14),
    (7, 10),
    (2, 15),
]

ROUND_LABELS = {
    1: "round_of_64",
    2: "round_of_32",
    3: "sweet_16",
    4: "elite_8",
    5: "final_4",
    6: "championship",
    7: "title",
}


@dataclass
class Bracket:
    teams: list[Team]

    @classmethod
    def from_frame(cls, teams_df: pd.DataFrame) -> "Bracket":
        teams = [
            Team(
                name=row.team_name,
                region=row.region,
                seed=int(row.seed),
                team_strength=float(getattr(row, "team_strength", 0.0)),
            )
            for row in teams_df.itertuples(index=False)
        ]
        bracket = cls(teams=teams)
        bracket.validate()
        return bracket

    def validate(self) -> None:
        if len(self.teams) != 64:
            raise ValueError("Bracket must contain exactly 64 teams")
        regions = {team.region for team in self.teams}
        if len(regions) != 4:
            raise ValueError("Bracket must contain exactly four regions")
        for region in regions:
            seeds = sorted(team.seed for team in self.teams if team.region == region)
            if seeds != list(range(1, 17)):
                raise ValueError(f"Region {region} must contain seeds 1 through 16 exactly once")

    def teams_by_region(self) -> dict[str, list[Team]]:
        return {
            region: sorted([team for team in self.teams if team.region == region], key=lambda t: t.seed)
            for region in sorted({team.region for team in self.teams})
        }

    def first_round_games(self) -> list[tuple[Team, Team, str, int]]:
        games: list[tuple[Team, Team, str, int]] = []
        for region, teams in self.teams_by_region().items():
            seed_map = {team.seed: team for team in teams}
            for idx, (seed_a, seed_b) in enumerate(FIRST_ROUND_SEED_PAIRS, start=1):
                games.append((seed_map[seed_a], seed_map[seed_b], region, idx))
        return games

    def semifinal_pairings(self, region_winners: dict[str, Team]) -> list[tuple[Team, Team]]:
        ordered_regions = sorted(region_winners)
        return [
            (region_winners[ordered_regions[0]], region_winners[ordered_regions[1]]),
            (region_winners[ordered_regions[2]], region_winners[ordered_regions[3]]),
        ]


def load_bracket_csv(path: str) -> Bracket:
    return Bracket.from_frame(pd.read_csv(path))


def validate_bracket_frame(df: pd.DataFrame) -> None:
    Bracket.from_frame(df)


def round_name(round_number: int) -> str:
    return ROUND_LABELS[round_number]
