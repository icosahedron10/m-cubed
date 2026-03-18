import pytest

from march_madness_model.pricing import build_seed_price_table, get_seed_cost


EXPECTED = {
    1: 25, 2: 23, 3: 22, 4: 20, 5: 19, 6: 17, 7: 15, 8: 14,
    9: 12, 10: 11, 11: 9, 12: 7, 13: 6, 14: 4, 15: 3, 16: 1,
}


def test_exact_seed_cost_mapping():
    table = build_seed_price_table()
    assert dict(zip(table['seed'], table['cost'])) == EXPECTED
    for seed, cost in EXPECTED.items():
        assert get_seed_cost(seed) == cost


@pytest.mark.parametrize('seed', [0, 17])
def test_invalid_seed(seed):
    with pytest.raises(ValueError):
        get_seed_cost(seed)
