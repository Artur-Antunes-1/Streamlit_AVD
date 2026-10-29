# Registro do uso de IA

Este arquivo documenta o pedido recebido e as decisões de implementação tomadas durante a preparação do projeto. Não é uma transcrição integral da conversa. A revisão e a validação humana do conteúdo continuam necessárias antes da entrega acadêmica.

## Pedido do usuário — síntese fiel

Criar uma aplicação Streamlit a partir da EDA anterior do Messy Food Waste Prediction Dataset, usando o notebook e as três aulas anexadas. A aplicação deve ter dois dashboards acessíveis por abas: um laboratório de distribuições e correlações e um painel com métricas para um público definido individualmente.

O painel lateral deve conter um seletor de variáveis e um filtro de intervalo. O primeiro dashboard exige um mapa de calor e um histograma para cada quantitativa avaliada. O segundo exige três a cinco métricas próprias e três visuais adicionais. O repositório público deve conter notebooks, `app.py`, `entregas/` com os dois rascunhos e `prompts/`. Após publicar, testar em janela anônima, conferir widgets, abas, exposição de dados sensíveis e link do app no README.

Fonte indicada pelo usuário: <https://www.kaggle.com/competitions/messy-food-waste-prediction-dataset/data>.

## Orientações de implementação utilizadas

1. Inspecionar o notebook para reaproveitar os dados e as regras de tratamento já adotadas, preservando a rastreabilidade com o CSV original incorporado e sua impressão digital.
2. Definir nutricionistas e gestores de cozinhas de serviços de alimentação como público do dashboard de gestão.
3. Preservar valores extremos e ausências; permitir a investigação por filtros sem modificar o arquivo original.
4. Criar histogramas por variável, mapa de calor com Pearson/Spearman e gráfico de dispersão no laboratório.
5. Calcular desperdício total, refeições, desperdício ponderado em g/refeição, mediana e percentual de registros acima de uma meta hipotética ajustável.
6. Comparar evolução mensal, categorias e presença de evento; explicitar as diferenças entre volume total e intensidade por refeição.
7. Preparar dois rascunhos SVG, documentação e verificações reproduzíveis. Distinguir desenhos de planejamento, capturas reais, testes locais e testes de uma aplicação publicada.

## Limites impostos ao conteúdo gerado

Não apresentar a razão g/refeição como percentual de comida desperdiçada. Não inventar custos, economia financeira, efeitos causais, previsões, representatividade da amostra ou identidade de cozinhas. Não fabricar URLs de publicação nem registrar testes externos como concluídos sem execução e evidência.

Os rascunhos SVG usam formas e valores ilustrativos para discutir o layout. Os indicadores apresentados pelo app devem ser calculados diretamente sobre os dados filtrados. A meta de 150 g/refeição é uma referência inicial de simulação, sem atribuição a norma ou recomendação técnica externa.

## Conferência humana antes de enviar

Conferir a adequação do público escolhido à proposta individual, interpretar as métricas e limitações, revisar os dois rascunhos e confirmar o funcionamento do endereço publicado em janela anônima. A contribuição de IA deve seguir as regras de autoria e divulgação da disciplina.
