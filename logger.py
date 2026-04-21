"""
Modulo de logging do sistema de monitoramento.

Implementa a classe Logger, responsavel por registrar todas as acoes
do sistema em um arquivo de log persistente, com timestamp e usuario.

Atende o criterio do trabalho: "log de acoes do usuario" (+1 ponto).

Complexidade (Big O):
    - log(): O(1) para registro (mais O(s) do I/O, onde s = tamanho
      da mensagem, que e constante na pratica).
"""

import os
from datetime import datetime


class Logger:
    """
    Registra todas as acoes do sistema em arquivo de log.

    Cria (ou abre) um arquivo de log e adiciona linhas com timestamp,
    nome do usuario e mensagem. Tambem imprime no console para
    visualizacao em tempo real.

    Attributes:
        arquivo (str): Caminho do arquivo de log.
        usuario (str): Nome do usuario que esta executando o sistema.
    """

    def __init__(self, nome_arquivo="acoes.log", usuario="sistema"):
        """
        Inicializa o logger e cria o arquivo se nao existir.

        Args:
            nome_arquivo (str, optional): Caminho do arquivo de log.
                Default: 'acoes.log'.
            usuario (str, optional): Nome do usuario logado.
                Default: 'sistema'.
        """
        self.arquivo = nome_arquivo
        self.usuario = usuario
        if not os.path.exists(self.arquivo):
            with open(self.arquivo, "w", encoding="utf-8") as f:
                f.write(f"=== LOG INICIADO EM {datetime.now()} ===\n")

    def log(self, mensagem):
        """
        Registra uma mensagem no arquivo de log e no console.

        A linha gravada tem formato:
            [DD/MM/AAAA HH:MM:SS] [usuario] mensagem

        Args:
            mensagem (str): Mensagem a ser registrada.
        """
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linha = f"[{timestamp}] [{self.usuario}] {mensagem}\n"

        with open(self.arquivo, "a", encoding="utf-8") as f:
            f.write(linha)

        print(linha.strip())