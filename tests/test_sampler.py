from pathlib import Path

from simcrowd.panel.sampler import (
    load_records,
    marginals,
    max_marginal_error,
    panel_marginals,
    weighted_sample,
)


def test_joint_sample_marginals_within_3pp():
    """Panel marginals stay within 3 percentage points of ACS sample marginals."""
    records = load_records(Path("data/census/sample.jsonl"))
    keys = ["education", "income_bin", "region", "age_bin"]
    pop = {k: marginals(records, k) for k in keys}
    panel = weighted_sample(records, 200, seed=42)
    for key, pop_m in pop.items():
        err = max_marginal_error(pop_m, panel_marginals(panel, key))
        assert err <= 0.03, f"{key} marginal error {err:.4f} exceeds 3pp"


def test_sample_preserves_record_fields():
    records = load_records(Path("data/census/sample.jsonl"))
    panel = weighted_sample(records, 20, seed=1)
    assert all("education" in r and "income_bin" in r for r in panel)
