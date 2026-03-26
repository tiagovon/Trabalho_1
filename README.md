📖 Descrição

Este projeto consiste no desenvolvimento de um assistente automatizado de monitoramento de preços em páginas web, capaz de identificar alterações em valores exibidos em sites e executar ações automáticas em outra página.

O sistema foi projetado para funcionar com qualquer página web, sem conhecimento prévio da estrutura HTML, sendo necessário apenas que o usuário informe:

-A URL do site
-O XPath do elemento a ser monitorado
🎯 Objetivo
-Monitorar um valor (ex: preço) em uma página web
-Detectar alterações automaticamente
-Registrar as mudanças
-Interagir com outra página, informando:
    -Valor anterior
    -Novo valor
-Executar uma ação (ex: clicar em botão, enviar formulário)
⚙️ Tecnologias Utilizadas
-Python 3
-Selenium
-Logging
-Unittest (testes automatizados)

🏗️ Estrutura do Projeto
assistente_leilao/
│
├── main.py              # Arquivo principal
├── monitor.py           # Lógica de monitoramento
├── navegador.py         # Controle do navegador
├── logger.py            # Sistema de logs
│
├── tests/               # Testes automatizados
│   └── test_monitor.py
│
├── docs/                # Documentação (Sphinx/MkDocs)
│
└── README.md
🚀 Como Executar o Projeto
1️⃣ Instalar dependências
pip install selenium
2️⃣ Baixar o WebDriver
Chrome: https://chromedriver.chromium.org/
Certifique-se de que está no PATH
3️⃣ Executar o sistema
python main.py
4️⃣ Entrada do usuário

O sistema solicitará:

Digite a URL:
Digite o XPath do valor:
Digite seu nome: