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
                    print("Valor nao encontrado.")
                    time.sleep(5)
                    self.nav.driver.get(self.url_monitorada)  # auto-corrige
                    continue

                if self.valor_anterior is None:
                    self.valor_anterior = valor_atual
                    print(f"Valor inicial: {valor_atual}")

                elif valor_atual != self.valor_anterior:
                    print(f"Alteracao detectada: {self.valor_anterior} -> {valor_atual}")
                    self.acao(self.valor_anterior, valor_atual)
                    self.valor_anterior = valor_atual

                else:
                    print(f"Sem alteracao: {valor_atual}")

                time.sleep(5)
                # MUDANÇA CHAVE: em vez de refresh(), navega explicitamente.
                # Se o notificador deixou a aba em qualquer outro lugar,
                # isso corrige automaticamente.
                self.nav.driver.get(self.url_monitorada)

            except KeyboardInterrupt:
                print("\nMonitoramento encerrado pelo usuario.")
                break

    def _esperar_pagina(self):
        WebDriverWait(self.nav.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def acao(self, valor_antigo, valor_novo):
        print("\n===== ALTERACAO DETECTADA =====")
        print(f"Valor antigo: {valor_antigo}")
        print(f"Valor novo: {valor_novo}")
        print("================================\n")
        self.notificador.notificar(valor_antigo, valor_novo, self.usuario)