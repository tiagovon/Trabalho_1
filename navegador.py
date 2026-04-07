import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


class Navegador:
    def __init__(self, timeout=10):
        options = Options()
        options.add_argument(r"--user-data-dir=C:\selenium_chrome_profile")
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(timeout)

    def acessar(self, url):
        try:
            self.driver.get(url)
            return True
        except WebDriverException as erro:
            print(f"Erro ao acessar a URL: {erro}")
            return False

    def pegar_valor(self, tipo_busca, seletor):
        try:
            if tipo_busca == "xpath":
                elemento = self.driver.find_element(By.XPATH, seletor)
                valor = self._extrair_numero(elemento.text)
                return {
                    "valor": valor,
                    "metodo": "XPATH",
                    "posicao": seletor
                }

            if tipo_busca == "texto":
                body = self.driver.find_element(By.TAG_NAME, "body")
                texto_pagina = " ".join(body.text.split())
                valor = self._extrair_numero_associado(texto_pagina, seletor)
                return {
                    "valor": valor,
                    "metodo": "REGEX/TEXTO",
                    "posicao": f'termo="{seletor}"'
                }

            return None

        except Exception:
            return None

    def _extrair_numero_associado(self, texto, termo):
        if not texto:
            return None

        texto_lower = texto.lower()
        pos = texto_lower.find(termo.lower())

        if pos == -1:
            return None

        trecho = texto[pos + len(termo):]
        padrao = r"\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?"
        match = re.search(padrao, trecho)

        if match:
            return match.group(0)
        return None

    def _extrair_numero(self, texto):
        if not texto:
            return None

        padrao = r"\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?"
        match = re.search(padrao, texto)

        if match:
            return match.group(0)
        return None

    def fechar(self):
        self.driver.quit()