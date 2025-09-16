from processo import Processo
from comparador_vetores import comparar_vetores, exibir_comparacao
from simulador import SimuladorSistemaDistribuido


def exemplo_cadeia_complexa():
    """
    Exemplo mais complexo demonstrando uma cadeia causal longa.
    """
    print("\n EXEMPLO AVANÇADO: CADEIA CAUSAL COMPLEXA")
    print("="*60)
    
    # Sistema com 4 processos
    simulador = SimuladorSistemaDistribuido(4)
    
    # Sequência de eventos causalmente relacionados
    print("\n Sequência de eventos:")
    print("1. P0 executa evento interno")
    simulador.executar_evento_interno(0, "Inicialização do sistema")
    
    print("2. P0 envia dados para P1")
    simulador.enviar_mensagem_entre_processos(0, 1, "Dados iniciais")
    
    print("3. P1 processa e envia para P2")
    simulador.executar_evento_interno(1, "Processamento dos dados")
    simulador.enviar_mensagem_entre_processos(1, 2, "Dados processados")
    
    print("4. P2 processa e envia para P3")
    simulador.executar_evento_interno(2, "Validação dos dados")
    simulador.enviar_mensagem_entre_processos(2, 3, "Dados validados")
    
    print("5. P3 finaliza o processo")
    simulador.executar_evento_interno(3, "Finalização")
    
    # Análises de causalidade
    print("\n ANÁLISES DE CAUSALIDADE:")
    
    # Evento inicial vs evento final (deve ser "antes")
    print("\n1. Inicialização (P0) vs Finalização (P3):")
    simulador.comparar_eventos(0, 0, 3, 1)
    
    # Eventos em processos não diretamente comunicantes
    print("\n2. Processamento P1 vs Validação P2:")
    simulador.comparar_eventos(1, 1, 2, 2)


def exemplo_concorrencia_multipla():
    """
    Exemplo demonstrando múltiplos eventos concorrentes.
    """
    print("\n EXEMPLO AVANÇADO: MÚLTIPLOS EVENTOS CONCORRENTES")
    print("="*60)
    
    # Sistema com 4 processos
    simulador = SimuladorSistemaDistribuido(4)
    
    # Eventos simultâneos em processos diferentes (sem comunicação)
    print("\n Eventos concorrentes simultâneos:")
    print("1. Cada processo executa um evento independente")
    
    simulador.executar_evento_interno(0, "Tarefa A - Cálculo matemático")
    simulador.executar_evento_interno(1, "Tarefa B - Leitura de arquivo")
    simulador.executar_evento_interno(2, "Tarefa C - Acesso ao banco")
    simulador.executar_evento_interno(3, "Tarefa D - Processamento de imagem")
    
    print("\n ANÁLISES DE CONCORRÊNCIA:")
    
    # Comparações entre eventos concorrentes
    print("\n1. Tarefa A vs Tarefa C:")
    simulador.comparar_eventos(0, 0, 2, 0)
    
    print("\n2. Tarefa B vs Tarefa D:")
    simulador.comparar_eventos(1, 0, 3, 0)
    
    # Estado final
    simulador.obter_estado_processos()


def main():
    """
    Executa os exemplos avançados.
    """
    print(" EXEMPLOS AVANÇADOS DE RELÓGIOS VETORIAIS")
    print("="*60)
    
    # Exemplo 1: Cadeia causal complexa
    exemplo_cadeia_complexa()
    
    print("\n" + "="*60)
    
    # Exemplo 2: Múltiplos eventos concorrentes
    exemplo_concorrencia_multipla()

    print("\n EXEMPLOS AVANÇADOS CONCLUÍDOS!")
    print("="*60)


if __name__ == "__main__":
    main()