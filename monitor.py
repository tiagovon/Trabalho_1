import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Monitor:
    def __init__(self, navegador, url_monitorada, seletor):
        self.nav = navegador
        self.url_monitorada = url_monitorada
        self.seletor = seletor
        self.valor_anterior = None

    def iniciar(self):
        while True:
            valor_atual = self.nav.pegar_valor(self.seletor)

            if valor_atual is None:
                print("Valor não encontrado.")
                time.sleep(5)
                self.nav.driver.refresh()
                continue

            if self.valor_anterior is None:
                self.valor_anterior = valor_atual
                print(f"Valor inicial: {valor_atual}")

            elif valor_atual != self.valor_anterior:
                print(f"Alteração detectada: {self.valor_anterior} -> {valor_atual}")
                self.acao(self.valor_anterior, valor_atual)
                self.valor_anterior = valor_atual

            else:
                print(f"Sem alteração: {valor_atual}")

            time.sleep(5)
            self.nav.driver.refresh()

    def acao(self, valor_antigo, valor_novo):
        """
        Abre uma página pública de teste, escreve a mensagem e clica no botão.
        """
        driver = self.nav.driver

        try:
            print("Abrindo página pública para registrar a alteração...")

            driver.get("https://www.selenium.dev/selenium/web/web-form.html")

            wait = WebDriverWait(driver, 10)

            campo_texto = wait.until(
                EC.presence_of_element_located((By.NAME, "my-textarea"))
            )

            mensagem = (
                f"Alteração detectada no valor monitorado.\n"
                f"Valor antigo: {valor_antigo}\n"
                f"Valor novo: {valor_novo}"
            )

            campo_texto.clear()
            campo_texto.send_keys(mensagem)

            botao = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button"))
            )
            botao.click()

            print("Texto preenchido e botão clicado com sucesso.")

        except Exception as erro:
            print(f"Erro ao interagir com a outra página: {erro}")

        finally:
            print("Voltando para a página monitorada...")
            driver.get(self.url_monitorada)