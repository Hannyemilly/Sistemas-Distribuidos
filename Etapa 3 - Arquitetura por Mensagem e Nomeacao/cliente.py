import socket
import json

# --- Configurações ---
NOME_HOST = 'localhost'
NOME_PORT = 5001
NOME_SERVICO_ENTREGAS = "servico_entregas"

def consultar_servidor_entregas():
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

def coletar_pontos():
    """Pede ao usuário para escolher pontos de origem e destino, garantindo que sejam diferentes."""
    print("\n--- Novo Pedido ---")
    print("Pontos de Coleta disponíveis: P1, P2, P3, P4, P5")
    print("Pontos de Destino disponíveis: D1, D2, D3, D4, D5")
    
    while True:
        origem = input("Escolha o ponto de ORIGEM (ex: P1): ").strip().upper()
        destino = input("Escolha o ponto de DESTINO (ex: D2): ").strip().upper()
        
        # Validação para impedir origem e destino iguais
        if origem == destino:
            print("[Cliente] ERRO: O ponto de origem e destino não podem ser o mesmo. Por favor, tente novamente.")
        else:
            return origem, destino

def enviar_pedido():
    host_entregas, port_entregas = consultar_servidor_entregas()
    if not host_entregas: return

    origem, destino = coletar_pontos()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host_entregas, port_entregas))
        pedido = {
            "tipo": "comando_solicitar_entrega",
            "payload": {"origem": origem, "destino": destino}
        }
        s.send(json.dumps(pedido).encode())
        resposta = s.recv(1024)
        print("\n[Cliente] Resposta do servidor:", json.loads(resposta.decode()))

if __name__ == '__main__':
    while True:
        enviar_pedido()
        novo_pedido = input("\nDeseja fazer um novo pedido? (s/n): ").strip().lower()
        if novo_pedido != 's':
            print("[Cliente] Encerrando...")
            break