import socket
import threading
import json
from queue import Queue
from datetime import datetime
import uuid
import time
import random # <-- 1. IMPORTAR A BIBLIOTECA RANDOM

# --- Configurações ---
HOST = 'localhost'
PORT = 5000
NOME_HOST = 'localhost'
NOME_PORT = 5001
NOME_DO_SERVICO = "servico_entregas"
log_file = "log.txt"

# --- Mapa e Estado dos Drones ---
PONTOS_MAPA = {
    "P1": (2, 2), "P2": (8, 1), "P3": (1, 8), "P4": (9, 9), "P5": (5, 5),
    "D1": (1, 1), "D2": (7, 3), "D3": (3, 7), "D4": (9, 5), "D5": (5, 9)
}
drones_estado = {}
lock = threading.Lock()
fila_pedidos = Queue()


def log_evento(mensagem):
    with open(log_file, "a", encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {mensagem}\n")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Servidor] {mensagem}")

def registrar_no_servidor_nomes():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((NOME_HOST, NOME_PORT))
            mensagem = {
                "tipo": "comando_registrar_servico",
                "payload": {"nome": NOME_DO_SERVICO, "porta": PORT}
            }
            s.send(json.dumps(mensagem).encode())
            resposta = json.loads(s.recv(1024).decode())
            if resposta.get("status") == "ok":
                log_evento(f"Registrado com sucesso no Servidor de Nomes como '{NOME_DO_SERVICO}'")
            else:
                log_evento(f"Falha ao registrar no Servidor de Nomes: {resposta.get('detalhe')}")
        except ConnectionRefusedError:
            log_evento("ERRO CRÍTICO: Não foi possível conectar ao Servidor de Nomes. Ele está em execução?")
            exit()


def distribuidor_de_pedidos():
    """Thread que continuamente atribui pedidos da fila a drones disponíveis de forma aleatória."""
    while True:
        if not fila_pedidos.empty():
            drone_selecionado = None
            
            with lock:
                # 2. Criar uma lista de todos os drones que estão 'disponiveis'
                drones_disponiveis = [
                    nome for nome, estado in drones_estado.items() if estado["status"] == "disponivel"
                ]
                
                # 3. Se houver drones disponíveis, escolher um aleatoriamente
                if drones_disponiveis:
                    drone_selecionado = random.choice(drones_disponiveis)
                    drones_estado[drone_selecionado]["status"] = "em_entrega" # Marcar como ocupado
            
            if drone_selecionado:
                pedido = fila_pedidos.get()
                conn_drone = drones_estado[drone_selecionado]["conn"]
                pedido["drone_posicao_inicial"] = drones_estado[drone_selecionado]["posicao"]
                
                try:
                    evento_atribuicao = {"tipo": "evento_pedido_atribuido", "payload": pedido}
                    conn_drone.send(json.dumps(evento_atribuicao).encode())
                    log_evento(f"Pedido {pedido['id']} ... atribuído ao drone {drone_selecionado} (Seleção Aleatória).")
                except Exception as e:
                    log_evento(f"Erro ao enviar pedido para {drone_selecionado}: {e}. Devolvendo pedido para a fila.")
                    fila_pedidos.put(pedido)
                    drones_estado[drone_selecionado]["status"] = "disponivel" # Liberar drone se falhar
            else:
                time.sleep(1) 
        else:
            time.sleep(1)



def lidar_com_conexao(conn, addr):
    log_evento(f"Nova conexão: {addr}")
    nome_drone = None
    tipo_conexao = "desconhecida"

    try:
        while True:
            dados = conn.recv(2048)
            if not dados: break
            
            mensagem = json.loads(dados.decode())
            tipo_msg = mensagem.get("tipo")
            payload = mensagem.get("payload", {})

            if tipo_msg == "comando_registrar_drone":
                tipo_conexao = "drone"
                nome_drone = payload.get("nome")
                with lock:
                    drones_estado[nome_drone] = {
                        "status": "disponivel",
                        "posicao": (0, 0), 
                        "conn": conn
                    }
                log_evento(f"Drone '{nome_drone}' registrado e disponível na base (0, 0).")
            
            elif tipo_msg == "comando_solicitar_entrega":
                tipo_conexao = "cliente"
                ponto_origem = payload.get("origem")
                ponto_destino = payload.get("destino")

                if ponto_origem == ponto_destino:
                    log_evento(f"Pedido de {addr} rejeitado: origem e destino são iguais.")
                    resposta = {"tipo": "evento_pedido_rejeitado", "payload": {"motivo": "O ponto de origem e destino não podem ser o mesmo."}}
                    conn.send(json.dumps(resposta).encode())
                    continue

                if ponto_origem not in PONTOS_MAPA or ponto_destino not in PONTOS_MAPA:
                    log_evento(f"Pedido de {addr} rejeitado: ponto inválido.")
                    resposta = {"tipo": "evento_pedido_rejeitado", "payload": {"motivo": "Ponto de origem ou destino inválido."}}
                    conn.send(json.dumps(resposta).encode())
                    continue

                pedido = {
                    "id": str(uuid.uuid4())[:8],
                    "origem": {"nome": ponto_origem, "pos": PONTOS_MAPA[ponto_origem]},
                    "destino": {"nome": ponto_destino, "pos": PONTOS_MAPA[ponto_destino]}
                }
                fila_pedidos.put(pedido)
                log_evento(f"Novo pedido recebido (ID: {pedido['id']}): {ponto_origem} -> {ponto_destino}. Adicionado à fila.")
                resposta = {"tipo": "evento_pedido_confirmado", "payload": {"id": pedido["id"], "status": "Pedido recebido e na fila."}}
                conn.send(json.dumps(resposta).encode())

            elif tipo_msg == "comando_solicitar_estado_mapa":
                tipo_conexao = "visualizador"
                with lock:
                    estado_serializavel = {
                        nome: {"status": estado["status"], "posicao": estado["posicao"]}
                        for nome, estado in drones_estado.items()
                    }
                    resposta_estado = {
                        "tipo": "evento_estado_mapa",
                        "payload": {"drones": estado_serializavel, "pontos": PONTOS_MAPA}
                    }
                conn.send(json.dumps(resposta_estado).encode())

            elif tipo_msg == "comando_entrega_finalizada":
                nome_drone_finalizou = payload.get("drone")
                pedido_id = payload.get("pedido_id")
                posicao_final = tuple(payload.get("posicao_final"))
                with lock:
                    if nome_drone_finalizou in drones_estado:
                        drones_estado[nome_drone_finalizou]["status"] = "disponivel"
                        drones_estado[nome_drone_finalizou]["posicao"] = posicao_final
                log_evento(f"Drone '{nome_drone_finalizou}' finalizou pedido {pedido_id}. Agora disponível em {posicao_final}.")
            
            elif tipo_msg == "comando_atualizar_posicao":
                nome_drone_movendo = payload.get("drone")
                nova_posicao = tuple(payload.get("posicao"))
                with lock:
                    if nome_drone_movendo in drones_estado:
                         drones_estado[nome_drone_movendo]["posicao"] = nova_posicao

    except (ConnectionResetError, json.JSONDecodeError, KeyError, BrokenPipeError) as e:
        log_evento(f"Erro com {addr} ({nome_drone or tipo_conexao}): {e}")
    finally:
        if tipo_conexao == "drone" and nome_drone in drones_estado:
            with lock:
                del drones_estado[nome_drone]
            log_evento(f"Drone '{nome_drone}' desconectado.")
        conn.close()
        log_evento(f"Conexão com {addr} ({tipo_conexao}) encerrada.")

def iniciar_servidor():
    registrar_no_servidor_nomes()
    threading.Thread(target=distribuidor_de_pedidos, daemon=True).start()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        log_evento(f"Servidor de Entregas escutando em {HOST}:{PORT}")
        print("[Servidor] Pontos de Coleta (P) e Destino (D) disponíveis no mapa:", list(PONTOS_MAPA.keys()))
        while True:
            conn, addr = s.accept()
            threading.Thread(target=lidar_com_conexao, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    iniciar_servidor()