# Dados e reprodução

Fonte: [Messy Food Waste Prediction Dataset, Kaggle](https://www.kaggle.com/competitions/messy-food-waste-prediction-dataset/data).

- `train.csv`: 911 registros × 12 colunas, extraídos do CSV incorporado no notebook enviado. O app lê esse arquivo local; não precisa de conta ou chave do Kaggle.
- `eda_tratada.csv`: exportação do dataframe tratado da EDA, para auditoria. A seção 13 do notebook permite salvar novamente os dois arquivos. O app normaliza o original em `analytics.py`.

SHA-256 de `train.csv`: `c2bedb198bf40cc6793921cdfe0573589923996b3347b3361561b114214b9adf`.

Datas: 01/01/2022 a 26/09/2024. As datas se repetem e não identificam estabelecimentos. Uma linha é um **registro**, não necessariamente um dia exclusivo de um mesmo refeitório. A base foi fornecida como exercício de limpeza, com coleta e amostragem sem documentação suficiente para generalização.

Tratamento: datas convertidas, categorias aparadas e normalizadas com `casefold`, 164 ausências em experiência mantidas. Não há imputação, remoção de extremos ou deduplicação automática. Apenas treino é analisado, conforme a EDA. A razão kg/refeição da EDA equivale a g/refeição ÷ 1.000.

Não foi atribuída uma licença nova ao dataset. A fonte e os termos do Kaggle continuam aplicáveis; a presença dos arquivos no projeto não concede direitos adicionais sobre os dados.
