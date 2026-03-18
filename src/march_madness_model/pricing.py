from __future__ import annotations

import pandas as pd

MIN_SEED = 1
MAX_SEED = 16
MIN_COST = 1
MAX_COST = 25


def _validate_seed(seed: int) -> None:
    if not MIN_SEED <= int(seed) <= MAX_SEED:
        raise ValueError(f"Seed must be between {MIN_SEED} and {MAX_SEED}: {seed}")


def build_seed_price_table() -> pd.DataFrame:
    seeds = list(range(MIN_SEED, MAX_SEED + 1))
    slope = (MAX_COST - MIN_COST) / (MAX_SEED - MIN_SEED)
    costs = [int(round(MAX_COST - (seed - 1) * slope)) for seed in seeds]
    return pd.DataFrame({"seed": seeds, "cost": costs})


def get_seed_cost(seed: int) -> int:
    _validate_seed(seed)
    return int(build_seed_price_table().set_index("seed").loc[int(seed), "cost"])
