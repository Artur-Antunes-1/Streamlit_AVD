"""Verificação real em contexto isolado do Chromium (sem sessão persistida).

Uso: python scripts/test_browser.py --url http://127.0.0.1:8501
Para a publicação, use --url https://SEU-APP.streamlit.app.
"""
import argparse
import json
from pathlib import Path
import re

from playwright.sync_api import sync_playwright, expect


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
        expect(page.get_by_role("heading", name="Menos desperdício. Mais clareza.")).to_be_visible(timeout=60000)
        expect(page.locator(".js-plotly-plot")).to_have_count(11, timeout=60000)
        expect(page.get_by_test_id("stException")).to_have_count(0)
        checks.append("Sessão isolada sem cookies: aplicação abriu sem autenticação")
        expect(page.get_by_role("tab")).to_have_count(2)
        expect(page.get_by_role("tab", name="01 · Laboratório de análise")).to_have_attribute("aria-selected", "true")
        page.screenshot(path=str(output / "dashboard1_desktop.png"), full_page=True)
        checks.append("Laboratório: mapa, seis histogramas e dispersão carregados")

        # Evento é um filtro comum: confirma resposta real no servidor e nos KPIs.
        page.get_by_test_id("stSidebar").get_by_text("Com evento", exact=True).click()
        expect(page.get_by_text(re.compile(r"78 de 911 registros selecionados"))).to_be_visible(timeout=30000)
        page.get_by_role("tab", name="02 · Gestão do refeitório").click()
        expect(page.get_by_text("78 registros avaliados", exact=False)).to_be_visible()
        expect(page.get_by_test_id("stMetric")).to_have_count(5)
        checks.append("Filtro lateral: Com evento seleciona 78 registros e atualiza gestão")
        page.get_by_role("button", name="Restaurar filtros").click()
        expect(page.get_by_text(re.compile(r"911 de 911 registros selecionados"))).to_be_visible(timeout=30000)
        expect(page.get_by_text("119,5 g", exact=True)).to_be_visible(timeout=30000)
        checks.append("Restauração: 911 registros e intensidade ponderada de 119,5 g/refeição")

        # O slider da meta altera a quinta métrica.
        page.reload(wait_until="domcontentloaded")
        page.get_by_role("tab", name="02 · Gestão do refeitório").click(timeout=30000)
        expect(page.locator(".js-plotly-plot")).to_have_count(11, timeout=30000)
        fifth = page.get_by_test_id("stMetric").nth(4)
        target = page.get_by_test_id("stSlider").filter(has_text="Meta exploratória").get_by_role("slider")
        expect(target).to_have_attribute("aria-valuenow", "150")
        target.focus()
        target.press("ArrowRight")
        expect(target).to_have_attribute("aria-valuenow", "155")
        expect(fifth).to_contain_text("36,6%", timeout=30000)
        target.press("ArrowLeft")
        expect(target).to_have_attribute("aria-valuenow", "150")
        expect(fifth).to_contain_text("39,5%", timeout=30000)
        checks.append("Meta exploratória: slider atualiza o percentual e retorna ao valor inicial")
        page.get_by_text("Gramas por refeição", exact=True).last.click()
        expect(page.get_by_role("radio", name="Gramas por refeição", exact=True)).to_be_checked()
        page.get_by_text("Volume total (kg)", exact=True).click()
        checks.append("Comparação de categorias: alternância entre kg total e g/refeição")
        expect(page.locator(".js-plotly-plot")).to_have_count(11)
        page.screenshot(path=str(output / "dashboard2_graficos.png"), full_page=True)
        page.get_by_role("heading", name="Menos desperdício. Mais clareza.").scroll_into_view_if_needed()
        page.screenshot(path=str(output / "dashboard2_desktop.png"), full_page=True)

        page.get_by_text("Consultar e baixar o resumo mensal", exact=True).click()
        with page.expect_download() as download:
            page.get_by_role("button", name="Baixar resumo mensal (CSV)").click()
        csv_file = output / "resumo_mensal.csv"
        download.value.save_as(csv_file)
        assert "g/refeição" in csv_file.read_text()
        checks.append("Download: CSV mensal agregado recebido")
        page.get_by_text("Fonte, metodologia e limites dos dados", exact=True).click()
        expect(page.get_by_text("Os 164 registros sem experiência", exact=False)).to_be_visible()
        checks.append("Metodologia e limitações disponíveis na interface")
        expect(page.get_by_test_id("stException")).to_have_count(0)

        page.set_viewport_size({"width": 390, "height": 844})
        page.get_by_role("heading", name="Menos desperdício. Mais clareza.").scroll_into_view_if_needed()
        expect(page.get_by_role("heading", name="Menos desperdício. Mais clareza.")).to_be_visible()
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
