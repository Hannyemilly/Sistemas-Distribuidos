import copy

class Processo:
    def __init__(self, pid, num_processes):
        """
        Inicializa um processo com um relógio vetorial.

        Args:
            pid (int): ID do processo (de 0 a N-1).
            num_processes (int): Número total de processos (N).
        """
        self.pid = pid
        self.num_processes = num_processes
        # O relógio vetorial é inicializado com zeros
        self.vector_clock = [0] * num_processes

    def internal_event(self):
        """
        Simula um evento interno, incrementando a posição do próprio processo no vetor.
        Retorna uma cópia do relógio vetorial no momento do evento.
        """
        self.vector_clock[self.pid] += 1
        print(f"P{self.pid}: Evento interno. Relógio Vetorial: {self.vector_clock}")
        return copy.deepcopy(self.vector_clock)

    def send_message(self):
        """
        Prepara para enviar uma mensagem. O relógio é incrementado como um evento interno.
        Retorna uma cópia do relógio vetorial para ser "enviado" com a mensagem.
        """
        self.vector_clock[self.pid] += 1
        print(f"P{self.pid}: Enviando mensagem. Relógio Vetorial: {self.vector_clock}")
        return copy.deepcopy(self.vector_clock)

    def receive_message(self, sender_vc):
        """
        Recebe uma mensagem e atualiza seu relógio vetorial.

        Args:
            sender_vc (list): O relógio vetorial recebido com a mensagem.
        
        Retorna uma cópia do relógio vetorial após a atualização.
        """
        # 1. Atualiza cada elemento do seu relógio com o máximo entre o seu e o recebido
        for i in range(self.num_processes):
            self.vector_clock[i] = max(self.vector_clock[i], sender_vc[i])
        
        # 2. Incrementa sua própria posição no vetor (evento de recebimento)
        self.vector_clock[self.pid] += 1
        print(f"P{self.pid}: Recebeu mensagem. Relógio Vetorial atualizado: {self.vector_clock}")
        return copy.deepcopy(self.vector_clock)

def comparar_vetores(vc1, vc2):
    """
    Compara dois relógios vetoriais para determinar a relação causal.

    Args:
        vc1 (list): Relógio vetorial do primeiro evento.
        vc2 (list): Relógio vetorial do segundo evento.

    Returns:
        str: Uma string descrevendo a relação ("aconteceu antes de", 
             "aconteceu depois de", ou "são concorrentes").
    """
    # Verifica se vc1 <= vc2
    v1_le_v2 = all(v1 <= v2 for v1, v2 in zip(vc1, vc2))
    # Verifica se vc2 <= vc1
    v2_le_v1 = all(v2 <= v1 for v1, v2 in zip(vc1, vc2))

    # Se vc1 <= vc2 e vc1 != vc2, então vc1 aconteceu antes de vc2
    if v1_le_v2 and vc1 != vc2:
        return "aconteceu antes de"
    # Se vc2 <= vc1 e vc1 != vc2, então vc1 aconteceu depois de vc2
    elif v2_le_v1 and vc1 != vc2:
        return "aconteceu depois de"
    # Se os vetores são idênticos (mesmo evento registrado em dois pontos)
    elif vc1 == vc2:
        return "é o mesmo evento que"
    # Caso contrário, são concorrentes
    else:
        return "são concorrentes com"

# --- Simulação Principal ---
def main():
    NUM_PROCESSES = 3
    # Instancia N processos
    processes = [Processo(i, NUM_PROCESSES) for i in range(NUM_PROCESSES)]
    p0, p1, p2 = processes[0], processes[1], processes[2]

    print("="*40)
    print("CENÁRIO 1: CADEIA CAUSAL (A -> B)")
    print("="*40)
    # Evento A em P0
    print("1. Evento 'A' acontece em P0.")
    vc_A = p0.internal_event()
    
    # P0 envia mensagem para P1
    print("\n2. P0 envia uma mensagem para P1.")
    msg_vc = p0.send_message()
    
    # P1 recebe a mensagem, o que causa o Evento B
    print("\n3. P1 recebe a mensagem de P0, causando o evento 'B'.")
    vc_B = p1.receive_message(msg_vc)

    # Compara os vetores de A e B
    relacao = comparar_vetores(vc_A, vc_B)
    print("\n--- Análise de Causalidade ---")
    print(f"Relógio de A: {vc_A}")
    print(f"Relógio de B: {vc_B}")
    print(f"Resultado: Evento A {relacao} Evento B")
    print("="*40)

    print("\n" * 2)

    # Reinicia os processos para o segundo cenário
    processes = [Processo(i, NUM_PROCESSES) for i in range(NUM_PROCESSES)]
    p0, p1, p2 = processes[0], processes[1], processes[2]

    print("="*40)
    print("CENÁRIO 2: EVENTOS CONCORRENTES (X || Y)")
    print("="*40)
    # Evento X em P0
    print("1. Evento 'X' acontece em P0.")
    vc_X = p0.internal_event()

    # Evento Y em P2, sem nenhuma comunicação com P0
    print("\n2. Evento 'Y' acontece em P2, sem nenhuma comunicação prévia com P0.")
    vc_Y = p2.internal_event()

    # Compara os vetores de X e Y
    relacao = comparar_vetores(vc_X, vc_Y)
    print("\n--- Análise de Causalidade ---")
    print(f"Relógio de X: {vc_X}")
    print(f"Relógio de Y: {vc_Y}")
    print(f"Resultado: Evento X e Evento Y {relacao} si")
    print("="*40)


if __name__ == "__main__":
    main()