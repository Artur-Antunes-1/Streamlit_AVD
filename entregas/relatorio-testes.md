# Relatório de verificação — Mesa Clara

Verificação executada em **29/10/2026**, com Python 3.12, Streamlit 1.50.0, pandas 2.2.3 e Plotly 6.3.1. Este relatório descreve testes **locais**. O endereço do app publicado ainda não foi disponibilizado.

## Fluxo verificado

O usuário seleciona filtros no painel lateral → o Streamlit recalcula um único recorte do CSV local → o laboratório atualiza histogramas/correlações/dispersão e o painel de gestão atualiza os cinco KPIs, os três gráficos e o resumo mensal.

| Verificação | Resultado e evidência |
| --- | --- |
| Dados originais | 911 registros, 12 colunas, SHA-256 igual ao notebook. Categorias normalizadas; 164 ausências de experiência mantidas. |
| Cálculos | Testes validam ponderação por refeições, comparação estrita com a meta, somas por mês/categoria e denominadores inválidos. |
| Dois dashboards | AppTest confirma duas abas, 11 gráficos padrão e cinco indicadores. Chromium abriu ambas as abas sem erro de JavaScript. |
| Todos os widgets de análise | AppTest altera quantitativas, variável de intervalo, intervalo numérico, período, categorias, evento, método, classes, eixos, meta e modo das barras. Confere o efeito nos dados e gráficos. |
| Recortes vazios e constantes | Sem categorias: ambas as abas orientam ampliar os filtros. Sem quantitativas: laboratório orienta selecionar variáveis e gestão permanece disponível. Variável constante produz correlações indefinidas, sem falha. |
| Navegador sem sessão | Chromium/Playwright em contexto isolado, sem cookies ou estado persistido, abriu `http://127.0.0.1:8501` sem autenticação. Equivalente técnico de uma sessão anônima para o teste local. |
| Filtro real no navegador | “Com evento” selecionou 78 de 911 registros. A aba de gestão refletiu 78 registros. Restauração recuperou 911 registros e 119,5 g/refeição. |
| Meta real no navegador | De 150 para 155 g/refeição, o percentual acima da meta passou de 39,5% para 36,6%; ao voltar, recuperou 39,5%. |
| Barras e download | Alternância kg total/g por refeição respondeu. Download entregou CSV mensal agregado com a coluna g/refeição. |
| Tela estreita | Conteúdo de gestão disponível em viewport de 390 × 844; captura salva. Não foi uma auditoria completa de acessibilidade. |
| Privacidade | Inspeção dos arquivos textuais não encontrou indícios de credenciais, chaves privadas, e-mails ou CPF. IDs não são exibidos; download contém apenas agregados. Estatísticas de uso do Streamlit desativadas. |
| Rascunhos | Dois SVGs válidos e versões JPG em `entregas/`. São desenhos ilustrativos, distintos das capturas reais. |

## Resultado automatizado

```text
python -m pytest -q
13 passed
```

São seis casos de dados/métricas e sete de integração do Streamlit. O teste de navegador é separado e foi concluído com `page_errors: []`. Seu resultado estruturado está em [resultado.json](resultado.json); o script reproduzível é [scripts/test_browser.py](../scripts/test_browser.py).

Capturas reais do teste local:

- [Laboratório](dashboard1_desktop.png)
- [Gestão — indicadores](dashboard2_desktop.png)
- [Gestão — gráficos](dashboard2_graficos.png)
- [Gestão — tela estreita](dashboard2_mobile.png)

## Pendências externas

- O repositório de destino é [Artur-Antunes-1/Streamlit_AVD](https://github.com/Artur-Antunes-1/Streamlit_AVD), **privado por solicitação do autor**. A entrega acadêmica pede visibilidade pública.
- Publicar no Streamlit Community Cloud, com Python 3.12, branch `main` e `app.py`.
- Adicionar o endereço real do app no README.
- Repetir todos os testes no endereço publicado em janela anônima. O teste automatizado aceita `--url` com esse endereço.

Nenhum teste local foi apresentado como evidência de publicação. A configuração do provedor, o acesso público e os logs da versão publicada ainda precisam ser conferidos após o deploy.
