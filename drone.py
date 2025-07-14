import socket    # Comunicação via rede (sockets)
import json      # Manipular dados em formato JSON
import time      # Pausa e controle de tempo
import random    # Gerar tempo de entrega aleatório
import sys       # Permite acessar argumentos da linha de comando


HOST = 'localhost'
PORT = 5000


def drone(nome):
    # Cria o socket e conecta ao servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"[{nome}] Conectado ao servidor")

        while True:
            # Envia requisição perguntando se há pedidos
            requisicao = {"comando": "tem_pedido?"}
            s.send(json.dumps(requisicao).encode())

            # Recebe e decodifica a resposta do servidor
            resposta = json.loads(s.recv(1024).decode())

            # Se houver pedido disponível
            if resposta["status"] == "disponivel":
                pedido = resposta["pedido"]
                print(f"[{nome}] Executando entrega de {pedido['origem']} até {pedido['destino']} (ID: {pedido['id']})")

                # Simula o tempo da entrega
                time.sleep(random.randint(2, 5))
                print(f"[{nome}] Entrega concluída!")

                # Envia confirmação da entrega ao servidor
                confirmacao = {
                    "comando": "entrega_finalizada",
                    "drone": nome,
                    "pedido_id": pedido["id"]
                }
                s.send(json.dumps(confirmacao).encode())

                # Mostra resposta de confirmação do servidor
                resposta_confirmacao = json.loads(s.recv(1024).decode())
                print(f"[{nome}] Confirmação do servidor: {resposta_confirmacao['msg']}")

            else:
                # Se não houver pedidos disponíveis
                print(f"[{nome}] Nenhum pedido no momento.")
                time.sleep(3)  # Espera antes de perguntar novamente


if __name__ == '__main__':
    # Verifica se foi passado um nome como argumento, senão usa "Drone1"
    nome = sys.argv[1] if len(sys.argv) > 1 else "Drone1"
    drone(nome)