import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
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
        """
        Aceita:
        - XPath
        - texto comum, como: Dólar, Euro, Bitcoin etc.
        """

        try:
            if seletor.startswith("/") or seletor.startswith("("):
                elemento = self.driver.find_element(By.XPATH, seletor)
                return self._extrair_numero(elemento.text)

            termo = seletor.strip().lower()

            xpath = (
                "//*[contains("
                "translate(normalize-space(.), "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÃÂÉÈÊÍÌÎÓÒÕÔÚÙÛÇ', "
                "'abcdefghijklmnopqrstuvwxyzáàãâéèêíìîóòõôúùûç'"
                "), "
                f"'{termo}'"
                ")]"
            )

            elementos = self.driver.find_elements(By.XPATH, xpath)

            for elemento in elementos:
                textos_para_testar = []

                texto_atual = elemento.text.strip()
                if texto_atual:
                    textos_para_testar.append(texto_atual)

                try:
                    pai = elemento.find_element(By.XPATH, "..")
                    texto_pai = pai.text.strip()
                    if texto_pai:
                        textos_para_testar.append(texto_pai)
                except Exception:
                    pass

                try:
                    proximo = elemento.find_element(By.XPATH, "./following-sibling::*[1]")
                    texto_proximo = proximo.text.strip()
                    if texto_proximo:
                        textos_para_testar.append(texto_proximo)
                except Exception:
                    pass

                for texto in textos_para_testar:
                    numero = self._extrair_numero_associado(texto, termo)
                    if numero:
                        return numero

            return None

        except NoSuchElementException:
            return None

    def _extrair_numero_associado(self, texto, termo):
        """
        Procura um número associado ao rótulo informado.
        Ex:
        'Dólar 5,223 Euro 5,224' com termo='euro' -> retorna 5,224
        """
        if not texto:
            return None

        texto_limpo = " ".join(texto.split())
        texto_lower = texto_limpo.lower()
        termo_lower = termo.lower()

        pos = texto_lower.find(termo_lower)
        if pos == -1:
            return None

        trecho = texto_limpo[pos + len(termo):]

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