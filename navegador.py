import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


class Navegador:
    def __init__(self):
        options = Options()
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=options)

    def acessar(self, url):
        try:
            self.driver.get(url)
            return True
        except WebDriverException as erro:
            print(f"Erro ao acessar a URL: {erro}")
            return False

    def pegar_valor(self, seletor):
        try:
            if seletor.startswith("/") or seletor.startswith("("):
                elemento = self.driver.find_element(By.XPATH, seletor)
                return self._extrair_numero(elemento.text)

            termo = seletor.strip().lower()
            body = self.driver.find_element(By.TAG_NAME, "body")
            texto_pagina = " ".join(body.text.split())

            return self._extrair_numero_associado(texto_pagina, termo)

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