from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Team:
    name: str
    region: str
    seed: int
    team_strength: float = 0.0


@dataclass(frozen=True)
class Matchup:
    team_a: Team
    team_b: Team
    round_number: int
    region: str | None = None
    game_id: str | None = None


@dataclass
class SimulationResult:
    team_name: str
    region: str
    seed: int
    cost: int
    expected_wins: float
    expected_points: float
    round_probabilities: dict[str, float]
    value_per_cost: float


@dataclass
class Lineup:
    teams: list[Team]
    total_cost: int
    expected_points: float
    metadata: dict[str, Any] = field(default_factory=dict)
