# Relatório de verificação — Mesa Clara

Verificação local executada em **29/10/2026**, com Python 3.12, Streamlit 1.50.0, pandas 2.2.3 e Plotly 6.3.1. A verificação da publicação em **31/10/2026** está registrada separadamente abaixo.

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

Em 31/10/2026, após ajustar a restauração dos filtros, os **13 testes foram repetidos e passaram**. A configuração `pytest.ini` limita a descoberta aos testes do projeto em `tests/`, sem executar scripts temporários de inspeção.

Capturas reais do teste local:

- [Laboratório](dashboard1_desktop.png)
- [Gestão — indicadores](dashboard2_desktop.png)
- [Gestão — gráficos](dashboard2_graficos.png)
- [Gestão — tela estreita](dashboard2_mobile.png)

## Publicação — 31/10/2026

Endereço informado pelo autor: <https://arturantunes.streamlit.app/>. O link foi incluído no README.

Na primeira tentativa, o Chromium foi aberto em contexto isolado, sem cookies ou autenticação. O endereço redirecionou para `https://share.streamlit.io/app/arturantunes/`, com título **Not found · Streamlit**, e exibiu:

```text
You do not have access to this app or it does not exist
Please sign in to continue.
```

O autor alterou o compartilhamento para público e o teste foi repetido em uma nova sessão isolada. **O app passou a carregar sem autenticação.** O aviso inicial não foi tratado como erro de código ou de deploy.

Evidências da tentativa inicial: [captura da página de acesso](publicacao-acesso.png) e [resultado inicial](resultado-publicacao-acesso-inicial.json).

### Resultado após liberar o acesso público

O teste automatizado final no Chromium foi concluído com **11 verificações aprovadas e nenhum erro de JavaScript**:

- Acesso sem login, duas abas, 11 gráficos padrão e cinco indicadores.
- Filtro “Com evento” selecionando 78 registros; restauração recuperando os 911 registros e 119,5 g/refeição.
- Meta de 150 para 155 g/refeição alterando o percentual acima da meta de 39,5% para 36,6%, com retorno ao valor inicial.
- Alternância das barras entre volume total e intensidade por refeição.
- Download do CSV mensal agregado e consulta da metodologia.
- Consulta da tabela de estatísticas descritivas do laboratório.
- Remoção de uma quantitativa e restauração das seis seleções visíveis, com matriz 6 × 6 e 11 gráficos novamente.
- Conteúdo gerencial disponível em tela estreita de 390 × 844.

Na checagem complementar, foram alterados o método Pearson/Spearman, as classes dos histogramas, os dois eixos da dispersão, a seleção de quantitativas, a variável e o intervalo numérico, o período e as categorias. As respostas dos gráficos e indicadores foram conferidas: o limite superior de refeições excluiu o maior registro e retornou 910 registros e 337.264 refeições; período até 25/09/2024 combinado com remoção de Vegetais retornou 734 registros e 272.972 refeições.

A verificação identificou uma divergência na restauração: a seleção visível podia permanecer com cinco variáveis, enquanto a matriz já avaliava seis. O botão passou a atribuir explicitamente os padrões aos controles. A correção foi confirmada no navegador local e depois no app público, comparando as seis seleções visíveis com a matriz 6 × 6.

O recorte vazio também foi conferido na publicação: limpar as categorias retornou zero registros, orientações nas duas abas e nenhum gráfico ou indicador. Após restaurar, reapareceram os 911 registros, as seis variáveis e quatro categorias selecionadas, os cinco indicadores e os 11 gráficos. O CSV baixado continha somente cinco colunas agregadas, sem IDs, e reconciliou os 911 registros.

O script [scripts/test_browser.py](../scripts/test_browser.py) foi ajustado para localizar o app tanto na página principal local quanto no iframe usado pelo Community Cloud.

Evidências da publicação:

- [Resultado estruturado](resultado-publicacao.json)
- [Verificação complementar dos widgets](resultado-widgets-publicacao.json)
- [Laboratório](publicacao-dashboard1.png)
- [Gestão — indicadores](publicacao-dashboard2.png)
- [Gestão — gráficos](publicacao-graficos.png)
- [Gestão — tela estreita](publicacao-mobile.png)

## Pendências externas

- O repositório [Artur-Antunes-1/Streamlit_AVD](https://github.com/Artur-Antunes-1/Streamlit_AVD) foi tornado **público** pelo autor em 31/10/2026. A consulta à API do GitHub sem cabeçalho de autenticação retornou HTTP 200, `private: false` e `visibility: public`.
- Revisão humana das interpretações e preparação da entrega final.

Os resultados locais e os da publicação estão separados neste relatório. A configuração interna do provedor e seus logs não foram inspecionados; o fluxo público foi conferido diretamente no navegador.
