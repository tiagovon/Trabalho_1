import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from acao import Notificador


class Monitor:
    def __init__(self, navegador, url_monitorada, seletor, usuario="sistema"):
        self.nav = navegador
        self.url_monitorada = url_monitorada
        self.seletor = seletor
        self.usuario = usuario
        self.valor_anterior = None
        self.notificador = Notificador(navegador)

    def iniciar(self):
        while True:
            try:
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

            except KeyboardInterrupt:
                print("\nMonitoramento encerrado pelo usuário.")
                break

    def _esperar_pagina(self):
        WebDriverWait(self.nav.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def acao(self, valor_antigo, valor_novo):
        print("\n===== ALTERAÇÃO DETECTADA =====")
        print(f"Valor antigo: {valor_antigo}")
        print(f"Valor novo: {valor_novo}")
        print("================================\n")

        # Chama o notificador (escreve no Dontpad + clica no botão)
        self.notificador.notificar(valor_antigo, valor_novo, self.usuario)