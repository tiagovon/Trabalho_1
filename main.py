from urllib.parse import urlparse
from navegador import Navegador
from monitor import Monitor


def url_valida(url):
    try:
        r = urlparse(url)
        return all([r.scheme in ("http", "https"), r.netloc])
    except Exception:
        return False


def nome_valido(nome):
    return len(nome) >= 3 and all(c.isalpha() or c.isspace() for c in nome)


def main():
    nome = input("Digite seu nome: ").strip()
    while not nome_valido(nome):
        print("Nome invalido. Use apenas letras, minimo 3 caracteres.")
        nome = input("Digite seu nome: ").strip()

    url = input("Digite a URL: ").strip()
    while not url_valida(url):
        print("URL invalida. Deve comecar com http:// ou https://")
        url = input("Digite a URL: ").strip()

    seletor = input("Digite o texto ou XPATH do valor: ").strip()
    while not seletor:
        print("Seletor nao pode ser vazio.")
        seletor = input("Digite o texto ou XPATH do valor: ").strip()

    nav = Navegador()

    if not nav.acessar(url):
        print("Nao foi possivel abrir a pagina.")
        return

    monitor = Monitor(nav, url, seletor, usuario=nome)
    monitor.iniciar()


if __name__ == "__main__":
    main()