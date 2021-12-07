import pandas as pd

from localize_be.core import scoring


def test_calculate_distance():
    pois = pd.DataFrame([
        {"Category": "School", "Weight": 10, "Lat": 50.63604, "Lng": 4.78471}
    ])
    d = {
        "Lat": 50.5,
        "Lng": 4.7,
    }
    d = scoring._distance_average(d, pois)
    assert round(d, 0) == 16


def test_calculate_distance_weighted_averages():
    pois = pd.DataFrame([
        {"Category": "School", "Weight": 100, "Lat": 50.63604, "Lng": 4.78471},
        {"Category": "School", "Weight": 1, "Lat": 50.2, "Lng": 4.5}
    ])
    d = {
        "Lat": 50.5,
        "Lng": 4.7,
    }
    d = scoring._distance_average(d, pois)
    assert round(d, 0) == 16


def test_calculate_score():
    pois = pd.DataFrame([
        {"Category": "School", "Weight": 12, "Lat": 50.63604, "Lng": 4.78471}
    ])
    d = {
        "Lat": 50.63604,
        "Lng": 4.78471,
        "Attic": "No",
        "Basement": "No",
        "Garage": "No",
        "Office": "No",
        "Bedrooms": 3,
        "SqMeter": 200
    }
    d = scoring.calculate_score(d, pois)
    assert d["dist.Score"] >= 400
    assert d["TotalScore"] >= 600
