# March Madness Fantasy Draft Model

A reusable Python 3.11+ analytics environment for researching a 64-team NCAA tournament fantasy draft game where lineup value depends on seed-based pricing, simulated bracket outcomes, and budget-constrained optimization.

## Game Rules

- 64-team bracket with four regions and seeds 1 through 16 in each region.
- Team cost depends only on seed.
- Costs follow a rounded linear scale from 25 for a 1-seed down to 1 for a 16-seed.
- Total draft budget is 100.
- Each team earns 1 point per NCAA tournament win.
- Objective: maximize expected total wins under budget.

## Why bracket simulation matters

Tournament outcomes are path-dependent: a team's expected wins are not just a function of its own quality, but also which opponents survive into later rounds. A Monte Carlo bracket simulator captures this dependency by repeatedly simulating the full tournament tree rather than treating games independently.

## Modeling assumptions

- **Seed pricing:** deterministic and independent of team identity.
- **Seed-only model:** uses an empirical seed-vs-seed win lookup table when available.
- **Latent seed model:** falls back to a logistic win probability from latent seed ratings.
- **Team-adjusted model:** blends the seed baseline with optional team-strength ratings so future enhancements can incorporate power ratings, betting markets, injuries, or custom priors.
- **Expected points:** equal expected wins because scoring awards 1 point per win.

## Project structure

```text
src/march_madness_model/
  pricing.py
  data_models.py
  probabilities.py
  bracket.py
  simulator.py
  optimizer.py
  metrics.py
  plotting.py
  cli.py
data/example/
notebooks/
tests/
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quickstart

Build the price table:

```bash
mm-model build-price-table
```

Validate the example bracket:

```bash
mm-model validate-bracket data/example/example_bracket_64.csv
```

Run simulation:

```bash
mm-model simulate data/example/example_bracket_64.csv \
  --matchup-probs-path data/example/seed_matchup_probs.csv \
  --expected-wins-path data/example/seed_expected_wins.csv \
  --n-simulations 5000 \
  --random-seed 42 \
  --output simulation_results.csv
```

Optimize a lineup under the 100 budget:

```bash
mm-model optimize simulation_results.csv --budget 100 --roster-size 8
```

## CLI commands

- `build-price-table`
- `validate-bracket`
- `simulate`
- `optimize`
- `compare-models`

## Example data

- `data/example/example_bracket_64.csv`: example 64-team bracket scaffold.
- `data/example/seed_expected_wins.csv`: simple baseline expected wins by seed.
- `data/example/seed_matchup_probs.csv`: seed-vs-seed empirical-style win probabilities.

## Analysis workflows

- Rank seeds by historical or assumed value using `metrics.seed_value_summary`.
- Compare expected wins per cost with `metrics.expected_wins_per_cost`.
- Contrast seed-only vs team-adjusted models with `metrics.compare_models`.
- Explore sensitivity to team-strength weights, logistic scale, or budget constraints in the notebooks.

## Future extensions

- Add play-in support and dynamic 68-team bracket ingestion.
- Fit seed matchup probabilities from historical NCAA results.
- Import external team-strength forecasts from KenPom, betting markets, or custom ratings.
- Add scenario analysis for injury news and bracket uncertainty.
- Support portfolio-style lineup generation with exposure constraints across multiple entries.
