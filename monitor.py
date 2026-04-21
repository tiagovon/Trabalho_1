"""
Modulo de monitoramento continuo de valores em paginas web.

Implementa a classe Monitor, que fica em loop verificando periodicamente
o valor de um campo na pagina. Quando detecta uma alteracao, dispara a
acao de notificacao via Notificador e registra tudo via Logger.

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
    escreve o valor antigo e o novo em outra pagina publica (Dontpad)
    e registra a acao no arquivo de log.

    Attributes:
        nav (Navegador): Instancia do Navegador para controle do Chrome.
        url_monitorada (str): URL da pagina a ser monitorada.
        seletor (str): Texto ou XPath que identifica o valor na pagina.
        usuario (str): Nome do usuario que esta executando o sistema.
        valor_anterior (str): Ultimo valor lido da pagina.
        notificador (Notificador): Instancia do notificador de mudancas.
        logger (Logger): Instancia do logger (opcional).
    """

    INTERVALO_ENTRE_LEITURAS = 5  # segundos entre cada verificacao
    TIMEOUT_PAGINA = 10           # segundos para esperar a pagina carregar

    def __init__(self, navegador, url_monitorada, seletor,
                 usuario="sistema", logger=None):
        """
        Inicializa o monitor.

        Args:
            navegador (Navegador): Instancia ja inicializada do Navegador.
            url_monitorada (str): URL que sera monitorada continuamente.
            seletor (str): Texto ou XPath do valor a ser extraido.
            usuario (str, optional): Nome do usuario. Default: 'sistema'.
            logger (Logger, optional): Logger para registro de acoes.
        """
        self.nav = navegador
        self.url_monitorada = url_monitorada
        self.seletor = seletor
        self.usuario = usuario
        self.valor_anterior = None
        self.logger = logger
        self.notificador = Notificador(navegador, logger=logger)

    def _registrar(self, mensagem):
        """
        Registra no logger se disponivel; senao, apenas imprime.

        Args:
            mensagem (str): Mensagem a ser registrada.
        """
        if self.logger:
            self.logger.log(mensagem)
        else:
            print(mensagem)

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
                    self._registrar("[AVISO] Valor nao encontrado na pagina.")
                    time.sleep(self.INTERVALO_ENTRE_LEITURAS)
                    self.nav.driver.get(self.url_monitorada)
                    continue

                if self.valor_anterior is None:
                    self.valor_anterior = valor_atual
                    self._registrar(
                        f"Valor inicial capturado: {valor_atual}"
                    )

                elif valor_atual != self.valor_anterior:
                    self._registrar(
                        f"ALTERACAO DETECTADA: "
                        f"{self.valor_anterior} -> {valor_atual}"
                    )
                    self.acao(self.valor_anterior, valor_atual)
                    self.valor_anterior = valor_atual

                else:
                    self._registrar(f"Sem alteracao: {valor_atual}")

                time.sleep(self.INTERVALO_ENTRE_LEITURAS)
                self.nav.driver.get(self.url_monitorada)

            except KeyboardInterrupt:
                self._registrar("Monitoramento encerrado pelo usuario.")
                self.nav.fechar()
                break

            except Exception as erro:
                self._registrar(
                    f"[ERRO] Erro inesperado no monitoramento: {erro}"
                )
                time.sleep(self.INTERVALO_ENTRE_LEITURAS)
                continue

    def _esperar_pagina(self):
        """Espera o corpo da pagina estar presente antes de prosseguir."""
        WebDriverWait(self.nav.driver, self.TIMEOUT_PAGINA).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def acao(self, valor_antigo, valor_novo):
        """
        Executa a acao quando uma mudanca de valor e detectada.

        Args:
            valor_antigo (str): Valor anterior lido da pagina.
            valor_novo (str): Novo valor lido apos a mudanca.
        """
        self.notificador.notificar(valor_antigo, valor_novo, self.usuario)