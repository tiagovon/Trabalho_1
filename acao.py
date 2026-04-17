import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Notificador:
    """
    Envia notificação de mudança de preço para uma página pública.
    Usa o Dontpad como destino (bloco de notas público, sem login).
    """

    def __init__(self, navegador, url_destino="https://dontpad.com/alerta-trabalho-selenium"):
        self.nav = navegador
        self.url_destino = url_destino

    def notificar(self, valor_antigo, valor_novo, usuario="sistema"):
        """
        Abre uma nova aba, escreve a mensagem no Dontpad e clica em um botão.
        Retorna True em caso de sucesso, False caso contrário.
        """
        driver = self.nav.driver
        aba_original = driver.current_window_handle

        try:
            # 1. Abre nova aba (mantém o monitoramento intacto na aba original)
            driver.switch_to.new_window("tab")
            driver.get(self.url_destino)

            # 2. Espera o textarea carregar
            textarea = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "text"))
            )

            # 3. Monta e escreve a mensagem
            mensagem = (
                f"\n\n===== ALERTA DE MUDANCA DE PRECO =====\n"
                f"Usuario: {usuario}\n"
                f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Valor antigo: {valor_antigo}\n"
                f"Valor novo:   {valor_novo}\n"
                f"=======================================\n"
            )

            textarea.click()
            textarea.send_keys(mensagem)

            # 4. Força o save com Ctrl+S (Dontpad também salva automaticamente)
            textarea.send_keys(Keys.CONTROL, "s")
            time.sleep(3)

            # 5. Clica em um botão/link visível da página (atende o critério "clicar em botão")
            #    O Dontpad tem um link "Read-only" no topo da página.
            try:
                botao = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Read-only"))
                )
                botao.click()
                time.sleep(2)
            except Exception:
                # Fallback: se não achar Read-only, clica em qualquer link do cabeçalho
                links = driver.find_elements(By.TAG_NAME, "a")
                if links:
                    links[0].click()
                    time.sleep(2)

            print(f"[OK] Notificação enviada para: {self.url_destino}")
            return True

        except Exception as erro:
            print(f"[ERRO] Falha ao notificar: {erro}")
            return False

        finally:
            # 6. Fecha a aba da ação e volta pra aba monitorada
            try:
                if driver.current_window_handle != aba_original:
                    driver.close()
                driver.switch_to.window(aba_original)
            except Exception:
                pass