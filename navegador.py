import re
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


class Navegador:
    def __init__(self):
        self.driver = Driver(
            uc=True,
            headless=False,
            locale_code="pt-BR",
            do_not_track=True,
            disable_features="TranslateUI,Translate",
        )
        self.driver.maximize_window()

    def acessar(self, url):
        try:
            if "dontpad" in url:
                self.driver.uc_open_with_reconnect(url, reconnect_time=4)
            else:
                self.driver.get(url)
            return True
        except WebDriverException as erro:
            print(f"Erro ao acessar a URL: {erro}")
            return False

    def pegar_valor(self, seletor):
        try:
            # Se comeca com / ou ( ou // e XPath -> usa direto
            if seletor.startswith("/") or seletor.startswith("("):
                elemento = self.driver.find_element(By.XPATH, seletor)
                return self._extrair_numero(elemento.text)

            # Caso contrario, busca por texto
            termo = seletor.strip().lower()
            body = self.driver.find_element(By.TAG_NAME, "body")
            texto_pagina = body.text  # sem split/join pra preservar quebras de linha

            return self._extrair_melhor_numero(texto_pagina, termo)

        except Exception as e:
            print(f"[DEBUG] Erro ao pegar valor: {e}")
            return None

    def _extrair_melhor_numero(self, texto, termo):
        """
        Estrategia melhorada:
        - Procura TODAS as ocorrencias do termo na pagina
        - Pra cada ocorrencia, pega o numero mais proximo (nos 100 chars seguintes)
        - Escolhe o MAIOR numero encontrado (geralmente e o preco principal)
        """
        if not texto:
            return None

        texto_lower = texto.lower()
        termo_lower = termo.lower()

        # Padrao de numero (aceita formato BR e US)
        padrao = r"[\$R\$€£]?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"

        numeros_candidatos = []

        # Procura TODAS as ocorrencias do termo
        pos = 0
        while True:
            pos = texto_lower.find(termo_lower, pos)
            if pos == -1:
                break

            # Pega os 150 caracteres depois do termo
            trecho = texto[pos + len(termo_lower):pos + len(termo_lower) + 150]

            # Procura o primeiro numero no trecho
            match = re.search(padrao, trecho)
            if match:
                numero_str = match.group(1)
                # Converte pra float pra comparar
                try:
                    # Normaliza: remove pontos de milhar, troca virgula por ponto
                    if "," in numero_str and "." in numero_str:
                        # Se tem os dois, o ultimo e o decimal
                        if numero_str.rfind(",") > numero_str.rfind("."):
                            # Formato BR: 70.432,55
                            valor = float(numero_str.replace(".", "").replace(",", "."))
                        else:
                            # Formato US: 70,432.55
                            valor = float(numero_str.replace(",", ""))
                    elif "," in numero_str:
                        # So virgula: pode ser decimal BR ou milhar US
                        partes = numero_str.split(",")
                        if len(partes[-1]) <= 2:  # ex: 70,55 = decimal BR
                            valor = float(numero_str.replace(",", "."))
                        else:  # ex: 70,432 = milhar US
                            valor = float(numero_str.replace(",", ""))
                    elif "." in numero_str:
                        partes = numero_str.split(".")
                        if len(partes[-1]) <= 2:  # decimal US
                            valor = float(numero_str)
                        else:  # milhar BR
                            valor = float(numero_str.replace(".", ""))
                    else:
                        valor = float(numero_str)

                    numeros_candidatos.append((valor, numero_str))
                except ValueError:
                    pass

            pos += len(termo_lower)

        if not numeros_candidatos:
            return None

        # Escolhe o MAIOR numero (geralmente o preco principal)
        maior = max(numeros_candidatos, key=lambda x: x[0])
        return maior[1]

    def _extrair_numero(self, texto):
        if not texto:
            return None

        padrao = r"\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?"
        match = re.search(padrao, texto)

        if match:
            return match.group(0)

        return None

    def fechar(self):
        self.driver.quit()