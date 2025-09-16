class Processo:
    """
    Classe que representa um processo em um sistema distribuído com relógio vetorial.
    """
    
    def __init__(self, id_processo, num_processos):
        """
        Inicializa um processo com seu ID e relógio vetorial.
        
        Args:
            id_processo (int): ID único do processo (0 a N-1)
            num_processos (int): Número total de processos no sistema
        """
        self.id = id_processo
        self.num_processos = num_processos
        self.relogio_vetorial = [0] * num_processos
        self.eventos = []  # Lista para armazenar histórico de eventos
    
    def evento_interno(self, nome_evento):
        """
        Processa um evento interno do processo.
        
        Args:
            nome_evento (str): Nome descritivo do evento
            
        Returns:
            list: Cópia do relógio vetorial após o evento
        """
        # Incrementa o próprio relógio
        self.relogio_vetorial[self.id] += 1
        
        # Registra o evento
        evento_info = {
            'tipo': 'interno',
            'nome': nome_evento,
            'relogio': self.relogio_vetorial.copy()
        }
        self.eventos.append(evento_info)
        
        print(f"Processo P{self.id}: Evento interno '{nome_evento}' - Relógio: {self.relogio_vetorial}")
        
        return self.relogio_vetorial.copy()
    
    def enviar_mensagem(self, processo_destino, nome_evento):
        """
        Envia uma mensagem para outro processo.
        
        Args:
            processo_destino (Processo): Processo que receberá a mensagem
            nome_evento (str): Nome descritivo do evento de envio
            
        Returns:
            list: Cópia do relógio vetorial após o envio
        """
        # Incrementa o próprio relógio antes de enviar
        self.relogio_vetorial[self.id] += 1
        
        # Registra o evento de envio
        evento_info = {
            'tipo': 'envio',
            'nome': nome_evento,
            'destino': processo_destino.id,
            'relogio': self.relogio_vetorial.copy()
        }
        self.eventos.append(evento_info)
        
        print(f"Processo P{self.id}: Enviando mensagem '{nome_evento}' para P{processo_destino.id} - Relógio: {self.relogio_vetorial}")
        
        # Envia uma cópia do relógio vetorial atual
        return self.relogio_vetorial.copy()
    
    def receber_mensagem(self, relogio_remetente, nome_evento, id_remetente):
        """
        Recebe uma mensagem de outro processo e atualiza o relógio vetorial.
        
        Args:
            relogio_remetente (list): Relógio vetorial do processo remetente
            nome_evento (str): Nome descritivo do evento de recebimento
            id_remetente (int): ID do processo remetente
            
        Returns:
            list: Cópia do relógio vetorial após o recebimento
        """
        # Atualiza o relógio vetorial: max(VC_local, VC_remetente) + incrementa próprio
        for i in range(self.num_processos):
            if i == self.id:
                # Incrementa o próprio relógio
                self.relogio_vetorial[i] += 1
            else:
                # Toma o máximo entre o relógio local e o recebido
                self.relogio_vetorial[i] = max(self.relogio_vetorial[i], relogio_remetente[i])
        
        # Registra o evento de recebimento
        evento_info = {
            'tipo': 'recebimento',
            'nome': nome_evento,
            'remetente': id_remetente,
            'relogio': self.relogio_vetorial.copy()
        }
        self.eventos.append(evento_info)
        
        print(f"Processo P{self.id}: Recebendo mensagem '{nome_evento}' de P{id_remetente} - Relógio: {self.relogio_vetorial}")
        
        return self.relogio_vetorial.copy()
    
    def obter_ultimo_evento(self):
        """
        Retorna informações do último evento processado.
        
        Returns:
            dict: Informações do último evento ou None se não há eventos
        """
        return self.eventos[-1] if self.eventos else None
    
    def __str__(self):
        """
        Representação em string do processo.
        """
        return f"Processo P{self.id} - Relógio Vetorial: {self.relogio_vetorial}"