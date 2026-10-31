# Planejamento dos dois dashboards

Os arquivos [rascunho_dashboard_1.svg](rascunho_dashboard_1.svg) e [rascunho_dashboard_2.svg](rascunho_dashboard_2.svg) são os dois rascunhos solicitados. São desenhos de planejamento: formas, curvas e números de exemplo não representam capturas do app nem resultados calculados. O aplicativo recalcula os resultados a partir do recorte escolhido.

## Público e pergunta de decisão

O público do painel de gestão é composto por nutricionistas e gestores de cozinhas de serviços de alimentação. A pergunta central é: **em quais recortes há mais desperdício registrado e como a quantidade por refeição varia entre períodos, alimentos e presença de eventos?**

Os filtros aplicam-se às duas abas. A mesma seleção permite investigar as distribuições no laboratório e observar o efeito sobre os indicadores de gestão. A seleção de variáveis define quais quantitativas serão avaliadas no laboratório; o seletor da variável de intervalo determina qual coluna será filtrada pelo slider.

## Dashboard 1 — Laboratório

| Elemento | Objetivo e comportamento |
| --- | --- |
| Seletor de quantitativas | Avaliar refeições servidas, equipe, temperatura, umidade, desperdício anterior e desperdício atual. As seis aparecem inicialmente. |
| Histogramas | Exibir um histograma para cada variável quantitativa selecionada; a quantidade de classes é ajustável. |
| Mapa de calor | Comparar associações com Pearson ou Spearman, em escala fixa de −1 a +1. Uma variável constante ou poucos pares válidos podem tornar um coeficiente indefinido. |
| Dispersão | Investigar a relação entre duas quantitativas e a influência visual de valores extremos. |
| Contexto do recorte | Mostrar quantos registros permanecem após os filtros e deixar claro que correlação não estabelece causalidade. |

Os valores extremos permanecem na base principal, como na EDA. O filtro de intervalo permite avaliar sua influência sem alterar o CSV original. A seleção pelo próprio desperdício pode modificar as associações por construção e deve ser interpretada como análise de sensibilidade.

## Dashboard 2 — Gestão

As cinco métricas referem-se exclusivamente aos registros do recorte:

| Métrica | Definição | Uso |
| --- | --- | --- |
| Desperdício total | Soma de `food_waste_kg`, em kg. | Dimensionar o volume registrado. |
| Refeições servidas | Soma de `meals_served`. | Contextualizar o volume de operação registrado. |
| Desperdício por refeição | `1000 × soma(food_waste_kg) / soma(meals_served)`, em g/refeição. | Comparar intensidade com ponderação pelo número de refeições; denominador positivo. |
| Mediana do desperdício | Mediana de `food_waste_kg`, em kg/registro. | Descrever o centro com menor influência dos maiores valores. |
| Registros acima da meta | `100 × registros com g_por_refeicao > meta / registros com razão válida`. | Acompanhar uma referência hipotética ajustável, inicialmente 150 g/refeição. Não é um padrão oficial. |

A média ponderada de g/refeição não é a média simples das razões de cada registro. Por isso ela pode diferir do indicador por refeição relatado na EDA anterior. O percentual acima da meta usa registros como denominador; não mede a proporção de alimentos desperdiçados. A base não contém a massa total de alimentos preparados.

| Visual | Leitura proposta |
| --- | --- |
| Série mensal de g/refeição | Somar desperdício e refeições dentro de cada mês e calcular a razão ponderada; comparar com a meta ajustável. Não preencher meses sem observações como zero. |
| Barras por categoria do alimento | Comparar total em kg ou intensidade em g/refeição; informar o tamanho dos grupos. Maior volume não implica pior eficiência. |
| Boxplot por presença de evento | Comparar a distribuição de g/refeição entre registros com e sem evento, mantendo os pontos extremos e os tamanhos de grupo visíveis. É uma comparação descritiva. |

## Dados e limites herdados da EDA

A fonte é o [Messy Food Waste Prediction Dataset, no Kaggle](https://www.kaggle.com/competitions/messy-food-waste-prediction-dataset/data). O CSV utilizado está incorporado ao notebook fornecido pelo usuário e contém 911 registros e 12 colunas. O arquivo original deve ser preservado e sua integridade verificada pelo SHA-256 registrado no notebook.

O tratamento padroniza grafias de categorias e converte datas. Os 164 registros sem experiência informada continuam na análise, com rótulo de apresentação “Não informado”; não há imputação de experiência. Os IDs servem para auditoria, sem entrar nas correlações. Os extremos e registros quase repetidos são mantidos, seguindo a EDA original.

Não se pressupõe que cada linha corresponda a uma cozinha distinta, que a coleta seja independente ou que a amostra represente todos os serviços de alimentação. Não são estimadas economia financeira, redução causal de desperdício ou previsões. As comparações são exploratórias e dependem dos filtros.

## Critérios de aceite

- Painel lateral com seletor de variáveis e slider de intervalo funcional.
- Duas abas que carregam o laboratório e a gestão, usando o mesmo recorte.
- Um mapa de calor e um histograma por quantitativa selecionada no laboratório.
- Cinco métricas e pelo menos três visuais de gestão.
- Tratamento explícito de recorte vazio, poucas observações e denominadores inválidos.
- Repositório com notebook, `app.py` e `entregas/`.
- Link real do app publicado no README e teste em janela anônima após a publicação. O resultado desse teste deve ser registrado separadamente, sem confundir teste local com teste de publicação.
