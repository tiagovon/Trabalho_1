"""
Modulo de monitoramento continuo de valores em paginas web.

Implementa a classe Monitor, que fica em loop verificando periodicamente
o valor de um campo na pagina. Quando detecta uma alteracao, dispara a
acao de notificacao via Notificador.

Complexidade (Big O):
    - iniciar(): O(t * n) onde t = numero de iteracoes e n = tamanho da pagina.
    - acao(): O(1) + complexidade do Notificador (abertura de aba, escrita).
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from acao import Notificador


class Monitor:
    """
    Monitora continuamente um valor em uma pagina web.

    Quando detecta alteracao no valor, dispara um Notificador que
    escreve o valor antigo e o novo em outra pagina publica (Dontpad).

    Attributes:
        nav (Navegador): Instancia do Navegador para controle do Chrome.
        url_monitorada (str): URL da pagina a ser monitorada.
        seletor (str): Texto ou XPath que identifica o valor na pagina.
        usuario (str): Nome do usuario que esta executando o sistema.
        valor_anterior (str): Ultimo valor lido da pagina (para comparacao).
        notificador (Notificador): Instancia do notificador de mudancas.
    """

    INTERVALO_ENTRE_LEITURAS = 5  # segundos entre cada verificacao
    TIMEOUT_PAGINA = 10            # segundos para esperar a pagina carregar

    def __init__(self, navegador, url_monitorada, seletor, usuario="sistema"):
        """
        Inicializa o monitor.

        Args:
            navegador (Navegador): Instancia ja inicializada do Navegador.
            url_monitorada (str): URL que sera monitorada continuamente.
            seletor (str): Texto ou XPath do valor a ser extraido.
            usuario (str, optional): Nome do usuario. Default: 'sistema'.
        """
        self.nav = navegador
        self.url_monitorada = url_monitorada
        self.seletor = seletor
        self.usuario = usuario
        self.valor_anterior = None
        self.notificador = Notificador(navegador)

    def iniciar(self):
        """
        Inicia o loop infinito de monitoramento.

        A cada INTERVALO_ENTRE_LEITURAS segundos:
            1. Espera a pagina carregar completamente.
            2. Extrai o valor atual da pagina.
            3. Compara com o valor anterior.
            4. Se houve alteracao, dispara o Notificador.
            5. Recarrega a pagina para pegar novo valor.

        Loop interrompido graciosamente com Ctrl+C (KeyboardInterrupt).
        """
        while True:
            try:
                self._esperar_pagina()
                valor_atual = self.nav.pegar_valor(self.seletor)

                if valor_atual is None:
                    print("[AVISO] Valor nao encontrado na pagina.")
                    time.sleep(self.INTERVALO_ENTRE_LEITURAS)
                    self.nav.driver.get(self.url_monitorada)
                    continue

                if self.valor_anterior is None:
                    # Primeira leitura: apenas armazena
                    self.valor_anterior = valor_atual
                    print(f"[INFO] Valor inicial capturado: {valor_atual}")

                elif valor_atual != self.valor_anterior:
                    # Detectou mudanca -> dispara acao
                    print(f"[INFO] Alteracao detectada: "
                          f"{self.valor_anterior} -> {valor_atual}")
                    self.acao(self.valor_anterior, valor_atual)
                    self.valor_anterior = valor_atual

                else:
                    # Sem mudanca
                    print(f"[INFO] Sem alteracao: {valor_atual}")

                time.sleep(self.INTERVALO_ENTRE_LEITURAS)
                self.nav.driver.get(self.url_monitorada)

            except KeyboardInterrupt:
                print("\n[INFO] Monitoramento encerrado pelo usuario.")
                self.nav.fechar()
                break

            except Exception as erro:
                print(f"[ERRO] Erro inesperado no monitoramento: {erro}")
                time.sleep(self.INTERVALO_ENTRE_LEITURAS)
                continue

    def _esperar_pagina(self):
        """
        Espera o corpo da pagina estar presente antes de prosseguir.

        Usa WebDriverWait para aguardar ate TIMEOUT_PAGINA segundos
        pela presenca da tag <body>.

        Raises:
            TimeoutException: Se a pagina nao carregar dentro do timeout.
        """
        WebDriverWait(self.nav.driver, self.TIMEOUT_PAGINA).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def acao(self, valor_antigo, valor_novo):
        """
        Executa a acao quando uma mudanca de valor e detectada.

        Loga a alteracao no console e delega ao Notificador a tarefa
        de escrever a mensagem em outra pagina publica.

        Args:
            valor_antigo (str): Valor anterior lido da pagina.
            valor_novo (str): Novo valor lido apos a mudanca.
        """
        print("\n===== ALTERACAO DETECTADA =====")
        print(f"Valor antigo: {valor_antigo}")
        print(f"Valor novo:   {valor_novo}")
        print("===============================\n")

        self.notificador.notificar(valor_antigo, valor_novo, self.usuario)