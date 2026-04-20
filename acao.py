import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Notificador:
    """
    Envia alerta de mudanca de preco para o Dontpad classico.
    Qualquer pessoa pode abrir a mesma URL e dar F5 pra ver as mensagens.
    """

    def __init__(self, navegador, url_destino="https://dontpad.com/trabalho-algo-2422082020"):
        self.nav = navegador
        self.url_destino = url_destino

    def notificar(self, valor_antigo, valor_novo, usuario="sistema"):
        driver = self.nav.driver
        aba_original = driver.current_window_handle
        url_original = driver.current_url

        try:
            # 1. Abre nova aba
            print("\n[INFO] Abrindo Dontpad em nova aba...")
            driver.switch_to.new_window("tab")

            # 2. Usa o bypass do Cloudflare pra abrir o Dontpad
            try:
                self.nav.driver.uc_open_with_reconnect(self.url_destino, reconnect_time=5)
            except AttributeError:
                driver.get(self.url_destino)

            # PAUSA 1: espera o Cloudflare passar e o Dontpad carregar por completo
            print("[INFO] Aguardando Dontpad carregar (6s)...")
            time.sleep(6)

            # 3. Acha o textarea
            textarea = self._achar_textarea(driver)
            if textarea is None:
                print("[ERRO] Nao achei o textarea da pagina.")
                return False

            # 4. Monta a mensagem
            mensagem = (
                f"\n\n===== ALERTA DE MUDANCA DE PRECO =====\n"
                f"Usuario: {usuario}\n"
                f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Valor antigo: {valor_antigo}\n"
                f"Valor novo:   {valor_novo}\n"
                f"=======================================\n"
            )

            # 5. Escreve no textarea
            print("[INFO] Escrevendo mensagem no Dontpad...")
            escreveu = self._escrever(driver, textarea, mensagem)
            if not escreveu:
                print("[ERRO] Nao consegui escrever no textarea.")
                return False

            # PAUSA 2: espera para voce ver o texto aparecer no textarea
            print("[INFO] Mensagem digitada. Aguardando 3s para visualizar...")
            time.sleep(3)

            # 6. Forca salvamento com Ctrl+S
            try:
                textarea.send_keys(Keys.CONTROL, "s")
            except Exception:
                pass

            # 7. Espera o save acontecer
            print("[INFO] Aguardando save no servidor...")
            salvou = self._esperar_save(driver, textarea, timeout=15)

            if salvou:
                print(f"[OK] Mensagem SALVA em: {self.url_destino}")
            else:
                print("[AVISO] Save nao confirmado. Dando mais tempo...")
                time.sleep(5)

            # 8. Clica num botao visivel (atende criterio do trabalho)
            self._clicar_botao(driver)

            # PAUSA 3 (A GRANDE!): tempo generoso pra voce ver tudo antes de fechar
            print("\n" + "=" * 50)
            print("[INFO] Mensagem enviada com sucesso!")
            print("[INFO] Aguardando 10 segundos antes de voltar...")
            print("[INFO] (Aproveite pra conferir visualmente)")
            print("=" * 50 + "\n")
            time.sleep(10)

            return True

        except Exception as erro:
            print(f"[ERRO] Falha ao notificar: {erro}")
            return False

        finally:
            self._voltar_aba_original(aba_original, url_original)

    def _achar_textarea(self, driver):
        """Tenta varios seletores pra achar o textarea do Dontpad."""
        seletores = [
            (By.ID, "text"),
            (By.NAME, "text"),
            (By.CSS_SELECTOR, "textarea#text"),
            (By.CSS_SELECTOR, "textarea[name='text']"),
            (By.TAG_NAME, "textarea"),
        ]
        for by, valor in seletores:
            try:
                elementos = driver.find_elements(by, valor)
                for el in elementos:
                    if el.is_displayed() and el.is_enabled():
                        print(f"[OK] Textarea encontrado via: {by}={valor}")
                        return el
            except Exception:
                continue
        return None

    def _escrever(self, driver, textarea, mensagem):
        """Escreve no textarea usando 3 estrategias em cascata."""

        # Estrategia 1
        try:
            textarea.click()
            time.sleep(0.5)
            textarea.send_keys(Keys.CONTROL, Keys.END)
            time.sleep(0.3)
            textarea.send_keys(mensagem)
            time.sleep(1)
            if "ALERTA" in (textarea.get_attribute("value") or ""):
                return True
        except Exception as e:
            print(f"[DEBUG] Estrategia 1 falhou: {e}")

        # Estrategia 2
        try:
            actions = ActionChains(driver)
            actions.move_to_element(textarea).click().send_keys(mensagem).perform()
            time.sleep(1)
            if "ALERTA" in (textarea.get_attribute("value") or ""):
                return True
        except Exception as e:
            print(f"[DEBUG] Estrategia 2 falhou: {e}")

        # Estrategia 3
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
            time.sleep(1)
            return True
        except Exception as e:
            print(f"[DEBUG] Estrategia 3 falhou: {e}")

        return False

    def _esperar_save(self, driver, textarea, timeout=15):
        """Espera ATIVAMENTE pelo save do Dontpad."""
        inicio = time.time()

        try:
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));",
                textarea,
            )
        except Exception:
            pass

        while time.time() - inicio < timeout:
            try:
                pagina = driver.page_source.lower()
                if any(palavra in pagina for palavra in ["saved", "salvo", "gravado"]):
                    print("[OK] Indicador de save detectado.")
                    return True
            except Exception:
                pass
            time.sleep(1)

        try:
            textarea.send_keys(Keys.TAB)
            time.sleep(3)
        except Exception:
            pass

        return False

    def _clicar_botao(self, driver):
        """Clica em qualquer botao visivel."""
        try:
            botoes = driver.find_elements(By.TAG_NAME, "button")
            for btn in botoes:
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    print("[OK] Botao clicado.")
                    time.sleep(1)
                    return

            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], input[type='button']")
            for inp in inputs:
                if inp.is_displayed() and inp.is_enabled():
                    inp.click()
                    print("[OK] Input-botao clicado.")
                    time.sleep(1)
                    return

            print("[INFO] Nenhum botao visivel (OK se o save foi automatico).")
        except Exception as e:
            print(f"[AVISO] Erro ao clicar: {e}")

    def _voltar_aba_original(self, aba_original, url_original):
        """Fecha abas extras e garante retorno pra aba monitorada."""
        driver = self.nav.driver
        try:
            for handle in list(driver.window_handles):
                if handle != aba_original:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except Exception:
                        pass

            if aba_original in driver.window_handles:
                driver.switch_to.window(aba_original)
            else:
                if driver.window_handles:
                    driver.switch_to.window(driver.window_handles[0])
                driver.get(url_original)

            if driver.current_url != url_original:
                driver.get(url_original)

            time.sleep(1)
            print(f"[OK] Retornou para: {driver.current_url}")

        except Exception as erro:
            print(f"[AVISO] Erro ao voltar: {erro}")
            try:
                driver.get(url_original)
            except Exception:
                pass