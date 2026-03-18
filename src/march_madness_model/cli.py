from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .bracket import load_bracket_csv
from .metrics import compare_models
from .optimizer import compare_greedy_vs_optimal, optimize_lineup
from .pricing import build_seed_price_table
from .probabilities import SeedProbabilityModel
from .simulator import TournamentSimulator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mm-model", description="March Madness fantasy draft modeling CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    price = subparsers.add_parser("build-price-table")
    price.add_argument("--output", type=Path)

    validate = subparsers.add_parser("validate-bracket")
    validate.add_argument("bracket_path", type=Path)

    simulate = subparsers.add_parser("simulate")
    simulate.add_argument("bracket_path", type=Path)
    simulate.add_argument("--matchup-probs-path", type=Path)
    simulate.add_argument("--expected-wins-path", type=Path)
    simulate.add_argument("--n-simulations", type=int, default=5000)
    simulate.add_argument("--random-seed", type=int, default=42)
    simulate.add_argument("--output", type=Path)

    optimize = subparsers.add_parser("optimize")
    optimize.add_argument("simulation_results_path", type=Path)
    optimize.add_argument("--budget", type=int, default=100)
    optimize.add_argument("--roster-size", type=int)
    optimize.add_argument("--max-teams-per-seed", type=int)

    compare = subparsers.add_parser("compare-models")
    compare.add_argument("seed_only_results_path", type=Path)
    compare.add_argument("adjusted_results_path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "build-price-table":
        table = build_seed_price_table()
        if args.output:
            table.to_csv(args.output, index=False)
            print(f"Wrote price table to {args.output}")
        else:
            print(table.to_csv(index=False))
        return 0
    if args.command == "validate-bracket":
        load_bracket_csv(str(args.bracket_path))
        print(f"Bracket at {args.bracket_path} is valid.")
        return 0
    if args.command == "simulate":
        bracket = load_bracket_csv(str(args.bracket_path))
        matchup_df = pd.read_csv(args.matchup_probs_path) if args.matchup_probs_path else None
        wins_df = pd.read_csv(args.expected_wins_path) if args.expected_wins_path else None
        model = SeedProbabilityModel.from_dataframes(matchup_df=matchup_df, expected_wins_df=wins_df)
        results = TournamentSimulator(bracket, model).simulate(n_simulations=args.n_simulations, random_seed=args.random_seed)
        if args.output:
            results.to_csv(args.output, index=False)
            print(f"Simulation results written to {args.output}")
        else:
            print(results.head(20).to_string(index=False))
        return 0
    if args.command == "optimize":
        results = pd.read_csv(args.simulation_results_path)
        optimal = optimize_lineup(results, budget=args.budget, roster_size=args.roster_size, max_teams_per_seed=args.max_teams_per_seed)
        print(optimal.lineup.to_string(index=False))
        print(f"Total cost: {optimal.total_cost}; expected points: {optimal.total_expected_points:.3f}")
        print(compare_greedy_vs_optimal(results, budget=args.budget, roster_size=args.roster_size, max_teams_per_seed=args.max_teams_per_seed).to_string(index=False))
        return 0
    if args.command == "compare-models":
        comparison = compare_models(pd.read_csv(args.seed_only_results_path), pd.read_csv(args.adjusted_results_path))
        print(comparison.head(20).to_string(index=False))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
