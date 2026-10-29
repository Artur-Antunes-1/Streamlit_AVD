# Justificativa das métricas do dashboard de gestão

**Público-alvo:** nutricionistas e gestores de cozinhas de serviços de alimentação. As métricas apoiam a leitura de volume registrado, intensidade por refeição e frequência de registros acima de uma referência operacional hipotética. Todas são recalculadas após os filtros; a unidade de observação é o registro do dataset, sem supor que cada linha represente uma cozinha distinta.

## 1. Desperdício total — kg

- **Variável utilizada:** `food_waste_kg`.
- **O que mede e fórmula:** volume de desperdício registrado no recorte, calculado por `soma(food_waste_kg)`.
- **Por que foi escolhida:** dimensiona a quantidade acumulada que acompanha as análises de distribuição da EDA.
- **Público que atende:** nutricionistas e gestores que precisam compreender o volume registrado para organizar uma investigação operacional.
- **Decisão apoiada:** escolher períodos ou categorias com maior volume para examinar práticas de preparo, armazenamento e serviço, usando os demais visuais para contextualizar.
- **O que comunica:** “quantos quilogramas de desperdício constam nos registros selecionados”. Não mede eficiência isoladamente: um recorte com mais refeições ou registros pode somar mais desperdício.

## 2. Refeições servidas — quantidade

- **Variável utilizada:** `meals_served`.
- **O que mede e fórmula:** volume de refeições registrado no recorte, por `soma(meals_served)`.
- **Por que foi escolhida:** fornece o denominador operacional necessário para interpretar o volume de desperdício.
- **Público que atende:** responsáveis pelo planejamento de serviços de alimentação e pelo acompanhamento do volume de atendimento.
- **Decisão apoiada:** avaliar se diferenças de desperdício entre recortes acompanham diferenças na quantidade de refeições antes de comparar seu desempenho.
- **O que comunica:** “quantas refeições constam nos registros selecionados”. Não indica pessoas únicas, refeições de cozinhas distintas ou atendimentos independentes; a EDA identificou registros quase repetidos.

## 3. Desperdício ponderado por refeição — g/refeição

- **Variáveis utilizadas:** `food_waste_kg` e `meals_served`.
- **O que mede e fórmula:** intensidade agregada, por `1000 × soma(food_waste_kg) / soma(meals_served)`, com denominador positivo. O fator 1000 converte kg em g.
- **Por que foi escolhida:** permite comparar o desperdício em relação ao volume de refeições. Cada refeição tem o mesmo peso no indicador agregado.
- **Público que atende:** nutricionistas e gestores que comparam períodos e categorias com diferentes volumes de operação.
- **Decisão apoiada:** identificar recortes que merecem investigação por apresentarem maior intensidade, além do volume total, e acompanhar sua evolução mensal.
- **O que comunica:** “quantos gramas de desperdício correspondem, em média ponderada, a cada refeição registrada”. Não mede a parcela percentual de comida desperdiçada, pois não há massa total preparada. Também não é a média simples das razões de cada registro usada em uma comparação da EDA original.

## 4. Mediana do desperdício — kg/registro

- **Variável utilizada:** `food_waste_kg`.
- **O que mede e fórmula:** valor central da distribuição de desperdício dos registros do recorte, por `mediana(food_waste_kg)`.
- **Por que foi escolhida:** a EDA mostrou cauda direita acentuada e influência de extremos. A mediana complementa o volume acumulado sem depender tanto dos maiores valores.
- **Público que atende:** gestores e nutricionistas que precisam interpretar o comportamento central dos registros junto aos gráficos.
- **Decisão apoiada:** verificar se um total elevado acompanha um deslocamento da distribuição ou decorre principalmente de poucos registros extremos, que devem ser investigados no laboratório.
- **O que comunica:** “qual valor divide os registros ordenados ao meio”. Não corresponde a desperdício por refeição nem a uma meta de desempenho.

## 5. Registros acima da meta hipotética — %

- **Variáveis utilizadas:** `food_waste_kg`, `meals_served` e a meta ajustável de g/refeição.
- **O que mede e fórmula:** primeiro calcular `g_por_refeicao = 1000 × food_waste_kg / meals_served` para registros com refeições positivas; depois `100 × quantidade de razões válidas estritamente maiores que a meta / quantidade de razões válidas`.
- **Por que foi escolhida:** distingue a intensidade agregada da frequência de ocorrências acima de uma referência. Registros exatamente na meta não são contados como acima dela.
- **Público que atende:** nutricionistas e gestores interessados em definir uma referência para acompanhar o recorte de dados.
- **Decisão apoiada:** explorar como a frequência de registros sinalizados muda ao ajustar a referência e priorizar a investigação dos grupos que concentram esses registros.
- **O que comunica:** “qual percentual dos registros com razão válida supera a referência escolhida”. A meta inicial de **150 g/refeição é hipotética**, criada para simulação; não é norma técnica, limite sanitário ou recomendação validada. O indicador não representa a porcentagem da comida que foi desperdiçada.

## Regras comuns de interpretação

Um recorte vazio ou um denominador inválido não deve ser interpretado como desempenho igual a zero; o app deve orientar a revisão dos filtros ou indicar a indisponibilidade da razão. Os filtros de intervalo podem selecionar pelo próprio desperdício e alterar as distribuições, por isso comparações entre recortes precisam considerar essa seleção.

As métricas não estimam custos ou economia financeira. A base não fornece massa preparada, custos, identificação confiável de cozinhas distintas ou desenho amostral que permita generalizar os resultados. Os visuais por evento e categoria são descritivos e não estabelecem causas. Os extremos e as ausências são preservados conforme a EDA, incluindo os 164 registros sem experiência informada entre os 911 registros originais.

**Fonte:** [Messy Food Waste Prediction Dataset — Kaggle](https://www.kaggle.com/competitions/messy-food-waste-prediction-dataset/data), `train.csv` incorporado ao notebook enviado pelo usuário.
