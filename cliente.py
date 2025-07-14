import socket  # Biblioteca para comunicação via rede (sockets)
import json    # Biblioteca para trabalhar com dados no formato JSON

# Endereço e porta do servidor
HOST = 'localhost'
PORT = 5000

# Função para coletar os dados de um endereço
def coletar_endereco(label):
    print(f"Informe o endereço de {label}:")
    cidade = input("Cidade: ").strip()
    cep = input("CEP: ").strip()
    rua = input("Rua: ").strip()
    numero = input("Número: ").strip()
    bairro = input("Bairro: ").strip()

    # Retorna os dados como um dicionário
    return {
        "cidade": cidade,
        "cep": cep,
        "rua": rua,
        "numero": numero,
        "bairro": bairro
    }

# Função principal que envia o pedido para o servidor
def enviar_pedido():
    # Coleta os endereços de origem e destino
    origem = coletar_endereco("origem")
    destino = coletar_endereco("destino")

    # Verifica se as cidades são iguais
    if origem["cidade"].lower() != destino["cidade"].lower():
        print("[Cliente] ERRO: Origem e destino devem ser da mesma cidade!")
        return  # Encerra se forem diferentes

    # Cria o socket para comunicação TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))  # Conecta ao servidor

        # Monta o pedido com os dados
        pedido = {
            "comando": "pedido_entrega",
            "dados": {
                "origem": origem,
                "destino": destino
            }
        }

        # Envia o pedido em formato JSON
        s.send(json.dumps(pedido).encode())

        # Recebe a resposta do servidor
        resposta = s.recv(1024)
        print("[Cliente] Resposta do servidor:", resposta.decode())


if __name__ == '__main__':
    enviar_pedido()