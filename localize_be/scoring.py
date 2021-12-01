from functools import lru_cache
from math import cos, radians
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


@lru_cache
def _distance_score_predictor():
    reg = LinearRegression()
    reg.fit(np.array([0, 10, 14, 16]).reshape(-1, 1), [400, 300, 100, 0])
    return reg


@lru_cache
def _size_score_predictor():
    reg = LinearRegression()
    reg.fit(np.array([0, 250, 350]).reshape(-1, 1), [0, 250, 270])
    return reg


@lru_cache
def _bedroom_score_predictor():
    reg = LinearRegression()
    # 4 rooms is pretty much a minimum, after that it's just a bonus
    reg.fit(np.array([0, 3, 4, 5]).reshape(-1, 1), [0, 0, 100, 120])
    return reg


def _distance_average(d: Dict, pois: pd.DataFrame):
    lat1 = radians(d["Lat"])
    lat2 = np.radians(pois.Lat)
    lng1 = radians(d["Lng"])
    lng2 = np.radians(pois.Lng)
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = np.sin(dlat / 2) ** 2 + cos(lat1) * np.cos(lat2) * np.sin(dlng / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distances = 6373.0 * c
    # distances = np.sqrt((d["Lat"] - pois.Lat) ** 2 + (d["Lng"] - pois.Lng) ** 2)
    return np.sum(distances * pois.Weight) / np.sum(pois.Weight)


def calculate_score(details: Dict, pois: pd.DataFrame):
    """
    Complete details with score fields
    """
    details["dist.Total"] = _distance_average(details, pois)
    details["dist.Score"] = _distance_score_predictor().predict([[details["dist.Total"]]])[0]
    details["size.Score"] = _size_score_predictor().predict([[details["SqMeter"]]])[0]
    bedrooms = details["Bedrooms"]
    if details["Office"] == "Yes":
        bedrooms += 1
    bedroom_score = _bedroom_score_predictor().predict([[bedrooms]])[0]
    features = {
        "Attic": 15,
        "Basement": 40,
        "Garage": 30
    }
    feat_score = sum([w for n, w in features.items() if details[n] == "Yes"])
    details["TotalScore"] = feat_score + bedroom_score + details["size.Score"] + details["dist.Score"]
    return details
