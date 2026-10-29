# 🌿 Mesa Clara — Desperdício alimentar

Aplicação Streamlit desenvolvida a partir da EDA do **Messy Food Waste Prediction Dataset**, com dois dashboards em abas. O painel de gestão foi pensado para **nutricionistas e gestores de refeitórios**.

**App publicado:** pendente de publicação no Streamlit Community Cloud. Substitua esta linha pelo endereço real após o deploy.

**Repositório:** [Artur-Antunes-1/Streamlit_AVD](https://github.com/Artur-Antunes-1/Streamlit_AVD). Mantido **privado** por solicitação do autor; a visibilidade pública exigida na entrega final permanece pendente.

## O que está pronto

- **Laboratório:** mapa de correlação Pearson/Spearman, seis histogramas inicialmente selecionados, dispersão interativa e estatísticas descritivas.
- **Gestão:** cinco KPIs e três visuais: evolução mensal de g/refeição, barras por categoria e boxplot por evento.
- **Painel lateral:** seleção de quantitativas, variável de filtro, intervalo numérico, período, categorias, evento e restauração dos filtros.
- **Entregas:** dois rascunhos em SVG/JPG, planejamento, justificativas das métricas e relatório de testes locais.
- **Reprodução:** notebook original com seção de exportação acrescentada, CSV original e tratado, testes dos dados, widgets e navegador.

## Executar localmente

Use **Python 3.12**, a mesma versão utilizada nos testes.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra <http://localhost:8501>. O CSV já está em `data/`; não há necessidade de baixar os dados do Kaggle, configurar chaves ou editar caminhos absolutos.

## Métricas e interpretação

| KPI | Definição |
| --- | --- |
| Desperdício total | Soma de `food_waste_kg`, em kg |
| Refeições servidas | Soma de `meals_served` |
| Gramas por refeição | `1000 × soma(food_waste_kg) / soma(meals_served)` |
| Mediana por registro | Mediana de `food_waste_kg` |
| Registros acima da meta | Percentual de razões individuais válidas estritamente acima da referência escolhida |

Na base completa: **40.851,7 kg**, **341.994 refeições**, **119,5 g/refeição**, mediana **41,1 kg/registro** e **39,5% dos registros acima de 150 g/refeição**. Esses totais descrevem os registros, incluindo os quase repetidos mantidos na EDA; não representam uma estimativa validada de desperdício de uma organização real.

O KPI de g/refeição é ponderado pelo número de refeições. Ele difere da média simples das razões por registro usada em uma comparação do notebook. A meta inicial de 150 g/refeição é **hipotética e ajustável**, sem origem em norma técnica. O percentual acima da meta usa registros como denominador; não é percentual de comida desperdiçada, pois não há massa preparada na base.

Os extremos e as 164 ausências em experiência foram preservados. As categorias foram normalizadas. As associações não estabelecem causalidade; coleta e amostragem não estão suficientemente documentadas para generalização. Os filtros, inclusive pelo próprio desperdício, podem alterar as relações observadas.

As justificativas completas estão em [entregas/justificativa-metricas.md](entregas/justificativa-metricas.md).

## Organização do repositório

```text
.
├── app.py
├── analytics.py
├── requirements.txt
├── requirements-dev.txt
├── requirements-eda.txt
├── .streamlit/config.toml
├── data/
│   ├── train.csv
│   ├── eda_tratada.csv
│   └── README.md
├── notebooks/01_eda_original.ipynb
├── entregas/
│   ├── rascunho-dashboard1.jpg
│   ├── rascunho-dashboard2.jpg
│   ├── rascunho_dashboard_1.svg
│   ├── rascunho_dashboard_2.svg
│   ├── planejamento.md
│   ├── justificativa-metricas.md
│   ├── relatorio-testes.md
│   └── capturas e evidências locais
├── prompts/
│   ├── declaracao-uso-ia.md
│   └── registro_ia.md
├── scripts/test_browser.py
└── tests/
    ├── test_analytics.py
    └── test_app.py
```

## Rascunhos e origem da EDA

- [Rascunho 1 — laboratório](entregas/rascunho-dashboard1.jpg)
- [Rascunho 2 — gestão](entregas/rascunho-dashboard2.jpg)
- [Planejamento dos painéis](entregas/planejamento.md)
- [Notebook da EDA](notebooks/01_eda_original.ipynb)
- [Fonte no Kaggle](https://www.kaggle.com/competitions/messy-food-waste-prediction-dataset/data)

Os rascunhos são desenhos ilustrativos, distintos das capturas do app. O notebook recebido foi preservado com os resultados executados; apenas uma seção final foi acrescentada para exportar os dados original e tratado. Para reexecutá-lo, instale `requirements-eda.txt`, abra o Jupyter/Colab e execute as células em ordem. O CSV também está incorporado no notebook; os dois arquivos podem ser exportados novamente pela seção 14. Consulte a origem e o SHA-256 em [data/README.md](data/README.md).

## Testes reproduzíveis

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
# Com o servidor Streamlit rodando em outro terminal:
python -m playwright install chromium
python scripts/test_browser.py --url http://localhost:8501
# Se o Chromium já estiver instalado:
python scripts/test_browser.py --url http://localhost:8501 --chromium /caminho/do/chromium
```

O teste de navegador cria um contexto isolado, sem sessão persistida. As evidências e o escopo efetivamente executado estão em [entregas/relatorio-testes.md](entregas/relatorio-testes.md). **Testes locais não comprovam o funcionamento de uma publicação.**

## Publicar e concluir a entrega

1. O projeto está preparado para o repositório [Streamlit_AVD](https://github.com/Artur-Antunes-1/Streamlit_AVD), mantido privado por enquanto. Para a entrega final, altere a visibilidade para **público** nas configurações do GitHub. Ao enviar os arquivos, inclua os arquivos ocultos de configuração. `app.py` e `requirements.txt` devem ficar na raiz. Não envie o ZIP como único arquivo. Não inclua `.venv/`, caches, `.env` ou `secrets.toml`.
2. Acesse <https://streamlit.io/cloud> com a conta associada ao GitHub. Escolha **Create app → Deploy a public app from GitHub**.
3. Selecione o repositório, a branch `main` e **Main file path: `app.py`**. Nas configurações avançadas, escolha **Python 3.12**. Publique o app com acesso público.
4. Copie o endereço gerado, terminado em `.streamlit.app`, para a linha **App publicado** no início deste README. Confira a visibilidade do repositório e faça commit/push da alteração no README.
5. Abra o endereço publicado em uma janela anônima, execute o checklist abaixo e registre os resultados. O teste automatizado também aceita `--url https://SEU-APP.streamlit.app`; use o endereço real, não esse exemplo.

Se o app apresentar `ModuleNotFoundError`, confira `requirements.txt` e Python 3.12. Se o CSV não for encontrado, confirme que `data/train.csv` foi enviado e que o caminho principal é `app.py`. Uma hibernação do plano gratuito pode exigir aguardar a inicialização.

### Checklist após publicação — ainda pendente

- [ ] Repositório público acessível sem login, contendo notebook, dados, código, `entregas/` e `prompts/`.
- [ ] Endereço real do app adicionado no início deste README.
- [ ] App publicado aberto em janela anônima, sem autenticação.
- [ ] Duas abas carregadas com gráficos e métricas.
- [ ] Todos os widgets alterados e resposta dos gráficos/indicadores conferida.
- [ ] Seleções vazias e restauração dos filtros conferidas.
- [ ] Download do resumo mensal conferido.
- [ ] Ausência de informações pessoais, segredos e credenciais conferida na publicação e no repositório.
- [ ] Dois rascunhos presentes em `entregas/`, com métricas justificadas.
- [ ] Revisão humana do público, das interpretações e da declaração de uso de IA concluída.

## Uso de IA

Foi utilizado um assistente para desenvolver código, documentos, desenhos e testes. Consulte a [declaração](prompts/declaracao-uso-ia.md) e o [registro de orientações](prompts/registro_ia.md). Não foi fabricado histórico de commits das aulas anteriores; o material deve ser revisado pelo autor antes da entrega acadêmica.
