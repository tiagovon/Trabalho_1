import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


class Navegador:
    def __init__(self):
        options = Options()
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
            # Se for XPath, usa direto
            if seletor.startswith("/") or seletor.startswith("("):
                elemento = self.driver.find_element(By.XPATH, seletor)
                return self._extrair_numero(elemento.text)

            termo = seletor.strip().lower()

            # pega todo o texto visível do body
            body = self.driver.find_element(By.TAG_NAME, "body")
            texto_pagina = " ".join(body.text.split())

            return self._extrair_numero_associado(texto_pagina, termo)

        except Exception:
            return None

    def _extrair_numero_associado(self, texto, termo):
        """
        Ex:
        'Dólar 5,201 Euro 5,224'
        termo='dólar' -> 5,201
        termo='euro'  -> 5,224
        """
        if not texto:
            return None

        texto_lower = texto.lower()
        termo_lower = termo.lower()

        pos = texto_lower.find(termo_lower)
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