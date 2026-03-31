from navegador import Navegador
from monitor import Monitor


def main():
    url = input("Digite a URL: ").strip()
    seletor = input("Digite o texto ou XPATH do valor: ").strip()

    nav = Navegador()

    if not nav.acessar(url):
        print("Não foi possível abrir a página.")
        return

    monitor = Monitor(nav, url, seletor)
    monitor.iniciar()


if __name__ == "__main__":
    main()