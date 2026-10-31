"""Verificação real em contexto isolado do Chromium (sem sessão persistida).

Uso: python scripts/test_browser.py --url http://127.0.0.1:8501
Para a publicação, use --url https://SEU-APP.streamlit.app.
"""
import argparse
import json
from pathlib import Path
import re
import time

from playwright.sync_api import Error, sync_playwright, expect


def find_app_frame(page, timeout_ms=60000):
    """Local usa o frame principal; Community Cloud pode envolver o app num iframe."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.get_by_role("heading", name="Menos desperdício. Mais clareza.").is_visible():
                    return frame
            except Error:
                # O frame anterior pode ser removido durante o carregamento do Cloud.
                continue
        page.wait_for_timeout(250)
    raise AssertionError("A aplicação não carregou em nenhum frame da página: " + page.url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", default="artifacts/browser")
    parser.add_argument("--chromium", default=None, help="Caminho opcional do Chromium já instalado")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    checks, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium, headless=True,
                                    args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1600, "height": 1100}, locale="pt-BR")
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url, wait_until="domcontentloaded")
        app = find_app_frame(page)
        expect(app.get_by_role("heading", name="Menos desperdício. Mais clareza.")).to_be_visible(timeout=60000)
        expect(app.locator(".js-plotly-plot")).to_have_count(11, timeout=60000)
        expect(app.get_by_test_id("stException")).to_have_count(0)
        checks.append("Sessão isolada sem cookies: aplicação abriu sem autenticação")
        expect(app.get_by_role("tab")).to_have_count(2)
        expect(app.get_by_role("tab", name="01 · Laboratório de análise")).to_have_attribute("aria-selected", "true")
        page.screenshot(path=str(output / "dashboard1_desktop.png"), full_page=True)
        checks.append("Laboratório: mapa, seis histogramas e dispersão carregados")

        # Regressão: restaurar filtros precisa atualizar a seleção visível e o mapa.
        quantitative = app.get_by_test_id("stSidebar").get_by_test_id("stMultiSelect").filter(
            has_text="Variáveis quantitativas avaliadas")
        tags = quantitative.get_by_role("button", name=re.compile(r", close by backspace$"))
        expect(tags).to_have_count(6)
        quantitative.get_by_role("combobox").focus()
        quantitative.get_by_role("combobox").press("Backspace")
        quantitative.get_by_role("combobox").press("Escape")
        expect(tags).to_have_count(5)
        expect(app.locator(".js-plotly-plot")).to_have_count(10, timeout=30000)
        app.get_by_role("button", name="Restaurar filtros").click()
        expect(tags).to_have_count(6, timeout=30000)
        app.wait_for_function("""() => {
            const plot = document.querySelector('.js-plotly-plot');
            return plot?.data?.[0]?.x?.length === 6 && plot.data[0].y.length === 6;
        }""", timeout=30000)
        expect(app.locator(".js-plotly-plot")).to_have_count(11, timeout=30000)
        checks.append("Restauração das variáveis: seis seleções visíveis e matriz 6 × 6 após remover uma variável")

        app.get_by_text("Estatísticas descritivas do recorte", exact=True).click()
        expect(app.get_by_test_id("stDataFrame").first).to_be_visible()
        app.get_by_text("Estatísticas descritivas do recorte", exact=True).click()
        checks.append("Estatísticas descritivas: expansor abre a tabela do recorte")

        # Evento é um filtro comum: confirma resposta real no servidor e nos KPIs.
        app.get_by_test_id("stSidebar").get_by_text("Com evento", exact=True).click()
        expect(app.get_by_text(re.compile(r"78 de 911 registros selecionados"))).to_be_visible(timeout=30000)
        app.get_by_role("tab", name="02 · Gestão do refeitório").click()
        expect(app.get_by_text("78 registros avaliados", exact=False)).to_be_visible()
        expect(app.get_by_test_id("stMetric")).to_have_count(5)
        checks.append("Filtro lateral: Com evento seleciona 78 registros e atualiza gestão")
        app.get_by_role("button", name="Restaurar filtros").click()
        expect(app.get_by_text(re.compile(r"911 de 911 registros selecionados"))).to_be_visible(timeout=30000)
        expect(app.get_by_text("119,5 g", exact=True)).to_be_visible(timeout=30000)
        checks.append("Restauração: 911 registros e intensidade ponderada de 119,5 g/refeição")

        # O slider da meta altera a quinta métrica.
        page.reload(wait_until="domcontentloaded")
        app = find_app_frame(page)
        app.get_by_role("tab", name="02 · Gestão do refeitório").click(timeout=30000)
        expect(app.locator(".js-plotly-plot")).to_have_count(11, timeout=30000)
        fifth = app.get_by_test_id("stMetric").nth(4)
        target = app.get_by_test_id("stSlider").filter(has_text="Meta exploratória").get_by_role("slider")
        expect(target).to_have_attribute("aria-valuenow", "150")
        target.focus()
        target.press("ArrowRight")
        expect(target).to_have_attribute("aria-valuenow", "155")
        expect(fifth).to_contain_text("36,6%", timeout=30000)
        target.press("ArrowLeft")
        expect(target).to_have_attribute("aria-valuenow", "150")
        expect(fifth).to_contain_text("39,5%", timeout=30000)
        checks.append("Meta exploratória: slider atualiza o percentual e retorna ao valor inicial")
        app.get_by_text("Gramas por refeição", exact=True).last.click()
        expect(app.get_by_role("radio", name="Gramas por refeição", exact=True)).to_be_checked()
        app.get_by_text("Volume total (kg)", exact=True).click()
        checks.append("Comparação de categorias: alternância entre kg total e g/refeição")
        expect(app.locator(".js-plotly-plot")).to_have_count(11)
        page.screenshot(path=str(output / "dashboard2_graficos.png"), full_page=True)
        app.get_by_role("heading", name="Menos desperdício. Mais clareza.").scroll_into_view_if_needed()
        page.screenshot(path=str(output / "dashboard2_desktop.png"), full_page=True)

        app.get_by_text("Consultar e baixar o resumo mensal", exact=True).click()
        with page.expect_download() as download:
            app.get_by_role("button", name="Baixar resumo mensal (CSV)").click()
        csv_file = output / "resumo_mensal.csv"
        download.value.save_as(csv_file)
        assert "g/refeição" in csv_file.read_text()
        checks.append("Download: CSV mensal agregado recebido")
        app.get_by_text("Fonte, metodologia e limites dos dados", exact=True).click()
        expect(app.get_by_text("Os 164 registros sem experiência", exact=False)).to_be_visible()
        checks.append("Metodologia e limitações disponíveis na interface")
        expect(app.get_by_test_id("stException")).to_have_count(0)

        page.set_viewport_size({"width": 390, "height": 844})
        app.get_by_role("heading", name="Menos desperdício. Mais clareza.").scroll_into_view_if_needed()
        expect(app.get_by_role("heading", name="Menos desperdício. Mais clareza.")).to_be_visible()
        page.screenshot(path=str(output / "dashboard2_mobile.png"), full_page=True)
        checks.append("Tela estreita: conteúdo gerencial permanece disponível")
        assert not errors, errors
        context.close()
        browser.close()
    report = {"url": args.url, "isolated_context": True, "checks": checks, "page_errors": errors}
    (output / "resultado.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
