def validar_url(url):
    return url.startswith("http://") or url.startswith("https://")


def ler_inteiro_positivo(mensagem):
    valor = input(mensagem).strip()
    if not valor.isdigit() or int(valor) <= 0:
        raise ValueError("O valor deve ser um inteiro positivo.")
    return int(valor)