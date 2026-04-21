import unittest
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse


# Funcoes importadas do main (repete aqui pra testar sem rodar o Chrome)
def url_valida(url):
    try:
        r = urlparse(url)
        return all([r.scheme in ("http", "https"), r.netloc])
    except Exception:
        return False


def nome_valido(nome):
    return len(nome) >= 3 and all(c.isalpha() or c.isspace() for c in nome)


class TestValidacoes(unittest.TestCase):
    """Testes das funcoes de validacao de entrada."""

    def test_url_valida_http(self):
        self.assertTrue(url_valida("http://exemplo.com"))

    def test_url_valida_https(self):
        self.assertTrue(url_valida("https://coinmarketcap.com/currencies/bitcoin/"))

    def test_url_invalida_sem_protocolo(self):
        self.assertFalse(url_valida("exemplo.com"))

    def test_url_invalida_vazia(self):
        self.assertFalse(url_valida(""))

    def test_url_invalida_ftp(self):
        self.assertFalse(url_valida("ftp://exemplo.com"))

    def test_nome_valido_simples(self):
        self.assertTrue(nome_valido("Tiago"))

    def test_nome_valido_composto(self):
        self.assertTrue(nome_valido("Tiago Silva"))

    def test_nome_invalido_curto(self):
        self.assertFalse(nome_valido("Ti"))

    def test_nome_invalido_numeros(self):
        self.assertFalse(nome_valido("Tiago123"))

    def test_nome_invalido_especiais(self):
        self.assertFalse(nome_valido("Tiago@"))


class TestExtracaoNumero(unittest.TestCase):
    """Testes da extracao de numeros do texto."""

    def setUp(self):
        from navegador import Navegador
        self.nav = Navegador.__new__(Navegador)  # cria sem chamar __init__

    def test_extrair_numero_simples(self):
        self.assertEqual(self.nav._extrair_numero("123"), "123")

    def test_extrair_numero_decimal(self):
        self.assertEqual(self.nav._extrair_numero("R$ 99,99"), "99,99")

    def test_extrair_numero_milhar(self):
        resultado = self.nav._extrair_numero("70.432,55")
        self.assertIn("70", resultado)

    def test_extrair_numero_texto_sem_numero(self):
        self.assertIsNone(self.nav._extrair_numero("sem numero aqui"))

    def test_extrair_numero_texto_vazio(self):
        self.assertIsNone(self.nav._extrair_numero(""))


class TestLogger(unittest.TestCase):
    """Testes do logger."""

    def test_logger_cria_arquivo(self):
        import os
        from logger import Logger

        arquivo_teste = "test_log.log"
        if os.path.exists(arquivo_teste):
            os.remove(arquivo_teste)

        logger = Logger(nome_arquivo=arquivo_teste, usuario="teste")
        logger.log("mensagem de teste")

        self.assertTrue(os.path.exists(arquivo_teste))

        with open(arquivo_teste, "r", encoding="utf-8") as f:
            conteudo = f.read()

        self.assertIn("mensagem de teste", conteudo)
        self.assertIn("teste", conteudo)

        os.remove(arquivo_teste)


if __name__ == "__main__":
    unittest.main()