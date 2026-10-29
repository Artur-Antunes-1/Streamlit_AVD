"""Regressões da EDA e dos denominadores usados nos painéis."""

from datetime import date
from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics import CATEGORY_LABELS, category_summary, compute_kpis, filter_data, load_data, monthly_summary


@pytest.fixture
def data():
    return load_data()


def test_exact_source_and_cleaning_preserve_eda(data):
    path = Path(__file__).resolve().parents[1] / "data/train.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "c2bedb198bf40cc6793921cdfe0573589923996b3347b3361561b114214b9adf"
    assert len(data) == 911
    assert data.staff_experience.isna().sum() == 164
    assert data.staff_experience.nunique() == 3
    assert data.waste_category.nunique() == 4
    assert data.food_waste_kg.max() > 274  # extremos não são descartados
    assert data.date.min() == pd.Timestamp("2022-01-01")
    assert data.date.max() == pd.Timestamp("2024-09-26")
    assert data.meals_served.corr(data.food_waste_kg, method="spearman") == pytest.approx(.5577, abs=.0001)
    assert data.food_waste_kg.mean() == pytest.approx(44.84, abs=.01)


def test_kpis_use_weighted_ratio_and_strict_target(data):
    sample = data.iloc[:2].copy()
    sample["food_waste_kg"] = [1., 9.]
    sample["meals_served"] = [10., 30.]
    sample["g_por_refeicao"] = [100., 300.]
    result = compute_kpis(sample, target_g=100)
    assert result["g_per_meal"] == 250  # média simples daria 200
    assert result["above_target_pct"] == 50  # igualdade não excede meta
    assert result["median_waste_kg"] == 5
    assert result["total_meals"] == 40


def test_filters_are_inclusive_and_combined(data):
    row = data.iloc[0]
    result = filter_data(data, (row.date.date(), row.date.date()), [row.alimento_label], row.evento,
                         "food_waste_kg", (row.food_waste_kg, row.food_waste_kg))
    assert row.ID in result.ID.values
    assert (result.date == row.date).all()
    assert result.alimento_label.eq(row.alimento_label).all()
    assert result.evento.eq(row.evento).all()
    full = filter_data(data, (date(2022, 1, 1), date(2024, 9, 26)), list(CATEGORY_LABELS.values()),
                       "Todos", "food_waste_kg", (data.food_waste_kg.min(), data.food_waste_kg.max()))
    assert len(full) == 911
    assert len(data) == 911  # nenhum filtro modifica base original


def test_empty_selection_and_undefined_denominators(data):
    empty = filter_data(data, (data.date.min(), data.date.max()), [], "Todos", "meals_served", (0, 10000))
    result = compute_kpis(empty)
    assert result["records"] == 0
    assert result["total_waste_kg"] == 0
    assert np.isnan(result["g_per_meal"])
    assert np.isnan(result["above_target_pct"])
    assert monthly_summary(empty).empty
    assert category_summary(empty).empty
    sample = data.iloc[:1].copy()
    sample["meals_served"] = 0
    sample["g_por_refeicao"] = np.nan
    assert np.isnan(compute_kpis(sample)["g_per_meal"])
    assert np.isnan(compute_kpis(sample)["above_target_pct"])


@pytest.mark.parametrize("summarizer", [monthly_summary, category_summary])
def test_grouped_totals_reconcile_and_ratios_are_weighted(data, summarizer):
    groups = summarizer(data)
    kpis = compute_kpis(data)
    assert groups.total_waste_kg.sum() == pytest.approx(kpis["total_waste_kg"])
    assert groups.total_meals.sum() == kpis["total_meals"]
    assert groups.records.sum() == 911
    assert np.allclose(groups.g_per_meal, 1000 * groups.total_waste_kg / groups.total_meals)
    assert np.average(groups.g_per_meal, weights=groups.total_meals) == pytest.approx(kpis["g_per_meal"])
