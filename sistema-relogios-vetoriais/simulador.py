from processo import Processo
from comparador_vetores import comparar_vetores, exibir_comparacao


class SimuladorSistemaDistribuido:
    """
    Simulador de sistema distribuído com relógios vetoriais.
    """
    
    def __init__(self, num_processos):
        """
        Inicializa o simulador com o número especificado de processos.
        
        Args:
            num_processos (int): Número de processos no sistema distribuído
        """
        self.num_processos = num_processos
        self.processos = []
        
        # Cria os processos
        for i in range(num_processos):
            processo = Processo(i, num_processos)
            self.processos.append(processo)
        
        print(f" Sistema distribuído inicializado com {num_processos} processos")
        print("="*60)
    
    def enviar_mensagem_entre_processos(self, id_origem, id_destino, nome_evento):
        """
        Simula o envio de uma mensagem entre dois processos.
        
        Args:
            id_origem (int): ID do processo remetente
            id_destino (int): ID do processo destinatário
            nome_evento (str): Nome do evento de comunicação
        """
        if id_origem >= self.num_processos or id_destino >= self.num_processos:
            raise ValueError("IDs de processo inválidos")
        
        processo_origem = self.processos[id_origem]
        processo_destino = self.processos[id_destino]
        
        # Processo origem envia mensagem
        relogio_envio = processo_origem.enviar_mensagem(processo_destino, f"Envio: {nome_evento}")
        
        # Processo destino recebe mensagem
        processo_destino.receber_mensagem(relogio_envio, f"Recebimento: {nome_evento}", id_origem)
    
    def executar_evento_interno(self, id_processo, nome_evento):
        """
        Executa um evento interno em um processo específico.
        
        Args:
            id_processo (int): ID do processo
            nome_evento (str): Nome do evento interno
        """
        if id_processo >= self.num_processos:
            raise ValueError("ID de processo inválido")
        
        self.processos[id_processo].evento_interno(nome_evento)
    
    def obter_estado_processos(self):
        """
        Exibe o estado atual de todos os processos.
        """
        print("\n ESTADO ATUAL DOS PROCESSOS:")
        print("-" * 40)
        for processo in self.processos:
            print(processo)
    
    def comparar_eventos(self, id_processo1, evento_index1, id_processo2, evento_index2):
        """
        Compara dois eventos específicos de processos diferentes.
        
        Args:
            id_processo1 (int): ID do primeiro processo
            evento_index1 (int): Índice do evento no primeiro processo
            id_processo2 (int): ID do segundo processo
            evento_index2 (int): Índice do evento no segundo processo
        """
        processo1 = self.processos[id_processo1]
        processo2 = self.processos[id_processo2]
        
        if evento_index1 >= len(processo1.eventos) or evento_index2 >= len(processo2.eventos):
            raise ValueError("Índices de eventos inválidos")
        
        evento1 = processo1.eventos[evento_index1]
        evento2 = processo2.eventos[evento_index2]
        
        relacao = comparar_vetores(evento1['relogio'], evento2['relogio'])
        exibir_comparacao(evento1, evento2, relacao)
        
        return relacao


def main():
    """
    Função principal que executa os cenários de teste.
    """
    print(" SIMULADOR DE RELÓGIOS VETORIAIS")
    print("Análise de Causalidade em Sistemas Distribuídos")
    print("="*60)
    
    # Criar sistema com 3 processos
    simulador = SimuladorSistemaDistribuido(3)
    
    print("\n CENÁRIO 1: DEMONSTRANDO CADEIA CAUSAL")
    print("="*60)
    
    # Evento A em P0
    simulador.executar_evento_interno(0, "Evento A")
    
    # P0 envia mensagem para P1 (estabelece causalidade)
    simulador.enviar_mensagem_entre_processos(0, 1, "Mensagem A→B")
    
    # Evento B em P1 (causalmente dependente de A)
    simulador.executar_evento_interno(1, "Evento B")
    
    # Comparar eventos A e B
    print("\n Comparando Evento A (P0) com Evento B (P1):")
    relacao1 = simulador.comparar_eventos(0, 0, 1, 1)  # Evento A vs Evento B
    
    print("\n" + "="*60)
    print("\n CENÁRIO 2: DEMONSTRANDO EVENTOS CONCORRENTES")
    print("="*60)
    
    # Reinicializar para cenário limpo
    simulador = SimuladorSistemaDistribuido(3)
    
    # Evento X em P0 (independente)
    simulador.executar_evento_interno(0, "Evento X")
    
    # Evento Y em P2 (independente, sem comunicação com P0)
    simulador.executar_evento_interno(2, "Evento Y")
    
    # Comparar eventos X e Y (devem ser concorrentes)
    print("\n Comparando Evento X (P0) com Evento Y (P2):")
    relacao2 = simulador.comparar_eventos(0, 0, 2, 0)  # Evento X vs Evento Y
    
    # Estado final dos processos
    simulador.obter_estado_processos()
    
    print("\n SIMULAÇÃO CONCLUÍDA!")
    print("="*60)
    print(" RESUMO DOS RESULTADOS:")
    print(f"   • Cenário 1 (Cadeia Causal): Relação '{relacao1.upper()}'")
    print(f"   • Cenário 2 (Concorrência): Relação '{relacao2.upper()}'")
    print("="*60)


if __name__ == "__main__":
    main()