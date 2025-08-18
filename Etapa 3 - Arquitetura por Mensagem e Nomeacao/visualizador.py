import pygame
import socket
import json
import time

# --- Configurações Gráficas ---
TAMANHO_CELULA = 60
TAMANHO_MAPA = 10 # O mapa é uma grade de 10x10
LARGURA = TAMANHO_CELULA * TAMANHO_MAPA
ALTURA = TAMANHO_CELULA * TAMANHO_MAPA
COR_FUNDO = (240, 240, 240)
COR_GRADE = (200, 200, 200)
COR_DRONE = (220, 50, 50)
COR_PONTO_P = (30, 180, 80) # Cor para pontos de coleta
COR_PONTO_D = (80, 30, 180) # Cor para pontos de destino

# --- Configurações de Rede ---
NOME_HOST = 'localhost'
NOME_PORT = 5001
NOME_SERVICO_ENTREGAS = "servico_entregas"

def consultar_servidor_entregas():
    """Conecta-se ao Servidor de Nomes para descobrir o endereço do servidor de entregas."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((NOME_HOST, NOME_PORT))
            mensagem = {"tipo": "comando_consultar_servico", "payload": {"nome": NOME_SERVICO_ENTREGAS}}
            s.send(json.dumps(mensagem).encode())
            resposta = json.loads(s.recv(1024).decode())
            if resposta.get("status") == "ok":
                return resposta["payload"]["host"], resposta["payload"]["porta"]
        except Exception:
            return None, None
    return None, None

def desenhar_grade(screen):
    """Desenha as linhas da grade do mapa na tela."""
    for x in range(0, LARGURA, TAMANHO_CELULA):
        pygame.draw.line(screen, COR_GRADE, (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, TAMANHO_CELULA):
        pygame.draw.line(screen, COR_GRADE, (0, y), (LARGURA, y))

def desenhar_pontos(screen, pontos, fonte):
    """Desenha os nomes dos pontos de coleta (P) e destino (D) no mapa."""
    for nome, (x, y) in pontos.items():
        cor = COR_PONTO_P if nome.startswith('P') else COR_PONTO_D
        # As coordenadas do mapa (1-10) são convertidas para pixels na tela
        texto = fonte.render(nome, True, cor)
        rect_texto = texto.get_rect(center=((x-1) * TAMANHO_CELULA + TAMANHO_CELULA / 2, (y-1) * TAMANHO_CELULA + TAMANHO_CELULA / 2))
        screen.blit(texto, rect_texto)

def desenhar_drones(screen, drones, fonte):
    """Desenha os drones (círculos vermelhos) e seus nomes no mapa."""
    for nome, estado in drones.items():
        x, y = estado['posicao']
        # As coordenadas (0-9) são convertidas para pixels no centro da célula
        px = x * TAMANHO_CELULA + TAMANHO_CELULA / 2
        py = y * TAMANHO_CELULA + TAMANHO_CELULA / 2
        pygame.draw.circle(screen, COR_DRONE, (px, py), TAMANHO_CELULA / 4)
        
        texto_nome = fonte.render(nome, True, (0,0,0))
        rect_texto = texto_nome.get_rect(center=(px, py + 20)) # Posiciona o nome abaixo do círculo
        screen.blit(texto_nome, rect_texto)

def main():
    """Função principal que inicializa o Pygame e o loop de visualização."""
    host, porta = consultar_servidor_entregas()
    if not host:
        print("[Visualizador] Não foi possível encontrar o servidor de entregas. Encerrando.")
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, porta))
    print(f"[Visualizador] Conectado ao servidor em {host}:{porta}")

    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Micromundo de Drones - Visualizador")
    fonte = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    rodando = True
    while rodando:
        # Loop de eventos do Pygame (para fechar a janela)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        try:
            # 1. Pede o estado atual do mapa ao servidor
            s.send(json.dumps({"tipo": "comando_solicitar_estado_mapa"}).encode())
            dados = s.recv(4096)
            if not dados: break
            estado_mapa = json.loads(dados.decode())
            
            drones = estado_mapa["payload"]["drones"]
            pontos = estado_mapa["payload"]["pontos"]

            # 2. Desenha tudo na tela
            screen.fill(COR_FUNDO)
            desenhar_grade(screen)
            desenhar_pontos(screen, pontos, fonte)
            desenhar_drones(screen, drones, fonte)
            
            # 3. Atualiza a tela
            pygame.display.flip()
            clock.tick(5) # Limita a taxa de atualização para 5 frames por segundo
        except (ConnectionResetError, BrokenPipeError):
            print("[Visualizador] Conexão com o servidor perdida.")
            break
        except json.JSONDecodeError:
            print("[Visualizador] Erro ao decodificar dados do servidor.")
            # Continua tentando no próximo frame

    s.close()
    pygame.quit()

if __name__ == '__main__':
    main()
