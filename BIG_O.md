import os
from datetime import datetime


class Logger:
    """Registra todas as acoes do sistema em arquivo de log."""

    def __init__(self, nome_arquivo="acoes.log", usuario="sistema"):
        self.arquivo = nome_arquivo
        self.usuario = usuario
        if not os.path.exists(self.arquivo):
            with open(self.arquivo, "w", encoding="utf-8") as f:
                f.write(f"=== LOG INICIADO EM {datetime.now()} ===\n")

    def log(self, mensagem):
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linha = f"[{timestamp}] [{self.usuario}] {mensagem}\n"
        with open(self.arquivo, "a", encoding="utf-8") as f:
            f.write(linha)
        print(linha.strip())