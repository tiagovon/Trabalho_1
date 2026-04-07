from navegador import Navegador
from monitor import Monitor
from utils import validar_url, ler_inteiro_positivo


def main():
    nome_usuario = input("Digite seu nome: ").strip()
    if len(nome_usuario) < 3 or not all(parte.isalpha() for parte in nome_usuario.split()):
        print("Nome inválido. Digite ao menos 3 letras, usando apenas caracteres.")
        return

    url = input("Digite a URL: ").strip()
    if not validar_url(url):
        print("URL inválida. Use http:// ou https://")
        return

    tipo_busca = input("Como deseja procurar o valor? Digite 'xpath' ou 'texto': ").strip().lower()
    if tipo_busca not in ("xpath", "texto"):
        print("Tipo de busca inválido.")
        return

    seletor = input("Agora digite o conteúdo a procurar (ex: Dólar) ou o XPATH do elemento: ").strip()
    if not seletor:
        print("Seletor não pode ser vazio.")
        return

    intervalo = ler_inteiro_positivo("Digite o intervalo de monitoramento em segundos: ")
    timeout = ler_inteiro_positivo("Digite o timeout de carregamento em segundos: ")

    nav = Navegador(timeout=timeout)

    if not nav.acessar(url):
        print("Não foi possível abrir a página.")
        return

    monitor = Monitor(
        navegador=nav,
        url_monitorada=url,
        tipo_busca=tipo_busca,
        seletor=seletor,
        intervalo=intervalo,
        nome_usuario=nome_usuario,
    )
    monitor.iniciar()


if __name__ == "__main__":
    main()