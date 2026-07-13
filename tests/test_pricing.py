from simcrowd.synthesis.pricing import van_westendorp


def test_van_westendorp_ok():
    rows = [
        {"cheap": "0", "bargain": "5", "expensive": "20", "too_expensive": "35"},
        {"cheap": "5", "bargain": "12", "expensive": "20", "too_expensive": "35"},
        {"cheap": "0", "bargain": "5", "expensive": "12", "too_expensive": "20"},
    ]
    out = van_westendorp(rows)
    assert out["ok"] is True
    assert "optimal_price_point" in out
