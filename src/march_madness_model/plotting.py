from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_seed_value(seed_summary: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(seed_summary["seed"].astype(str), seed_summary["value_per_cost"])
    ax.set_title("Expected Wins per Cost by Seed")
    ax.set_xlabel("Seed")
    ax.set_ylabel("Value per Cost")
    fig.tight_layout()
    return fig, ax


def plot_model_comparison(comparison: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(comparison["delta"], bins=15)
    ax.set_title("Team-adjusted vs seed-only expected points delta")
    ax.set_xlabel("Expected points delta")
    ax.set_ylabel("Count")
    fig.tight_layout()
    return fig, ax
