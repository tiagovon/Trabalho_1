import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import configurar_logger


class Monitor:
    def __init__(self, navegador, url_monitorada, tipo_busca, seletor, intervalo, nome_usuario):
        self.nav = navegador
        self.url_monitorada = url_monitorada
        self.tipo_busca = tipo_busca
        self.seletor = seletor
        self.intervalo = intervalo
        self.nome_usuario = nome_usuario
        self.valor_anterior = None
        self.logger = configurar_logger()

    def iniciar(self):
        self.logger.info(f"Usuário: {self.nome_usuario}")
        self.logger.info(f"URL monitorada: {self.url_monitorada}")
        self.logger.info(f"Tipo de busca: {self.tipo_busca}")
        self.logger.info(f"Seletor: {self.seletor}")

        try:
            while True:
                self._esperar_pagina()

                resultado = self.nav.pegar_valor(self.tipo_busca, self.seletor)

                if not resultado or resultado["valor"] is None:
                    msg = "Valor não encontrado."
                    print(msg)
                    self.logger.warning(msg)
                    time.sleep(self.intervalo)
                    self.nav.driver.refresh()
                    continue

                valor_atual = resultado["valor"]
                metodo = resultado["metodo"]
                posicao = resultado["posicao"]

                print(f"Encontrado por {metodo}: {posicao} -> {valor_atual}")
                self.logger.info(f"Encontrado por {metodo}: {posicao} -> {valor_atual}")

                if self.valor_anterior is None:
                    self.valor_anterior = valor_atual
                    print(f"Valor inicial: {valor_atual}")
                    self.logger.info(f"Valor inicial: {valor_atual}")

                elif valor_atual != self.valor_anterior:
                    msg = f"Alteração detectada: {self.valor_anterior} -> {valor_atual}"
                    print(msg)
                    self.logger.info(msg)
                    self.acao(self.valor_anterior, valor_atual)
                    self.valor_anterior = valor_atual

                else:
                    msg = f"Sem alteração: {valor_atual}"
                    print(msg)
                    self.logger.info(msg)

                time.sleep(self.intervalo)
                self.nav.driver.refresh()

        except KeyboardInterrupt:
            print("Monitoramento encerrado pelo usuário.")
            self.logger.info("Monitoramento encerrado pelo usuário.")
        finally:
            self.nav.fechar()

    def _esperar_pagina(self):
        WebDriverWait(self.nav.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def acao(self, valor_antigo, valor_novo):
        driver = self.nav.driver

        try:
            self.logger.info("Abrindo página de registro da alteração.")

            html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Registro de Alteração</title>
            </head>
            <body>
                <h1>Alteração detectada</h1>

                <label for="mensagem">Mensagem:</label><br>
                <textarea id="mensagem" rows="8" cols="60"></textarea><br><br>

                <button id="btnConfirmar" onclick="document.getElementById('status').innerText='Botão clicado com sucesso';">
                    Confirmar envio
                </button>

                <p id="status"></p>
            </body>
            </html>
            """

            driver.get("data:text/html;charset=utf-8," + html)

            wait = WebDriverWait(driver, 20)

            campo_mensagem = wait.until(
                EC.presence_of_element_located((By.ID, "mensagem"))
            )
            campo_mensagem.clear()
            campo_mensagem.send_keys(
                f"Alteração detectada.\n\n"
                f"Valor antigo: {valor_antigo}\n"
                f"Valor novo: {valor_novo}\n"
                f"URL monitorada: {self.url_monitorada}"
            )

            botao = wait.until(
                EC.element_to_be_clickable((By.ID, "btnConfirmar"))
            )
            botao.click()

            print("Página pública preenchida e botão acionado com sucesso.")
            self.logger.info("Página pública preenchida e botão acionado com sucesso.")

            time.sleep(3)

        except Exception as erro:
            print(f"Erro ao registrar alteração na página pública: {erro}")
            self.logger.error(f"Erro ao registrar alteração na página pública: {erro}")

        finally:
            driver.get(self.url_monitorada)