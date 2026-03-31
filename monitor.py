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
            self._esperar_pagina()

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

    def _esperar_pagina(self):
        WebDriverWait(self.nav.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def acao(self, valor_antigo, valor_novo):
        driver = self.nav.driver

        try:
            print("Abrindo Gmail para registrar a alteração...")

            driver.get("https://mail.google.com/mail/u/0/#inbox?compose=new")

            wait = WebDriverWait(driver, 20)

            campo_para = wait.until(
                EC.presence_of_element_located((By.NAME, "to"))
            )
            campo_para.clear()
            campo_para.send_keys("tiago3242@gmail.com")

            campo_assunto = wait.until(
                EC.presence_of_element_located((By.NAME, "subjectbox"))
            )
            campo_assunto.clear()
            campo_assunto.send_keys("Alteração de preço detectada")

            campo_corpo = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@aria-label="Corpo da mensagem"]')
                )
            )
            campo_corpo.click()
            campo_corpo.send_keys(
                f"Alteração de preço detectada.\n\n"
                f"Valor antigo: {valor_antigo}\n"
                f"Valor novo: {valor_novo}"
            )

            botao_enviar = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@role="button" and @aria-label*="Enviar"]')
                )
            )
            botao_enviar.click()

            print("E-mail preenchido e enviado com sucesso.")

        except Exception as erro:
            print(f"Erro ao interagir com o Gmail: {erro}")

        finally:
            print("Voltando para a página monitorada...")
            driver.get(self.url_monitorada)