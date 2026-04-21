# Análise de Complexidade (Big O)

Análise da complexidade assintótica das principais funções do sistema de
monitoramento de preços.

## Definições

- **n** = tamanho do texto da página monitorada (em caracteres)
- **k** = número de ocorrências do termo de busca no texto
- **t** = número de iterações do loop de monitoramento

## Módulo `navegador.py`

### `Navegador.acessar(url)`
- **Complexidade: O(1)**
- Justificativa: Executa uma única chamada de navegação. O tempo varia com
  a latência da rede, mas não com o tamanho da entrada.

### `Navegador.pegar_valor(seletor)`
- **Complexidade: O(n)** no caminho textual, **O(1)** no caminho XPath.
- Justificativa (XPath): acesso direto ao elemento via índice DOM.
- Justificativa (textual): percorre todo o texto do body uma vez.

### `Navegador._extrair_numero(texto)`
- **Complexidade: O(n)** onde n é o tamanho do texto.
- Justificativa: `re.search` é linear no tamanho do texto de entrada.

### `Navegador._extrair_melhor_numero(texto, termo)`
- **Complexidade: O(n * k)**
- Justificativa: faz até k buscas de termo no texto (cada uma O(n)) e
  para cada ocorrência aplica regex em janela de tamanho constante
  (O(1) por ocorrência).

### `Navegador._converter_para_float(numero_str)`
- **Complexidade: O(m)** onde m é o tamanho da string do número (m << n).
- Na prática: **O(1)**, pois m é limitado (números têm poucos dígitos).

## Módulo `monitor.py`

### `Monitor.iniciar()`
- **Complexidade: O(t * n)**
- Justificativa: loop infinito onde cada iteração faz:
  - 1 chamada a `pegar_valor()`: O(n)
  - 1 comparação de strings: O(1)
  - Eventualmente 1 chamada a `acao()`: O(1)

### `Monitor.acao(valor_antigo, valor_novo)`
- **Complexidade: O(1)** + complexidade do Notificador.

## Módulo `acao.py`

### `Notificador.notificar(valor_antigo, valor_novo, usuario)`
- **Complexidade: O(1)**
- Justificativa: número fixo de operações no DOM (abrir aba, achar
  textarea, escrever mensagem de tamanho constante, clicar botão, fechar).
  Não depende do tamanho da entrada.

## Módulo `main.py`

### `main.url_valida(url)` e `main.nome_valido(nome)`
- **Complexidade: O(m)** onde m é o tamanho da string.
- Justificativa: percorre a string uma vez para validação.

## Módulo `logger.py`

### `Logger.log(mensagem)`
- **Complexidade: O(1)** para o log em si (mais O(s) da operação de I/O,
  onde s é o tamanho da mensagem - que é constante no nosso caso).

## Complexidade Total do Sistema

**O(t * n)** onde:
- t = tempo de execução (número de iterações)
- n = tamanho médio da página monitorada

### Gargalos identificados

1. **Extração de texto do body**: a cada iteração, o Selenium retorna
   todo o texto da página. Para páginas grandes (~100KB), isso domina
   o tempo de cada leitura.

2. **Busca textual com múltiplas ocorrências**: se o termo aparecer
   muitas vezes, o custo O(n * k) pode crescer. Em casos extremos
   (termo muito comum), considerar XPath específico ao invés de busca
   textual.

### Otimizações possíveis

- Cache do texto do body entre leituras consecutivas (não implementado,
  pois valores mudam a cada leitura).
- Uso de XPath direto ao invés de busca textual (já suportado pelo
  sistema - basta o usuário informar XPath como seletor).