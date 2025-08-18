import socket
import threading
import json
from datetime import datetime

HOST = 'localhost'
PORT = 5001  # Porta dedicada para o serviço de nomes

# Dicionário para armazenar os serviços registrados: {"nome_servico": ("ip", porta)}
servicos_registrados = {}
lock = threading.Lock()

def log_evento(mensagem):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Nomes] {mensagem}")

def lidar_com_conexao(conn, addr):
    log_evento(f"Nova conexão de {addr}")
    try:
        while True:
            dados = conn.recv(1024)
            if not dados:
                break

            try:
                mensagem = json.loads(dados.decode())
                tipo_msg = mensagem.get("tipo")
                payload = mensagem.get("payload", {})

                resposta = {"status": "erro", "detalhe": "Comando inválido"}

                if tipo_msg == "comando_registrar_servico":
                    nome_servico = payload.get("nome")
                    porta_servico = payload.get("porta")
                    if nome_servico and porta_servico:
                        with lock:
                            servicos_registrados[nome_servico] = (addr[0], porta_servico)
                        resposta = {"status": "ok", "detalhe": f"Serviço '{nome_servico}' registrado com sucesso."}
                        log_evento(f"Serviço '{nome_servico}' registrado em {(addr[0], porta_servico)}")
                
                elif tipo_msg == "comando_consultar_servico":
                    nome_servico = payload.get("nome")
                    with lock:
                        endereco = servicos_registrados.get(nome_servico)
                    
                    if endereco:
                        resposta = {"status": "ok", "payload": {"nome": nome_servico, "host": endereco[0], "porta": endereco[1]}}
                        log_evento(f"Consulta por '{nome_servico}' atendida para {addr}.")
                    else:
                        resposta = {"status": "nao_encontrado", "detalhe": f"Serviço '{nome_servico}' não encontrado."}
                        log_evento(f"Consulta por '{nome_servico}' falhou (não encontrado).")
                
                conn.send(json.dumps(resposta).encode())

            except (json.JSONDecodeError, KeyError) as e:
                log_evento(f"Erro ao processar mensagem de {addr}: {e}")
                conn.send(json.dumps({"status": "erro", "detalhe": "Formato de mensagem inválido"}).encode())

    except Exception as e:
        log_evento(f"Erro na conexão com {addr}: {e}")
    finally:
        conn.close()
        log_evento(f"Conexão com {addr} encerrada.")

def iniciar_servidor_nomes():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        log_evento(f"Servidor de Nomes escutando em {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=lidar_com_conexao, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    iniciar_servidor_nomes()