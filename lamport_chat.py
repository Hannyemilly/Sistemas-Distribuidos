import threading
import time
import random
from queue import PriorityQueue

class Process:
    def __init__(self, process_id, num_processes):
        """
        Inicializa um processo (usuário no chat).
        
        Args:
            process_id (int): Identificador único do processo.
            num_processes (int): Número total de processos no sistema.
        """
        self.process_id = process_id
        self.num_processes = num_processes
        self.clock = 0  # Relógio de Lamport
        self.message_queue = PriorityQueue() # Fila de prioridade para ordenar mensagens
        self.network = [] # Lista para referenciar outros processos
        self.lock = threading.Lock() # Lock para garantir a segurança das threads

    def set_network(self, network):
        """
        Conecta o processo à rede de outros processos.
        """
        self.network = network

    def internal_event(self):
        """
        Simula um evento interno, incrementando o relógio.
        """
        with self.lock:
            self.clock += 1
            print(f"Processo {self.process_id}: Evento interno. Relógio: {self.clock}")

    def send_message(self, message_content):
        """
        Envia uma mensagem para todos os outros processos (broadcast).
        """
        with self.lock:
            self.clock += 1
            timestamp = self.clock
        
        message = (timestamp, self.process_id, message_content)
        print(f"Processo {self.process_id} (Relógio: {timestamp}): Enviando '{message_content}'")
        
        for other_process in self.network:
            if other_process.process_id != self.process_id:
                # Simula a latência de rede aleatória
                latency = random.uniform(0.1, 1.5)
                # Envia a mensagem em uma thread separada para não bloquear o remetente
                threading.Thread(target=self.send_with_latency, args=(other_process, message, latency)).start()

    def send_with_latency(self, receiver, message, latency):
        """
        Helper para simular o atraso da rede.
        """
        time.sleep(latency)
        receiver.receive_message(message)

    def receive_message(self, message):
        """
        Recebe uma mensagem, atualiza o relógio e a coloca na fila.
        """
        received_timestamp, sender_id, message_content = message
        
        with self.lock:
            self.clock = max(self.clock, received_timestamp) + 1
            
            # Adiciona a mensagem à fila de prioridade.
            # A tupla (timestamp, sender_id) é usada para ordenar.
            # sender_id é usado como critério de desempate.
            self.message_queue.put(message)
            
            print(f"Processo {self.process_id} (Relógio: {self.clock}): Recebeu '{message_content}' de {sender_id} (TS: {received_timestamp}).")

    def process_queue(self):
        """
        Processa e "entrega" as mensagens da fila na ordem correta.
        Este método roda em um loop para simular um cliente de chat ativo.
        """
        print(f"--- Chat do Processo {self.process_id} ---")
        while True:
            if not self.message_queue.empty():
                timestamp, sender_id, message_content = self.message_queue.get()
                print(f"  [P{self.process_id} - Chat Log] {sender_id}: {message_content} (TS: {timestamp})")
            time.sleep(0.5)

# --- Simulação Principal ---
def main():
    NUM_PROCESSES = 3
    processes = [Process(i, NUM_PROCESSES) for i in range(NUM_PROCESSES)]

    # Conecta todos os processos uns aos outros
    for p in processes:
        p.set_network(processes)

    # Inicia uma thread para cada processo para processar sua fila de mensagens
    for p in processes:
        thread = threading.Thread(target=p.process_queue, daemon=True)
        thread.start()

    # Define uma sequência de eventos para simular o chat
    # As mensagens são enviadas em threads para acontecerem de forma concorrente
    threading.Thread(target=lambda: (time.sleep(0.2), processes[0].send_message("Olá pessoal!"))).start()
    threading.Thread(target=lambda: (time.sleep(0.5), processes[1].send_message("Oi, tudo bem?"))).start()
    threading.Thread(target=lambda: (time.sleep(0.1), processes[2].send_message("Primeira mensagem aqui!"))).start()
    threading.Thread(target=lambda: (time.sleep(1.0), processes[0].send_message("Vamos terminar o trabalho?"))).start()

    # Mantém o programa principal rodando para observar a simulação
    try:
        time.sleep(10) # Duração da simulação
    except KeyboardInterrupt:
        print("\nSimulação encerrada.")

if __name__ == "__main__":
    main()