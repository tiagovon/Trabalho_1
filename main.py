"""
Modulo principal do sistema de monitoramento de precos.

Este modulo e o ponto de entrada da aplicacao. Solicita ao usuario:
- Nome (valida apenas letras e espacos, minimo 3 caracteres)
- URL da pagina a ser monitorada (valida formato http/https)
- Seletor (texto ou XPath do valor a ser monitorado)

Apos validar as entradas, inicializa o navegador e inicia o monitoramento
continuo da pagina informada.

Exemplo de uso:
    $ python main.py
    Digite seu nome: Tiago
    Digite a URL: https://coinmarketcap.com/currencies/bitcoin/
    Digite o texto ou XPATH do valor: Bitcoin price
"""

import sys
from urllib.parse import urlparse

from navegador import Navegador
from monitor import Monitor


def url_valida(url):
    """
    Valida se uma URL tem formato correto.

    A URL deve ter esquema http ou https e um dominio valido.

    Args:
        url (str): URL a ser validada.

    Returns:
        bool: True se a URL for valida, False caso contrario.

    Example:
        >>> url_valida("https://google.com")
        True
        >>> url_valida("google.com")
        False
    """
    try:
        resultado = urlparse(url)
        return all([
            resultado.scheme in ("http", "https"),
            resultado.netloc,
        ])
    except Exception:
        return False


def nome_valido(nome):
    """
    Valida se um nome esta no formato correto.

    O nome deve ter pelo menos 3 caracteres e conter apenas letras e espacos.

    Args:
        nome (str): Nome a ser validado.

    Returns:
        bool: True se o nome for valido, False caso contrario.

    Example:
        >>> nome_valido("Tiago")
        True
        >>> nome_valido("Ti")
        False
        >>> nome_valido("Tiago123")
        False
    """
    if len(nome) < 3:
        return False
    return all(c.isalpha() or c.isspace() for c in nome)


def pedir_entrada(mensagem):
    """
    Solicita entrada do usuario garantindo ordem correta no terminal.

    Usa sys.stdout.write com flush para forcar a mensagem a aparecer
    ANTES do cursor de digitacao, evitando problemas de buffer no
    Git Bash e outros terminais.

    Args:
        mensagem (str): Mensagem a ser exibida como prompt.

    Returns:
        str: Texto digitado pelo usuario, sem espacos extras.
    """
    sys.stdout.write(mensagem)
    sys.stdout.flush()
    return input().strip()


def main():
    """
    Funcao principal. Orquestra o fluxo do programa.

    Passos:
        1. Solicita e valida o nome do usuario.
        2. Solicita e valida a URL a ser monitorada.
        3. Solicita o seletor (texto ou XPath).
        4. Inicia o navegador e acessa a URL.
        5. Dispara o monitoramento continuo.
    """
    # Validacao do nome
    nome = pedir_entrada("Digite seu nome: ")
    while not nome_valido(nome):
        print("Nome invalido. Use apenas letras, minimo 3 caracteres.",
              flush=True)
        nome = pedir_entrada("Digite seu nome: ")

    # Validacao da URL
    url = pedir_entrada("Digite a URL: ")
    while not url_valida(url):
        print("URL invalida. Deve comecar com http:// ou https://",
              flush=True)
        url = pedir_entrada("Digite a URL: ")

    # Validacao do seletor
    seletor = pedir_entrada("Digite o texto ou XPATH do valor: ")
    while not seletor:
        print("Seletor nao pode ser vazio.", flush=True)
        seletor = pedir_entrada("Digite o texto ou XPATH do valor: ")

    print("\n[INFO] Iniciando navegador...", flush=True)

    nav = Navegador()

    if not nav.acessar(url):
        print("Nao foi possivel abrir a pagina.", flush=True)
        return

    print(f"[INFO] Monitoramento iniciado por: {nome}")
    print(f"[INFO] URL: {url}")
    print(f"[INFO] Seletor: {seletor}\n")

    monitor = Monitor(nav, url, seletor, usuario=nome)
    monitor.iniciar()


if __name__ == "__main__":
    main()