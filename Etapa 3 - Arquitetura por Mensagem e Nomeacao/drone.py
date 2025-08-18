import socket
import json
import time
import random
import sys

# --- Configurações de Rede ---
NOME_HOST = 'localhost'
NOME_PORT = 5001
NOME_SERVICO_ENTREGAS = "servico_entregas"

def consultar_servidor_entregas():
    """
    Conecta-se ao Servidor de Nomes para descobrir o endereço (host, porta)
    do servidor principal de entregas.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((NOME_HOST, NOME_PORT))
            mensagem = {"tipo": "comando_consultar_servico", "payload": {"nome": NOME_SERVICO_ENTREGAS}}
            s.send(json.dumps(mensagem).encode())
            resposta = json.loads(s.recv(1024).decode())
            if resposta.get("status") == "ok":
                payload = resposta.get("payload", {})
                return payload.get("host"), payload.get("porta")
            else:
                print(f"[Erro] Não foi possível encontrar o '{NOME_SERVICO_ENTREGAS}'. Detalhe: {resposta.get('detalhe')}")
                return None, None
        except ConnectionRefusedError:
            print("[Erro] Não foi possível conectar ao Servidor de Nomes.")
            return None, None

def mover_para_destino(s, nome_drone, pos_atual, pos_destino):
    """
    Simula o movimento passo a passo de um drone de uma posição atual para um destino.
    A cada passo, envia uma atualização de sua posição para o servidor.
    """
    pos_atual = tuple(pos_atual)
    pos_destino = tuple(pos_destino)
    while pos_atual != pos_destino:
        # Lógica de movimento simples: move primeiro no eixo X, depois no eixo Y
        if pos_atual[0] < pos_destino[0]:
            pos_atual = (pos_atual[0] + 1, pos_atual[1])
        elif pos_atual[0] > pos_destino[0]:
            pos_atual = (pos_atual[0] - 1, pos_atual[1])
        elif pos_atual[1] < pos_destino[1]:
            pos_atual = (pos_atual[0], pos_atual[1] + 1)
        elif pos_atual[1] > pos_destino[1]:
            pos_atual = (pos_atual[0], pos_atual[1] - 1)
        
        print(f"[{nome_drone}] ...movendo para {pos_atual}")
        
        # Envia comando de atualização de posição para o servidor
        atualizacao = {
            "tipo": "comando_atualizar_posicao",
            "payload": {"drone": nome_drone, "posicao": pos_atual}
        }
        s.send(json.dumps(atualizacao).encode())
        
        time.sleep(0.5) # Pausa para simular o tempo de voo entre coordenadas
    return pos_atual

def drone(nome):
    """Função principal que define o ciclo de vida e comportamento de um drone."""
    host_entregas, port_entregas = consultar_servidor_entregas()
    if not host_entregas: return

    print(f"[{nome}] Conectando ao Servidor de Entregas em {host_entregas}:{port_entregas}")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host_entregas, port_entregas))
        
        # 1. Registra-se no servidor para se anunciar como disponível
        registro = {"tipo": "comando_registrar_drone", "payload": {"nome": nome}}
        s.send(json.dumps(registro).encode())
        print(f"[{nome}] Registrado no servidor. Aguardando por entregas...")

        # 2. Loop principal: aguarda passivamente por tarefas do servidor
        while True:
            try:
                dados = s.recv(2048)
                if not dados:
                    print(f"[{nome}] Conexão com o servidor perdida.")
                    break
                
                mensagem = json.loads(dados.decode())
                
                # 3. Se receber um evento de pedido atribuído, inicia a lógica de entrega
                if mensagem.get("tipo") == "evento_pedido_atribuido":
                    pedido = mensagem["payload"]
                    posicao_atual = tuple(pedido["drone_posicao_inicial"])
                    origem_pos = tuple(pedido["origem"]["pos"])
                    destino_pos = tuple(pedido["destino"]["pos"])
                    
                    print(f"[{nome}] Novo pedido! De {pedido['origem']['nome']} para {pedido['destino']['nome']}.")
                    print(f"[{nome}] Rota: Base {posicao_atual} -> Coleta {origem_pos} -> Entrega {destino_pos}")

                    # Fase 1: Mover para o ponto de coleta
                    print(f"[{nome}] Fase 1: Indo para o ponto de coleta em {origem_pos}...")
                    posicao_atual = mover_para_destino(s, nome, posicao_atual, origem_pos)
                    print(f"[{nome}] Chegou em {origem_pos}. Pacote coletado!")
                    time.sleep(1)

                    # Fase 2: Mover para o ponto de entrega
                    print(f"[{nome}] Fase 2: Indo para o ponto de entrega em {destino_pos}...")
                    posicao_atual = mover_para_destino(s, nome, posicao_atual, destino_pos)
                    print(f"[{nome}] Chegou em {destino_pos}. Entrega finalizada!")
                    time.sleep(1)

                    # 4. Envia comando de confirmação de finalização para o servidor
                    confirmacao = {
                        "tipo": "comando_entrega_finalizada",
                        "payload": {
                            "drone": nome,
                            "pedido_id": pedido["id"],
                            "posicao_final": posicao_atual
                        }
                    }
                    s.send(json.dumps(confirmacao).encode())

            except (ConnectionResetError, BrokenPipeError):
                print(f"[{nome}] A conexão com o servidor foi encerrada.")
                break
            except Exception as e:
                print(f"[{nome}] Ocorreu um erro: {e}")
                break

if __name__ == '__main__':
    # Permite que o nome do drone seja passado como argumento na linha de comando
    if len(sys.argv) > 1:
        nome_drone = sys.argv[1]
        drone(nome_drone)
    else:
        print("Uso: python drone.py <NomeDoDrone>")
