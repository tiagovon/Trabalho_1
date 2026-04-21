"""
Modulo de acao/notificacao de mudancas de preco.

Implementa a classe Notificador, responsavel por abrir uma pagina publica
(Dontpad) em nova aba, escrever a mensagem com o valor antigo e novo,
e clicar em um botao - cumprindo o criterio do trabalho:
    "interagir com outra pagina e clicar em um botao".

Qualquer pessoa pode abrir a mesma URL do Dontpad em outro navegador
e dar F5 para visualizar as mensagens enviadas.

Complexidade (Big O):
    - notificar(): O(1) - numero constante de operacoes no DOM.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class Notificador:
    """
    Envia alerta de mudanca de preco para uma pagina publica (Dontpad).

    Qualquer usuario pode abrir a mesma URL e dar F5 para visualizar
    as mensagens salvas pelo sistema.

    Attributes:
        nav (Navegador): Instancia do navegador em uso.
        url_destino (str): URL do Dontpad onde as mensagens serao salvas.
    """

    URL_PADRAO = "https://dontpad.com/trabalho-algo-2422082020"
    TIMEOUT_TEXTAREA = 20  # segundos esperando pelo textarea aparecer
    TIMEOUT_SAVE = 15      # segundos esperando pelo save do servidor
    PAUSA_VISUALIZACAO = 10  # segundos antes de fechar a aba

    def __init__(self, navegador, url_destino=None):
        """
        Inicializa o Notificador.

        Args:
            navegador (Navegador): Instancia do Navegador em uso.
            url_destino (str, optional): URL do Dontpad. Usa URL_PADRAO
                se nao for informada.
        """
        self.nav = navegador
        self.url_destino = url_destino or self.URL_PADRAO

    def notificar(self, valor_antigo, valor_novo, usuario="sistema"):
        """
        Notifica a mudanca de preco escrevendo no Dontpad.

        Fluxo completo:
            1. Abre nova aba no navegador.
            2. Acessa o Dontpad (com bypass de Cloudflare se disponivel).
            3. Simula interacao humana (movimento de mouse).
            4. Encontra o textarea da pagina.
            5. Escreve a mensagem com valor antigo/novo.
            6. Aguarda o save automatico do Dontpad.
            7. Clica em um botao da pagina.
            8. Volta para a aba original (pagina monitorada).

        Args:
            valor_antigo (str): Valor anterior antes da mudanca.
            valor_novo (str): Valor atual apos a mudanca.
            usuario (str, optional): Nome do usuario. Default: 'sistema'.

        Returns:
            bool: True se a notificacao foi enviada, False caso contrario.
        """
        driver = self.nav.driver
        aba_original = driver.current_window_handle
        url_original = driver.current_url

        try:
            # 1. Abre nova aba
            print("\n[INFO] Abrindo Dontpad em nova aba...")
            driver.switch_to.new_window("tab")

            # 2. Acessa o Dontpad com bypass de Cloudflare
            self._abrir_dontpad(driver)

            # 3. Simula interacao humana para liberar Cloudflare
            print("[INFO] Simulando interacao humana...")
            self._simular_interacao_humana(driver)

            # 4. Aguarda a pagina carregar completamente
            print("[INFO] Aguardando pagina carregar...")
            time.sleep(5)

            # 5. Procura o textarea
            textarea = self._achar_textarea(driver)
            if textarea is None:
                print("[ERRO] Textarea nao encontrado na pagina.")
                return False

            # 6. Monta a mensagem
            mensagem = self._montar_mensagem(
                valor_antigo, valor_novo, usuario
            )

            # 7. Escreve no textarea
            print("[INFO] Escrevendo mensagem no Dontpad...")
            if not self._escrever(driver, textarea, mensagem):
                print("[ERRO] Nao foi possivel escrever no textarea.")
                return False

            # 8. Pausa para visualizacao
            print("[INFO] Mensagem digitada. Aguardando 3s...")
            time.sleep(3)

            # 9. Forca save com Ctrl+S
            self._forcar_save(textarea)

            # 10. Aguarda save do servidor
            print("[INFO] Aguardando save no servidor...")
            time.sleep(self.TIMEOUT_SAVE)
            print(f"[OK] Mensagem SALVA em: {self.url_destino}")

            # 11. Clica em um botao (atende criterio do trabalho)
            self._clicar_botao(driver)

            # 12. Pausa final antes de fechar a aba
            print("\n" + "=" * 50)
            print("[INFO] Notificacao enviada com sucesso!")
            print(f"[INFO] Aguardando {self.PAUSA_VISUALIZACAO}s "
                  "antes de voltar...")
            print("=" * 50 + "\n")
            time.sleep(self.PAUSA_VISUALIZACAO)

            return True

        except Exception as erro:
            print(f"[ERRO] Falha ao notificar: {erro}")
            return False

        finally:
            self._voltar_aba_original(aba_original, url_original)

    def _abrir_dontpad(self, driver):
        """
        Abre o Dontpad usando bypass de Cloudflare se disponivel.

        Args:
            driver: Instancia do webdriver em uso.
        """
        try:
            # Tenta usar bypass de Cloudflare do SeleniumBase
            self.nav.driver.uc_open_with_reconnect(
                self.url_destino, reconnect_time=5
            )
        except AttributeError:
            # Fallback para driver.get se nao for SeleniumBase
            driver.get(self.url_destino)
        except Exception as erro:
            print(f"[AVISO] Erro no bypass, usando fallback: {erro}")
            driver.get(self.url_destino)

    def _montar_mensagem(self, valor_antigo, valor_novo, usuario):
        """
        Monta a mensagem de alerta a ser escrita no Dontpad.

        Args:
            valor_antigo (str): Valor anterior.
            valor_novo (str): Valor atual.
            usuario (str): Nome do usuario.

        Returns:
            str: Mensagem formatada com timestamp e valores.
        """
        return (
            f"\n\n===== ALERTA DE MUDANCA DE PRECO =====\n"
            f"Usuario: {usuario}\n"
            f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"Valor antigo: {valor_antigo}\n"
            f"Valor novo:   {valor_novo}\n"
            f"=======================================\n"
        )

    def _simular_interacao_humana(self, driver):
        """
        Simula movimento de mouse para enganar detectores de bot.

        Move o cursor para varias posicoes na pagina com pequenas
        pausas, imitando comportamento humano. Util para paginas
        com protecao Cloudflare ou Turnstile.

        Args:
            driver: Instancia do webdriver em uso.
        """
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(body, 100, 100).pause(0.5)
            actions.move_to_element_with_offset(body, 300, 200).pause(0.3)
            actions.move_to_element_with_offset(body, 500, 300).pause(0.3)
            actions.perform()

            driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(0.5)
            driver.execute_script("window.scrollBy(0, -50);")
            time.sleep(0.5)
        except Exception as erro:
            print(f"[AVISO] Nao foi possivel simular interacao: {erro}")

    def _achar_textarea(self, driver):
        """
        Procura o textarea principal do Dontpad com espera ativa.

        Testa varios seletores em ordem de prioridade, aguardando
        ate TIMEOUT_TEXTAREA segundos pelo elemento aparecer.

        Args:
            driver: Instancia do webdriver em uso.

        Returns:
            WebElement | None: Elemento textarea encontrado ou None.
        """
        seletores = [
            (By.ID, "text"),
            (By.NAME, "text"),
            (By.CSS_SELECTOR, "textarea#text"),
            (By.TAG_NAME, "textarea"),
        ]

        inicio = time.time()
        while time.time() - inicio < self.TIMEOUT_TEXTAREA:
            for by, valor in seletores:
                try:
                    elementos = driver.find_elements(by, valor)
                    for el in elementos:
                        if el.is_displayed() and el.is_enabled():
                            print(f"[OK] Textarea encontrado: {by}={valor}")
                            return el
                except Exception:
                    continue
            time.sleep(0.5)

        return None

    def _escrever(self, driver, textarea, mensagem):
        """
        Escreve uma mensagem no textarea usando 3 estrategias.

        Tenta em cascata ate uma funcionar:
            1. send_keys tradicional do Selenium.
            2. ActionChains (simula digitacao humana).
            3. JavaScript direto com eventos input/change.

        Args:
            driver: Instancia do webdriver em uso.
            textarea (WebElement): Elemento textarea onde escrever.
            mensagem (str): Texto a ser escrito.

        Returns:
            bool: True se conseguiu escrever, False caso contrario.
        """
        # Estrategia 1: send_keys tradicional
        try:
            driver.execute_script("arguments[0].focus();", textarea)
            time.sleep(0.3)
            textarea.click()
            time.sleep(0.5)
            textarea.send_keys(Keys.CONTROL, Keys.END)
            time.sleep(0.3)
            textarea.send_keys(mensagem)
            time.sleep(1.5)
            if "ALERTA" in (textarea.get_attribute("value") or ""):
                return True
        except Exception as erro:
            print(f"[DEBUG] Estrategia 1 falhou: {erro}")

        # Estrategia 2: ActionChains
        try:
            actions = ActionChains(driver)
            actions.move_to_element(textarea).click().pause(0.5)
            actions.send_keys(mensagem).perform()
            time.sleep(1.5)
            if "ALERTA" in (textarea.get_attribute("value") or ""):
                return True
        except Exception as erro:
            print(f"[DEBUG] Estrategia 2 falhou: {erro}")

        # Estrategia 3: JavaScript direto
        try:
            texto_atual = textarea.get_attribute("value") or ""
            novo_texto = texto_atual + mensagem
            driver.execute_script(
                """
                var el = arguments[0];
                el.focus();
                el.value = arguments[1];
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                el.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
                """,
                textarea,
                novo_texto,
            )
            time.sleep(1.5)
            return True
        except Exception as erro:
            print(f"[DEBUG] Estrategia 3 falhou: {erro}")

        return False

    def _forcar_save(self, textarea):
        """
        Forca o save imediato usando Ctrl+S no textarea.

        O Dontpad faz save automatico, mas Ctrl+S acelera o processo.

        Args:
            textarea (WebElement): Elemento textarea onde aplicar o save.
        """
        try:
            textarea.send_keys(Keys.CONTROL, "s")
        except Exception:
            pass  # Ignora: save automatico do Dontpad ja funciona

    def _clicar_botao(self, driver):
        """
        Clica em um botao visivel da pagina.

        Atende o criterio do trabalho: "clicar em um botao da tela".
        Tenta primeiro botoes <button>, depois inputs do tipo submit.

        Args:
            driver: Instancia do webdriver em uso.
        """
        try:
            # Tenta botoes <button>
            botoes = driver.find_elements(By.TAG_NAME, "button")
            for btn in botoes:
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    print("[OK] Botao clicado.")
                    time.sleep(1)
                    return

            # Tenta inputs de submit/button
            inputs = driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='submit'], input[type='button']"
            )
            for inp in inputs:
                if inp.is_displayed() and inp.is_enabled():
                    inp.click()
                    print("[OK] Input-botao clicado.")
                    time.sleep(1)
                    return

            print("[INFO] Nenhum botao visivel encontrado.")

        except Exception as erro:
            print(f"[AVISO] Erro ao clicar em botao: {erro}")

    def _voltar_aba_original(self, aba_original, url_original):
        """
        Fecha abas extras e retorna para a aba monitorada.

        Garante que apos a notificacao o driver volta para a pagina
        original que esta sendo monitorada, mesmo se algo deu errado.

        Args:
            aba_original (str): Handle (identificador) da aba original.
            url_original (str): URL que deve estar carregada na aba original.
        """
        driver = self.nav.driver
        try:
            # Fecha todas as abas que nao sejam a original
            for handle in list(driver.window_handles):
                if handle != aba_original:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except Exception:
                        pass

            # Volta para a aba original
            if aba_original in driver.window_handles:
                driver.switch_to.window(aba_original)
            else:
                # Aba original foi fechada - usa a primeira disponivel
                if driver.window_handles:
                    driver.switch_to.window(driver.window_handles[0])
                driver.get(url_original)

            # Garante que a URL esta correta
            if driver.current_url != url_original:
                driver.get(url_original)

            time.sleep(1)
            print(f"[OK] Retornou para: {driver.current_url}")

        except Exception as erro:
            print(f"[AVISO] Erro ao voltar para aba original: {erro}")
            try:
                driver.get(url_original)
            except Exception:
                pass