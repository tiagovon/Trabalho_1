from navegador import Navegador
from monitor import Monitor


def main():
    url = input("Digite a URL: ").strip()
    seletor = input("Digite o texto ou XPATH do valor: ").strip()

    nav = Navegador()

    if not nav.acessar(url):
        print("Não foi possível abrir a página. Verifique a URL ou sua conexão.")
        return

    monitor = Monitor(nav, seletor)
    monitor.iniciar()


if __name__ == "__main__":
    main()