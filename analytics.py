"""Transformações e métricas reproduzíveis da EDA de desperdício alimentar."""

from pathlib import Path

import numpy as np
import pandas as pd


QUANT = [
    "meals_served", "kitchen_staff", "temperature_C", "humidity_percent",
    "past_waste_kg", "food_waste_kg",
]
LABELS = {
    "meals_served": "Refeições servidas",
    "kitchen_staff": "Equipe (pessoas)",
    "temperature_C": "Temperatura (°C)",
    "humidity_percent": "Umidade (%)",
    "past_waste_kg": "Desperdício anterior (kg)",
    "food_waste_kg": "Desperdício atual (kg)",
}
CATEGORY_LABELS = {
    "dairy": "Laticínios", "grains": "Grãos", "meat": "Carne",
    "vegetables": "Vegetais",
}
EXPERIENCE_LABELS = {
    "beginner": "Iniciante", "intermediate": "Intermediário", "expert": "Especialista",
}
SUMMARY_COLUMNS = ["total_waste_kg", "total_meals", "g_per_meal", "records"]


def load_data(path=None):
    """Carrega somente treino; preserva ausências, extremos e todos os registros.

    As regras de limpeza reproduzem a seção 6.1 do notebook original.
    Não há imputação, deduplicação ou arredondamento do conjunto analítico.
    """
    path = Path(path) if path is not None else Path(__file__).parent / "data" / "train.csv"
    df = pd.read_csv(path)
    required = set(QUANT + [
        "ID", "date", "staff_experience", "waste_category", "special_event", "day_of_week",
    ])
    if missing := required.difference(df.columns):
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}")
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="raise")
    for column in ["staff_experience", "waste_category"]:
        df[column] = df[column].astype("string").str.strip().str.casefold().replace("", pd.NA)
    for column in QUANT + ["special_event", "day_of_week"]:
        df[column] = pd.to_numeric(df[column], errors="raise")
    df["evento"] = df["special_event"].map({0: "Sem evento", 1: "Com evento"})
    df["alimento_label"] = df["waste_category"].map(CATEGORY_LABELS)
    df["experiencia_label"] = df["staff_experience"].map(EXPERIENCE_LABELS).fillna("Não informado")
    df["dia_label"] = df["day_of_week"].map(dict(enumerate(["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"])))
    df["g_por_refeicao"] = 1000 * df["food_waste_kg"].div(df["meals_served"].where(df["meals_served"] > 0))
    return df


def filter_data(df, date_range, categories, event, range_variable, value_range):
    """Aplica os mesmos filtros aos dois painéis, com limites inclusivos."""
    if range_variable not in QUANT:
        raise ValueError("Variável de intervalo não quantitativa.")
    if event not in {"Todos", "Sem evento", "Com evento"}:
        raise ValueError("Filtro de evento desconhecido.")
    start, end = (pd.Timestamp(value) for value in date_range)
    lower, upper = value_range
    mask = (
        df["date"].between(start, end)
        & df["alimento_label"].isin(categories)
        & df[range_variable].between(lower, upper)
    )
    if event != "Todos":
        mask &= df["evento"].eq(event)
    return df.loc[mask].copy()


def compute_kpis(df, target_g=150):
    """Calcula a intensidade ponderada: 1.000 × Σ kg / Σ refeições.

    O percentual acima da meta usa registros com razão válida. A meta é
    um cenário escolhido pelo usuário, não uma referência externa de desempenho.
    """
    total_waste = float(df["food_waste_kg"].sum())
    total_meals = float(df["meals_served"].sum())
    valid_ratios = df["g_por_refeicao"].dropna()
    return {
        "records": len(df),
        "total_waste_kg": total_waste,
        "total_meals": total_meals,
        "g_per_meal": 1000 * total_waste / total_meals if total_meals > 0 else np.nan,
        "median_waste_kg": float(df["food_waste_kg"].median()) if len(df) else np.nan,
        "above_target_pct": float(100 * valid_ratios.gt(target_g).mean()) if len(valid_ratios) else np.nan,
    }


def _summarize(df, group_column):
    if df.empty:
        return pd.DataFrame(columns=[group_column] + SUMMARY_COLUMNS)
    grouped = df.groupby(group_column, observed=True).agg(
        total_waste_kg=("food_waste_kg", "sum"),
        total_meals=("meals_served", "sum"),
        records=("food_waste_kg", "size"),
    ).reset_index()
    grouped["g_per_meal"] = 1000 * grouped["total_waste_kg"].div(grouped["total_meals"].where(grouped["total_meals"] > 0))
    return grouped[[group_column] + SUMMARY_COLUMNS]


def monthly_summary(df):
    """Agrupa por mês calendário sem inventar observações nos meses ausentes."""
    monthly = df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
    return _summarize(monthly, "month").sort_values("month").reset_index(drop=True)


def category_summary(df):
    """Retorna totais, intensidade ponderada e tamanho de cada grupo."""
    return _summarize(df, "alimento_label").sort_values("total_waste_kg", ascending=False).reset_index(drop=True)
