# [IA] ChatGPT/Codex – implementação deste arquivo: testes de integração dos dashboards.
"""Integração dos widgets com os dois painéis usando o runtime do Streamlit."""
import base64
from datetime import date
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analytics import LABELS, QUANT, load_data


@pytest.fixture
def app():
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()


def assert_healthy(app):
    assert not app.exception, [element.message for element in app.exception]
    assert len(app.tabs) == 2


def chart(app, name):
    item = next(item for item in app.get("plotly_chart") if item.proto.id.endswith("-" + name))
    return json.loads(item.proto.spec)


def values(payload):
    """Aceita tanto listas JSON quanto arrays binários do Plotly 6."""
    if isinstance(payload, dict) and "bdata" in payload:
        result = np.frombuffer(base64.b64decode(payload["bdata"]), dtype=payload["dtype"])
        if "shape" in payload:
            result = result.reshape(tuple(int(n) for n in payload["shape"].split(",")))
        return result
    return np.asarray(payload)


def metric_value(app, label):
    raw = next(metric.value for metric in app.metric if metric.label == label)
    return float(raw.split()[0].replace("%", "").replace(".", "").replace(",", "."))


def test_default_dashboards_match_source_and_required_visuals(app):
    assert_healthy(app)
    assert [tab.label for tab in app.tabs] == ["01 · Laboratório de análise", "02 · Gestão do refeitório"]
    assert len(app.get("plotly_chart")) == 11
    assert len(app.metric) == 5
    assert metric_value(app, "Desperdício total") == 40851.7
    assert metric_value(app, "Refeições servidas") == 341994
    assert metric_value(app, "Gramas por refeição") == 119.5
    assert len(values(chart(app, "heatmap")["data"][0]["z"])) == 6
    for variable in QUANT:
        histogram = chart(app, "hist_" + variable)["data"][0]
        assert histogram["type"] == "histogram"
        assert len(values(histogram["x"])) == 911
    assert chart(app, "categories")["data"][0]["type"] == "bar"
    assert chart(app, "events")["data"][0]["type"] == "box"


def test_laboratory_controls_change_correlations_bins_and_scatter(app):
    spearman = values(chart(app, "heatmap")["data"][0]["z"])[0, 5]
    app.radio(key="corr_method").set_value("Pearson")
    app.slider(key="hist_bins").set_value(40)
    app.selectbox(key="scatter_x").set_value("past_waste_kg")
    app.selectbox(key="scatter_y").set_value("temperature_C")
    app.run()
    assert_healthy(app)
    pearson = values(chart(app, "heatmap")["data"][0]["z"])[0, 5]
    assert spearman == pytest.approx(.5577, abs=.0001)
    assert pearson == pytest.approx(.8521, abs=.0001)
    for variable in QUANT:
        assert chart(app, "hist_" + variable)["data"][0]["nbinsx"] == 40
    scatter = chart(app, "scatter")
    assert scatter["layout"]["xaxis"]["title"]["text"] == LABELS["past_waste_kg"]
    assert scatter["layout"]["yaxis"]["title"]["text"] == LABELS["temperature_C"]


def test_sidebar_numeric_range_changes_both_dashboards(app):
    app.selectbox(key="filter_range_variable").set_value("meals_served").run()
    app.slider(key="filter_interval_meals_served").set_value((150., 400.)).run()
    assert_healthy(app)
    expected = load_data().loc[lambda df: df.meals_served.between(150, 400)]
    assert 0 < len(expected) < 911
    assert len(values(chart(app, "hist_food_waste_kg")["data"][0]["x"])) == len(expected)
    assert metric_value(app, "Refeições servidas") == expected.meals_served.sum()
    assert metric_value(app, "Desperdício total") == pytest.approx(expected.food_waste_kg.sum(), abs=.051)


def test_sidebar_date_category_and_event_filters_combine_then_reset(app):
    app.multiselect(key="filter_variables").set_value(["food_waste_kg"])
    app.slider(key="filter_dates").set_value((date(2023, 1, 1), date(2023, 12, 31)))
    app.multiselect(key="filter_categories").set_value(["Carne"])
    app.radio(key="filter_event").set_value("Com evento")
    app.run()
    assert_healthy(app)
    data = load_data()
    expected = data.loc[data.date.between("2023-01-01", "2023-12-31") & data.alimento_label.eq("Carne") & data.special_event.eq(1)]
    assert len(expected) > 0
    assert len(values(chart(app, "hist_food_waste_kg")["data"][0]["x"])) == len(expected)
    assert metric_value(app, "Refeições servidas") == expected.meals_served.sum()
    assert {trace["name"] for trace in chart(app, "events")["data"]} == {"Com evento"}
    assert list(chart(app, "categories")["data"][0]["y"]) == ["Carne"]
    app.button[0].click().run()
    assert_healthy(app)
    assert len(values(chart(app, "hist_food_waste_kg")["data"][0]["x"])) == 911
    assert app.radio(key="filter_event").value == "Todos"
    assert len(app.multiselect(key="filter_categories").value) == 4
    assert app.multiselect(key="filter_variables").value == QUANT
    assert app.selectbox(key="filter_range_variable").value == "food_waste_kg"
    assert app.slider(key="filter_dates").value == (date(2022, 1, 1), date(2024, 9, 26))


def test_management_goal_and_category_mode_change_their_outputs(app):
    original = metric_value(app, "Registros acima da meta")
    app.slider(key="target_g").set_value(250)
    app.radio(key="category_mode").set_value("Gramas por refeição")
    app.run()
    assert_healthy(app)
    assert metric_value(app, "Registros acima da meta") < original
    assert metric_value(app, "Desperdício total") == 40851.7
    assert metric_value(app, "Gramas por refeição") == 119.5
    assert chart(app, "monthly")["layout"]["shapes"][0]["y0"] == 250
    assert chart(app, "events")["layout"]["shapes"][0]["y0"] == 250
    assert chart(app, "categories")["layout"]["xaxis"]["title"]["text"] == "Desperdício (g/refeição)"


def test_variable_selection_single_variable_and_empty_variables_are_graceful(app):
    app.multiselect(key="filter_variables").set_value(["food_waste_kg"]).run()
    assert_healthy(app)
    assert len(app.get("plotly_chart")) == 5  # histograma + dispersão + três visuais gerenciais
    assert any("duas variáveis" in item.value for item in app.info)
    assert len(app.metric) == 5
    app.multiselect(key="filter_variables").set_value([]).run()
    assert_healthy(app)
    assert len(app.get("plotly_chart")) == 3
    assert any("pelo menos uma variável" in item.value for item in app.info)
    assert len(app.metric) == 5


def test_empty_records_and_constant_variable_do_not_crash(app):
    app.multiselect(key="filter_categories").set_value([]).run()
    assert_healthy(app)
    assert len(app.metric) == 0
    assert len(app.get("plotly_chart")) == 0
    assert sum("Nenhum registro" in item.value for item in app.info) == 2
    app.button[0].click().run()
    app.selectbox(key="filter_range_variable").set_value("kitchen_staff").run()
    app.slider(key="filter_interval_kitchen_staff").set_value((10., 10.)).run()
    assert_healthy(app)
    matrix = values(chart(app, "heatmap")["data"][0]["z"])
    assert np.isnan(matrix[1]).all()  # uma variável constante não tem correlação definida
    assert len(app.metric) == 5
    assert 0 < len(values(chart(app, "hist_food_waste_kg")["data"][0]["x"])) < 911
