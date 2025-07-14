import socket        # Comunicação por rede
import threading     # Para lidar com várias conexões ao mesmo tempo
import json          # Troca de dados em formato JSON
from queue import Queue        # Fila para gerenciar pedidos
from datetime import datetime  # Para registrar data e hora nos logs
import uuid          # Gerar identificadores únicos para os pedidos


HOST = 'localhost'
PORT = 5000


fila_pedidos = Queue()        # Fila para armazenar pedidos de entrega
lock = threading.Lock()       # Trava para garantir acesso seguro à fila
entregas_por_drone = {}       # Registra quantas entregas cada drone fez
log_file = "log.txt"          # Nome do arquivo de log

# Função para registrar mensagens no arquivo de log
def log_evento(mensagem):
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {mensagem}\n")

# Formata um endereço para exibir bonito no log
def formatar_endereco(endereco):
    return f"{endereco['rua']}, {endereco['numero']} - {endereco['bairro']} - {endereco['cidade']} ({endereco['cep']})"

# Função que lida com a conexão de cada cliente (cliente ou drone)
def lidar_com_conexao(conn, addr):
    print(f"[Servidor] Conectado: {addr}")
    try:
        while True:
            dados = conn.recv(1024)  # Recebe dados do cliente
            if not dados:
                break  # Encerra se não receber nada

            # Tenta interpretar os dados como JSON
            try:
                mensagem = json.loads(dados.decode())
            except json.JSONDecodeError:
                # Caso ocorra erro, envia mensagem de erro ao cliente
                print(f"[Servidor] Erro ao decodificar JSON: {dados}")
                conn.send(json.dumps({"status": "erro", "msg": "Formato JSON inválido"}).encode())
                continue

            # Trata o comando de pedido de entrega
            if mensagem["comando"] == "pedido_entrega":
                with lock:
                    pedido = mensagem["dados"]
                    # Verifica se as cidades de origem e destino são iguais
                    if pedido["origem"]["cidade"].lower() != pedido["destino"]["cidade"].lower():
                        conn.send(json.dumps({"status": "erro", "msg": "Cidades de origem e destino diferentes!"}).encode())
                        continue
                    # Gera um ID único para o pedido e adiciona na fila
                    pedido_id = str(uuid.uuid4())[:8]
                    pedido["id"] = pedido_id
                    fila_pedidos.put(pedido)
                    log_evento(f"Novo pedido ID {pedido_id}: {formatar_endereco(pedido['origem'])} -> {formatar_endereco(pedido['destino'])}")
                    print(f"[Servidor] Pedido recebido: {pedido}")
                    conn.send(json.dumps({"status": "ok", "msg": "Pedido adicionado", "id": pedido_id}).encode())

            # Trata a solicitação de um drone verificando se há pedidos
            elif mensagem["comando"] == "tem_pedido?":
                with lock:
                    if not fila_pedidos.empty():
                        pedido = fila_pedidos.get()
                        conn.send(json.dumps({"status": "disponivel", "pedido": pedido}).encode())
                        log_evento(f"Pedido enviado para drone: {pedido['id']}")
                    else:
                        conn.send(json.dumps({"status": "vazio"}).encode())

            # Trata confirmação de entrega feita por um drone
            elif mensagem["comando"] == "entrega_finalizada":
                drone = mensagem["drone"]
                pedido_id = mensagem.get("pedido_id", "desconhecido")
                with lock:
                    # Atualiza contador de entregas feitas pelo drone
                    entregas_por_drone[drone] = entregas_por_drone.get(drone, 0) + 1
                    log_evento(f"{drone} finalizou entrega do pedido {pedido_id}")
                conn.send(json.dumps({"status": "ok", "msg": "Entrega confirmada"}).encode())

    except Exception as e:
        print(f"[Servidor] Erro com {addr}: {e}")
    finally:
        conn.close()
        print(f"[Servidor] Conexao encerrada: {addr}")

# Função que inicia o servidor e aceita conexões
def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Servidor] Escutando em {HOST}:{PORT}")
        log_evento("Servidor iniciado")
        while True:
            conn, addr = s.accept()
            # Cria uma nova thread para cada cliente que se conecta
            threading.Thread(target=lidar_com_conexao, args=(conn, addr)).start()


if __name__ == '__main__':
    iniciar_servidor()