# [IA] ChatGPT/Codex – implementação deste arquivo: interface, filtros, gráficos e indicadores.
"""Dois dashboards de desperdício alimentar, baseados na EDA da atividade."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import (
    LABELS, QUANT, category_summary, compute_kpis, filter_data,
    load_data, monthly_summary,
)

ROOT = Path(__file__).resolve().parent
GREEN, LIGHT, AMBER = "#17624a", "#a9c9b8", "#c47a29"
EVENT_COLORS = {"Sem evento": GREEN, "Com evento": AMBER}
st.set_page_config(page_title="Mesa Clara · Desperdício alimentar", page_icon="🌿", layout="wide")
st.markdown("""
<style>
 .block-container {max-width:1480px; padding-top:3.5rem; padding-bottom:2rem}
 [data-testid="stSidebar"] {border-right:1px solid #dedfd5}
 h1,h2,h3 {letter-spacing:-.035em}
 .eyebrow {color:#17624a; font-size:.78rem; font-weight:700; letter-spacing:.16em; margin-bottom:.5rem}
 .intro {color:#5b665d; font-size:1.05rem; max-width:780px; margin-bottom:1.5rem}
 [data-testid="stMetric"] {background:#fffefa; border:1px solid #dfe4d9; border-radius:12px; padding:16px}
 [data-testid="stMetricLabel"] {font-size:.85rem}
 [data-testid="stMetricValue"] {font-size:1.65rem}
 button[data-baseweb="tab"] {font-size:1rem; padding-left:1.1rem; padding-right:1.1rem}
 .footnote {font-size:.8rem; color:#647067; border-top:1px solid #dfe4d9; padding-top:1rem; margin-top:1.5rem}
</style>
""", unsafe_allow_html=True)


def br(value, decimals=0):
    if pd.isna(value):
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data(show_spinner=False)
def get_data():
    return load_data(ROOT / "data" / "train.csv")


def chart(fig, key):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif", color="#283e32"),
        margin=dict(l=12, r=18, t=32, b=20),
        legend_title_text="", separators=",.",
    )
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor="#e3e8df", automargin=True)
    st.plotly_chart(fig, use_container_width=True, key=key, config={"displaylogo": False})


def filter_defaults(data):
    defaults = {
        "filter_variables": QUANT.copy(),
        "filter_range_variable": "food_waste_kg",
        "filter_dates": (data.date.min().date(), data.date.max().date()),
        "filter_categories": sorted(data.alimento_label.unique()),
        "filter_event": "Todos",
    }
    for variable in QUANT:
        defaults[f"filter_interval_{variable}"] = (
            float(data[variable].min()), float(data[variable].max()),
        )
    return defaults


def reset_filters():
    # Atribuir os padrões também sincroniza os valores exibidos nos widgets.
    st.session_state.update(filter_defaults(get_data()))


def laboratory(data, variables):
    st.subheader("Investigue a distribuição. Compare as relações.")
    st.caption("Os filtros laterais se aplicam aos dois painéis. Os gráficos usam somente os registros do recorte.")
    if data.empty:
        st.info("Nenhum registro neste recorte. Amplie os intervalos ou restaure os filtros.")
        return
    if not variables:
        st.info("Selecione pelo menos uma variável quantitativa no painel lateral.")
        return

    left, right = st.columns([1, 1])
    with left:
        method = st.radio("Método de correlação", ["Spearman", "Pearson"], horizontal=True, key="corr_method")
    with right:
        bins = st.slider("Número de classes dos histogramas", 5, 60, 25, key="hist_bins")
    st.markdown("#### Mapa de correlação")
    if len(variables) < 2 or len(data) < 3:
        st.info("Selecione ao menos duas variáveis e um recorte com três ou mais registros para a correlação.")
    else:
        corr = data[variables].corr(method=method.lower())
        counts = data[variables].notna().astype(int).T.dot(data[variables].notna().astype(int))
        heatmap = go.Figure(go.Heatmap(
            z=corr.to_numpy(), x=[LABELS[v] for v in variables], y=[LABELS[v] for v in variables],
            zmin=-1, zmax=1, zmid=0, colorscale=[[0, "#bc6b45"], [.5, "#f6f5ee"], [1, GREEN]],
            text=corr.round(2).to_numpy(), texttemplate="%{text:.2f}", customdata=counts.to_numpy(),
            hovertemplate="%{y} × %{x}<br>Correlação: %{z:.3f}<br>Pares válidos: %{customdata}<extra></extra>",
            colorbar=dict(title="r" if method == "Pearson" else "ρ"),
        ))
        heatmap.update_layout(height=470)
        heatmap.update_yaxes(autorange="reversed")
        chart(heatmap, "heatmap")
        st.caption("Escala fixa de −1 a +1. Células vazias indicam correlação indefinida (ex.: variável constante). "
                   "Spearman compara postos; Pearson mede associação linear e é sensível a extremos. Correlação não implica causalidade.")

    st.markdown("#### Distribuição de cada variável")
    columns = st.columns(2)
    for i, variable in enumerate(variables):
        with columns[i % 2]:
            st.markdown(f"**{LABELS[variable]}**")
            values = data[variable].dropna()
            st.caption(f"n = {br(len(values))} · Média {br(values.mean(), 2)} · Mediana {br(values.median(), 2)}")
            fig = px.histogram(data, x=variable, nbins=bins, labels={variable: LABELS[variable]},
                               color_discrete_sequence=[GREEN])
            fig.update_layout(height=275, bargap=.06, yaxis_title="Registros")
            chart(fig, f"hist_{variable}")

    st.markdown("#### Relação entre duas variáveis")
    c1, c2 = st.columns(2)
    x = c1.selectbox("Eixo horizontal", variables, format_func=LABELS.get, key="scatter_x")
    y = c2.selectbox("Eixo vertical", variables, index=len(variables) - 1, format_func=LABELS.get, key="scatter_y")
    scatter = px.scatter(data, x=x, y=y, color="evento", color_discrete_map=EVENT_COLORS,
                         labels={**LABELS, "evento": "Evento"}, opacity=.65)
    scatter.update_layout(height=380)
    chart(scatter, "scatter")
    with st.expander("Estatísticas descritivas do recorte"):
        summary = data[variables].describe().T.rename(index=LABELS, columns={
            "count": "Registros", "mean": "Média", "std": "Desvio padrão", "min": "Mínimo",
            "25%": "Q1", "50%": "Mediana", "75%": "Q3", "max": "Máximo",
        })
        st.dataframe(summary.round(2), width="stretch")


def management(data):
    st.subheader("Uma visão para planejar a cozinha")
    st.caption("Público-alvo: nutricionistas e gestores de refeitórios. Compare volume, intensidade e situações operacionais.")
    target = st.slider("Meta exploratória de desperdício (g/refeição)", 50, 300, 150, 5, key="target_g",
                       help="Referência ajustável para simulação. Não é um padrão técnico nem uma meta validada pela base.")
    if data.empty:
        st.info("Nenhum registro neste recorte. Amplie os intervalos ou restaure os filtros.")
        return
    k = compute_kpis(data, target)
    cols = st.columns(5)
    cols[0].metric("Desperdício total", br(k["total_waste_kg"], 1) + " kg", help="Soma do desperdício registrado no recorte.")
    cols[1].metric("Refeições servidas", br(k["total_meals"]), help="Soma das refeições registradas no recorte.")
    cols[2].metric("Gramas por refeição", br(k["g_per_meal"], 1) + " g", help="1.000 × soma do desperdício em kg ÷ soma das refeições. Razão ponderada pelo volume de refeições.")
    cols[3].metric("Mediana por registro", br(k["median_waste_kg"], 1) + " kg", help="Valor central do desperdício nos registros selecionados.")
    cols[4].metric("Registros acima da meta", br(k["above_target_pct"], 1) + "%", help="Percentual de registros com refeições positivas cujo desperdício em g/refeição supera a meta. Não é percentual de comida desperdiçada.")
    st.caption(f"{br(k['records'])} registros avaliados · Meta de referência: {target} g/refeição · Não há informação sobre massa preparada ou custo.")

    st.markdown("#### A intensidade muda ao longo dos meses?")
    monthly = monthly_summary(data)
    fig = px.line(monthly, x="month", y="g_per_meal", markers=True,
                  labels={"month": "Mês", "g_per_meal": "Desperdício (g/refeição)", "records": "Registros"},
                  hover_data={"records": True}, color_discrete_sequence=[GREEN])
    fig.add_hline(y=target, line_dash="dash", line_color=AMBER,
                  annotation_text=f"Referência: {target} g/refeição", annotation_position="top left")
    fig.update_layout(height=330)
    fig.update_xaxes(tickformat="%m/%Y")
    chart(fig, "monthly")
    st.caption("Razão ponderada calculada em cada mês, apenas com registros presentes no recorte. "
               "A cobertura é irregular: meses não equivalem a períodos completos de operação.")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Onde concentrar a investigação?")
        mode = st.radio("Comparar categorias por", ["Volume total (kg)", "Gramas por refeição"], horizontal=True, key="category_mode")
        metric = "total_waste_kg" if mode == "Volume total (kg)" else "g_per_meal"
        category = category_summary(data).sort_values(metric, ascending=True)
        label = "Desperdício total (kg)" if metric == "total_waste_kg" else "Desperdício (g/refeição)"
        fig = px.bar(category, x=metric, y="alimento_label", orientation="h", text_auto=".1f",
                     labels={metric: label, "alimento_label": "Categoria", "records": "Registros"},
                     hover_data={"records": True}, color_discrete_sequence=[GREEN])
        fig.update_layout(height=350)
        chart(fig, "categories")
        st.caption("O total depende do tamanho de cada grupo. Use g/refeição para considerar o volume servido. "
                   "A categoria identifica o registro; não informa a composição de todo o desperdício.")
    with right:
        st.markdown("#### Eventos pedem atenção extra?")
        fig = px.box(data, x="evento", y="g_por_refeicao", color="evento", points="outliers",
                     color_discrete_map=EVENT_COLORS, category_orders={"evento": ["Sem evento", "Com evento"]},
                     labels={"evento": "", "g_por_refeicao": "Desperdício (g/refeição)"})
        fig.add_hline(y=target, line_dash="dash", line_color=AMBER)
        fig.update_layout(height=398, showlegend=False)
        chart(fig, "events")
        counts = data.groupby("evento", observed=True).size()
        st.caption(" · ".join(f"{event}: {br(n)} registros" for event, n in counts.items()) +
                   ". A comparação é descritiva; não demonstra que o evento cause a diferença.")

    with st.expander("Consultar e baixar o resumo mensal"):
        output = monthly.rename(columns={"month": "Mês", "records": "Registros", "total_waste_kg": "Desperdício (kg)",
                                        "total_meals": "Refeições", "g_per_meal": "g/refeição"})
        st.dataframe(output, hide_index=True, width="stretch")
        st.download_button("Baixar resumo mensal (CSV)", output.to_csv(index=False, sep=";", decimal=","),
                           "resumo_mensal.csv", "text/csv", key="download_monthly")


def main():
    try:
        data = get_data()
    except (OSError, ValueError):
        st.error("Não foi possível carregar a base local. Confira data/train.csv e as instruções do README.")
        st.stop()
    for key, value in filter_defaults(data).items():
        st.session_state.setdefault(key, value)
    with st.sidebar:
        st.markdown("### 🌿 Mesa Clara")
        st.caption("DESPERDÍCIO ALIMENTAR · EDA")
        st.markdown("#### Seu recorte")
        st.button("Restaurar filtros", on_click=reset_filters, width="stretch")
        variables = st.multiselect("Variáveis quantitativas avaliadas", QUANT,
                                   format_func=LABELS.get, key="filter_variables")
        variable = st.selectbox("Variável do filtro de intervalo", QUANT, index=None,
                                format_func=LABELS.get, key="filter_range_variable")
        low, high = float(data[variable].min()), float(data[variable].max())
        interval = st.slider("Intervalo incluído na análise", low, high,
                             key=f"filter_interval_{variable}", format="%.2f")
        date_min, date_max = data.date.min().date(), data.date.max().date()
        dates = st.slider("Período dos registros", date_min, date_max,
                          format="DD/MM/YYYY", key="filter_dates")
        categories = st.multiselect("Categorias de alimento", sorted(data.alimento_label.unique()),
                                     key="filter_categories")
        event = st.radio("Evento especial", ["Todos", "Sem evento", "Com evento"], key="filter_event")
        st.caption("Extremos são mantidos por padrão. Ajuste o intervalo para investigar sua influência.")

    selected = filter_data(data, dates, categories, event, variable, interval)
    st.markdown('<div class="eyebrow">MESA CLARA / INTELIGÊNCIA NA COZINHA</div>', unsafe_allow_html=True)
    st.title("Menos desperdício. Mais clareza.")
    st.markdown('<p class="intro">Explore os dados de desperdício alimentar e transforme perguntas em decisões de planejamento.</p>', unsafe_allow_html=True)
    st.caption(f"BASE DE ESTUDO · {br(len(selected))} de {br(len(data))} registros selecionados "
               f"({br(100 * len(selected) / len(data), 1)}%) · {dates[0]:%d/%m/%Y} a {dates[1]:%d/%m/%Y}")
    lab, operations = st.tabs(["01 · Laboratório de análise", "02 · Gestão do refeitório"])
    with lab:
        laboratory(selected, variables)
    with operations:
        management(selected)
    with st.expander("Fonte, metodologia e limites dos dados"):
        st.markdown("""
        **Fonte:** [Messy Food Waste Prediction Dataset · Kaggle](https://www.kaggle.com/competitions/messy-food-waste-prediction-dataset/data),
        exclusivamente `train.csv` incorporado no notebook da EDA (911 registros, 12 colunas).

        **Tratamento:** datas convertidas e categorias padronizadas. Os 164 registros sem experiência da equipe
        permanecem na base; ausências não foram imputadas. Valores extremos e registros quase repetidos foram
        mantidos, seguindo a EDA. ID, data e códigos qualitativos não entram na matriz de correlação.

        **Interpretação:** g/refeição é uma razão de massas por refeições, não uma porcentagem do alimento preparado.
        A EDA compara médias das razões por registro; o KPI gerencial usa a razão entre os totais para ponderar pelo
        volume servido. A meta é uma simulação ajustável. Não foram estimados custos, economias ou efeitos causais.
        A coleta e a amostragem não estão documentadas o suficiente para generalizar os resultados.

        **Privacidade:** o app apresenta dados operacionais da base de estudo e resumos agregados. Não solicita login,
        não faz upload, não usa serviços externos de análise e não contém credenciais. IDs não são exibidos.
        """)
    st.markdown('<div class="footnote">Projeto acadêmico · Análise exploratória, sem previsão ou inferência causal · '
                'Dados locais, sem autenticação no Kaggle</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
