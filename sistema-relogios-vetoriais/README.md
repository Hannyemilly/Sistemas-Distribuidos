# Simulador de Relógios Vetoriais - Sistemas Distribuídos

Este projeto implementa um simulador de relógios vetoriais para análise de causalidade em sistemas distribuídos, desenvolvido para o trabalho da disciplina de Sistemas Distribuídos.

## 📋 Descrição

O simulador modela a execução de eventos em um sistema distribuído com N processos, implementando:

- **Relógios Vetoriais**: Para rastreamento de causalidade entre eventos
- **Análise de Causalidade**: Determinação se eventos são causais ou concorrentes
- **Simulação de Eventos**: Eventos internos, envio e recebimento de mensagens
- **Cenários de Teste**: Demonstração de cadeias causais e eventos concorrentes

## 🏗️ Estrutura do Projeto

```
📁 sistema-relogios-vetoriais/
├── 📄 processo.py           # Classe principal do Processo
├── 📄 comparador_vetores.py # Lógica de comparação de vetores
├── 📄 simulador.py          # Simulador principal e cenários básicos
├── 📄 exemplo_avancado.py   # Exemplos mais complexos
└── 📄 README.md             # Este arquivo
```

## 🔧 Funcionalidades

### Classe Processo
- **ID único**: Identificador de 0 a N-1
- **Relógio Vetorial**: Array de N inteiros
- **Eventos Internos**: Atualização do próprio relógio
- **Envio de Mensagens**: Incremento e propagação do relógio
- **Recebimento**: Sincronização com relógio do remetente

### Comparação de Vetores
- **Causalidade**: Determina se um evento aconteceu antes do outro
- **Concorrência**: Identifica eventos sem relação causal
- **Análise Visual**: Exibição formatada dos resultados

## 🚀 Como Executar

### Pré-requisitos
- Python 3.6 ou superior
- VS Code (recomendado)

### Execução dos Cenários Básicos

```bash
python simulador.py
```

Este comando executa:
- **Cenário 1**: Demonstração de cadeia causal (Evento A → Evento B)
- **Cenário 2**: Demonstração de eventos concorrentes

### Execução dos Exemplos Avançados

```bash
python exemplo_avancado.py
```

Este comando executa:
- Cadeia causal complexa com 4 processos
- Múltiplos eventos concorrentes

## 📊 Exemplo de Saída

```
🎯 SIMULADOR DE RELÓGIOS VETORIAIS
Análise de Causalidade em Sistemas Distribuídos
============================================================
🚀 Sistema distribuído inicializado com 3 processos

🔄 CENÁRIO 1: DEMONSTRANDO CADEIA CAUSAL
============================================================
Processo P0: Evento interno 'Evento A' - Relógio: [1, 0, 0]
Processo P0: Enviando mensagem 'Envio: Mensagem A→B' para P1 - Relógio: [2, 0, 0]
Processo P1: Recebendo mensagem 'Recebimento: Mensagem A→B' de P0 - Relógio: [2, 1, 0]
Processo P1: Evento interno 'Evento B' - Relógio: [2, 2, 0]

============================================================
ANÁLISE DE CAUSALIDADE
============================================================
Evento 1: Evento A
  Relógio Vetorial: [1, 0, 0]
Evento 2: Evento B  
  Relógio Vetorial: [2, 2, 0]

✅ RESULTADO: O evento 'Evento A' aconteceu ANTES do evento 'Evento B'
   (Existe uma relação de causalidade: evento1 → evento2)
```

## 🧪 Cenários de Teste Implementados

### Cenário 1: Cadeia Causal
- Evento A ocorre em P0
- P0 envia mensagem para P1  
- Evento B ocorre em P1
- **Resultado**: A → B (causal)

### Cenário 2: Eventos Concorrentes
- Evento X ocorre em P0
- Evento Y ocorre em P2 (sem comunicação)
- **Resultado**: X || Y (concorrente)

## 🔍 Algoritmo dos Relógios Vetoriais

### Evento Interno
```python
VC[i] = VC[i] + 1  # Incrementa próprio relógio
```

### Envio de Mensagem
```python
VC[i] = VC[i] + 1     # Incrementa antes de enviar
enviar(mensagem, VC)   # Envia cópia do relógio
```

### Recebimento de Mensagem
```python
for j in range(N):
    if j == i:
        VC[j] = VC[j] + 1              # Incrementa próprio
    else:
        VC[j] = max(VC[j], VC_msg[j])  # Máximo com recebido
```

## 📚 Conceitos Teóricos

### Relação de Causalidade (→)
- **A → B**: se VC_A[i] ≤ VC_B[i] para todo i E existe pelo menos um j onde VC_A[j] < VC_B[j]

### Eventos Concorrentes (||)
- **A || B**: se não vale A → B nem B → A

## 🎯 Objetivos Atendidos

- ✅ Implementação completa dos relógios vetoriais
- ✅ Análise de causalidade entre eventos
- ✅ Demonstração de cadeia causal
- ✅ Demonstração de eventos concorrentes
- ✅ Interface clara e informativa
- ✅ Código modular e bem documentado
- ✅ Exemplos práticos de uso

## 👨‍💻 Uso no VS Code

1. Abra o VS Code na pasta do projeto
2. Execute os arquivos Python diretamente:
   - `Ctrl+F5` ou `F5` para executar
   - Terminal integrado: `python simulador.py`
3. Veja os resultados no terminal integrado

## 📈 Extensões Possíveis

O simulador pode ser expandido para:
- Mais processos e cenários complexos
- Interface gráfica para visualização
- Análise estatística de causalidade
- Simulação de falhas de processos
- Implementação de diferentes algoritmos de sincronização

---

**Desenvolvido para a disciplina de Sistemas Distribuídos**