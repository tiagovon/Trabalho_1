import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException


class Navegador:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def acessar(self, url):
        try:
            self.driver.get(url)
            return True
        except WebDriverException as erro:
            print(f"Erro ao acessar a URL: {erro}")
            return False

    def pegar_valor(self, seletor):
        """
        Se o usuário digitar um texto como 'Dólar',
        tenta encontrar esse texto na página e retornar apenas o valor numérico próximo.
        Se digitar XPath, usa o XPath diretamente.
        """
        try:
            # Caso o usuário informe um XPath
            if seletor.startswith("/") or seletor.startswith("("):
                elemento = self.driver.find_element(By.XPATH, seletor)
                return self._extrair_numero(elemento.text)

            # Caso o usuário informe texto comum, ex: Dólar
            texto = seletor.strip().lower()

            xpath_texto = (
                "//*[contains("
                "translate(normalize-space(.), "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÃÂÉÈÊÍÌÎÓÒÕÔÚÙÛÇ', "
                "'abcdefghijklmnopqrstuvwxyzáàãâéèêíìîóòõôúùûç'"
                "), "
                f"'{texto}'"
                ")]"
            )

            elementos = self.driver.find_elements(By.XPATH, xpath_texto)

            for elemento in elementos:
                # tenta pegar número no próprio texto do elemento
                numero = self._extrair_numero(elemento.text)
                if numero:
                    return numero

                # tenta pegar número no texto do pai
                try:
                    pai = elemento.find_element(By.XPATH, "..")
                    numero = self._extrair_numero(pai.text)
                    if numero:
                        return numero
                except Exception:
                    pass

                # tenta pegar número no próximo irmão
                try:
                    irmao = elemento.find_element(By.XPATH, "./following-sibling::*[1]")
                    numero = self._extrair_numero(irmao.text)
                    if numero:
                        return numero
                except Exception:
                    pass

            return None

        except NoSuchElementException:
            return None

    def _extrair_numero(self, texto):
        """
        Extrai apenas o número do texto.
        Exemplos:
        'Dólar 5,656' -> '5,656'
        'R$ 132.097,00' -> '132.097,00'
        """
        if not texto:
            return None

        padrao = r"\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?"
        resultado = re.search(padrao, texto)

        if resultado:
            return resultado.group(0)

        return None

    def fechar(self):
        self.driver.quit()