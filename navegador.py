"""
Modulo de controle do navegador web via SeleniumBase.

Implementa a classe Navegador, que encapsula toda a interacao com o
Chrome via Selenium. Oferece metodos para acessar URLs e extrair
valores numericos de paginas web, usando XPath direto ou busca
textual com expressoes regulares.

Usa SeleniumBase com modo 'undetected' (uc=True) para contornar
protecoes anti-bot como Cloudflare em sites monitorados.

Complexidade (Big O):
    - acessar(): O(1) - tempo constante mais tempo de resposta da rede.
    - pegar_valor(): O(n) onde n e o tamanho do texto da pagina.
    - _extrair_melhor_numero(): O(n * k) onde k = ocorrencias do termo.
"""

import re

from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


class Navegador:
    """
    Encapsula o controle do navegador Chrome via SeleniumBase.

    Oferece metodos para navegar entre URLs e extrair valores numericos
    de paginas web, com suporte a XPath e busca textual.

    Attributes:
        driver: Instancia do SeleniumBase Driver (Chrome em modo undetected).
    """

    # Regex universal para numeros (aceita formato BR e US)
    # Exemplos que casa:
    #   70.432,55 (BR)  |  70,432.55 (US)  |  70432  |  99,99  |  $123.45
    PADRAO_NUMERO = r"\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?"

    # Janela de texto (em chars) a examinar apos encontrar o termo
    JANELA_BUSCA = 150

    def __init__(self):
        """
        Inicializa o navegador com bypass de deteccao de automacao.

        Configuracoes aplicadas:
            - uc=True: modo undetected (contorna Cloudflare).
            - locale_code='pt-BR': evita que o Google Tradutor apareca.
            - do_not_track=True: envia header DNT para mais privacidade.
            - disable_features: desativa UI do tradutor.
        """
        self.driver = Driver(
            uc=True,
            headless=False,
            locale_code="pt-BR",
            do_not_track=True,
            disable_features="TranslateUI,Translate",
        )
        self.driver.maximize_window()

    def acessar(self, url):
        """
        Acessa uma URL no navegador.

        Para URLs do Dontpad, usa o metodo uc_open_with_reconnect do
        SeleniumBase, que passa automaticamente pelo Cloudflare.
        Para outras URLs, usa o metodo get tradicional.

        Args:
            url (str): URL completa a ser acessada (com http:// ou https://).

        Returns:
            bool: True se a pagina foi acessada com sucesso, False em caso
            de erro de conexao ou navegador.

        Example:
            >>> nav = Navegador()
            >>> nav.acessar("https://coinmarketcap.com/currencies/bitcoin/")
            True
        """
        try:
            if "dontpad" in url:
                self.driver.uc_open_with_reconnect(url, reconnect_time=4)
            else:
                self.driver.get(url)
            return True
        except WebDriverException as erro:
            print(f"[ERRO] Erro ao acessar URL: {erro}")
            return False

    def pegar_valor(self, seletor):
        """
        Extrai o valor numerico da pagina usando um seletor.

        O seletor pode ser:
            - Um XPath (comeca com '/' ou '('): busca o elemento especifico.
            - Um texto: busca a palavra na pagina e retorna o numero
              mais proximo/maior associado.

        Loga no console a posicao/estrategia usada, conforme exigido
        pelo criterio do trabalho.

        Args:
            seletor (str): XPath ou texto a ser buscado na pagina.

        Returns:
            str | None: String com o numero encontrado ou None se nao
            encontrou.

        Example:
            >>> nav.pegar_valor("//span[@class='price']")
            '65.234,10'
            >>> nav.pegar_valor("Bitcoin price")
            '70.432,55'
        """
        try:
            # Caminho 1: seletor e XPath
            if seletor.startswith("/") or seletor.startswith("("):
                elemento = self.driver.find_element(By.XPATH, seletor)
                valor = self._extrair_numero(elemento.text)
                print(f"[LOG] Posicao via XPath: {seletor}")
                print(f"[LOG] Valor extraido: {valor}")
                return valor

            # Caminho 2: seletor e texto (busca na pagina)
            termo = seletor.strip().lower()
            body = self.driver.find_element(By.TAG_NAME, "body")
            texto_pagina = body.text

            valor = self._extrair_melhor_numero(texto_pagina, termo)
            print(f"[LOG] Posicao via busca textual: termo='{termo}'")
            print(f"[LOG] Regex usada: {self.PADRAO_NUMERO}")
            print(f"[LOG] Valor extraido: {valor}")
            return valor

        except Exception as erro:
            print(f"[DEBUG] Erro ao pegar valor: {erro}")
            return None

    def _extrair_numero(self, texto):
        """
        Extrai o primeiro numero encontrado em um texto.

        Usado quando ja temos o elemento especifico (via XPath) e
        precisamos so pegar o numero dentro dele.

        Args:
            texto (str): Texto onde buscar o numero.

        Returns:
            str | None: Numero encontrado como string ou None.
        """
        if not texto:
            return None

        match = re.search(self.PADRAO_NUMERO, texto)
        if match:
            return match.group(0)
        return None

    def _extrair_melhor_numero(self, texto, termo):
        """
        Extrai o numero mais relevante apos ocorrencias de um termo.

        Estrategia: procura TODAS as ocorrencias do termo no texto e,
        para cada uma, busca o numero mais proximo nos proximos
        JANELA_BUSCA caracteres. Retorna o MAIOR numero encontrado
        (geralmente o preco principal em destaque na pagina).

        Suporta formato brasileiro (70.432,55) e americano ($70,432.55).

        Args:
            texto (str): Texto completo da pagina.
            termo (str): Termo a ser buscado (ex: "Bitcoin price").

        Returns:
            str | None: Maior numero encontrado como string ou None.
        """
        if not texto:
            return None

        texto_lower = texto.lower()
        termo_lower = termo.lower()
        candidatos = []

        # Procura TODAS as ocorrencias do termo
        pos = 0
        while True:
            pos = texto_lower.find(termo_lower, pos)
            if pos == -1:
                break

            # Pega os proximos JANELA_BUSCA chars apos o termo
            inicio_trecho = pos + len(termo_lower)
            fim_trecho = inicio_trecho + self.JANELA_BUSCA
            trecho = texto[inicio_trecho:fim_trecho]

            # Extrai primeiro numero desse trecho
            match = re.search(self.PADRAO_NUMERO, trecho)
            if match:
                numero_str = match.group(0)
                valor_float = self._converter_para_float(numero_str)
                if valor_float is not None:
                    candidatos.append((valor_float, numero_str))

            pos += len(termo_lower)

        if not candidatos:
            return None

        # Retorna o MAIOR numero (geralmente o preco principal)
        maior = max(candidatos, key=lambda x: x[0])
        return maior[1]

    def _converter_para_float(self, numero_str):
        """
        Converte string de numero para float, suportando BR e US.

        Regras de deteccao:
            - "70.432,55" (BR): ponto = milhar, virgula = decimal.
            - "70,432.55" (US): virgula = milhar, ponto = decimal.
            - "70,55" (BR decimal) vs "70,432" (US milhar): decide pelo
              tamanho da parte apos a virgula.

        Args:
            numero_str (str): Numero como string (ex: "70.432,55").

        Returns:
            float | None: Valor convertido ou None em caso de erro.
        """
        try:
            tem_virgula = "," in numero_str
            tem_ponto = "." in numero_str

            if tem_virgula and tem_ponto:
                # Tem os dois: o que aparece depois e o decimal
                if numero_str.rfind(",") > numero_str.rfind("."):
                    # Formato BR: 70.432,55
                    return float(
                        numero_str.replace(".", "").replace(",", ".")
                    )
                else:
                    # Formato US: 70,432.55
                    return float(numero_str.replace(",", ""))

            if tem_virgula:
                # So tem virgula
                partes = numero_str.split(",")
                if len(partes[-1]) <= 2:
                    # Decimal BR: 70,55
                    return float(numero_str.replace(",", "."))
                # Milhar US: 70,432
                return float(numero_str.replace(",", ""))

            if tem_ponto:
                # So tem ponto
                partes = numero_str.split(".")
                if len(partes[-1]) <= 2:
                    # Decimal US: 70.55
                    return float(numero_str)
                # Milhar BR: 70.432
                return float(numero_str.replace(".", ""))

            # Numero puro, sem separador
            return float(numero_str)

        except (ValueError, AttributeError):
            return None

    def fechar(self):
        """
        Fecha o navegador e encerra a sessao do driver.

        Deve ser chamado ao final do uso para liberar recursos do
        sistema (processo do Chrome, memoria, etc.).
        """
        try:
            self.driver.quit()
        except Exception as erro:
            print(f"[AVISO] Erro ao fechar navegador: {erro}")