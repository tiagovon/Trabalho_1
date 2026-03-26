import time


class Monitor:
    def __init__(self, navegador, seletor):
        self.nav = navegador
        self.seletor = seletor
        self.valor_anterior = None

    def iniciar(self):
        while True:
            valor_atual = self.nav.pegar_valor(self.seletor)

            if valor_atual is None:
                print("Valor não encontrado.")
                time.sleep(5)
                continue

            if self.valor_anterior is None:
                self.valor_anterior = valor_atual
                print(f"Valor inicial: {valor_atual}")

            elif valor_atual != self.valor_anterior:
                print(f"Alteração detectada: {self.valor_anterior} -> {valor_atual}")
                self.acao(self.valor_anterior, valor_atual)
                self.valor_anterior = valor_atual

            else:
                print(f"Sem alteração: {valor_atual}")

            time.sleep(5)

    def acao(self, valor_antigo, valor_novo):
        print(f"Ação executada | antigo: {valor_antigo} | novo: {valor_novo}")