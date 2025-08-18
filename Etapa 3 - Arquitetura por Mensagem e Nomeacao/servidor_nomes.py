import socket
import threading
import json
from datetime import datetime

# --- Configurações Globais ---
HOST = 'localhost'
PORT = 5001  # Porta dedicada exclusivamente para o serviço de nomes

# --- Estruturas de Dados Globais ---
# Dicionário para armazenar os serviços registrados. Ex: {"servico_entregas": ("127.0.0.1", 5000)}
servicos_registrados = {}
lock = threading.Lock() # Lock para garantir acesso seguro ao dicionário de serviços

def log_evento(mensagem):
    """Imprime uma mensagem de log específica do Servidor de Nomes."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Nomes] {mensagem}")

def lidar_com_conexao(conn, addr):
    """
    Executa em uma thread para cada conexão.
    Processa os comandos de registrar ou consultar serviços.
    """
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

                # Lógica para registrar um novo serviço
                if tipo_msg == "comando_registrar_servico":
                    nome_servico = payload.get("nome")
                    porta_servico = payload.get("porta")
                    if nome_servico and porta_servico:
                        with lock:
                            servicos_registrados[nome_servico] = (addr[0], porta_servico)
                        resposta = {"status": "ok", "detalhe": f"Serviço '{nome_servico}' registrado com sucesso."}
                        log_evento(f"Serviço '{nome_servico}' registrado em {(addr[0], porta_servico)}")
                
                # Lógica para consultar o endereço de um serviço existente
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
        # A conexão com o serviço de nomes é curta e finaliza após a operação
        conn.close()
        log_evento(f"Conexão com {addr} encerrada.")

def iniciar_servidor_nomes():
    """Função principal que inicializa o Servidor de Nomes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        log_evento(f"Servidor de Nomes escutando em {HOST}:{PORT}")
        
        # Loop infinito para aceitar novas conexões
        while True:
            conn, addr = s.accept()
            # Cria uma nova thread para cada conexão
            threading.Thread(target=lidar_com_conexao, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    iniciar_servidor_nomes()
