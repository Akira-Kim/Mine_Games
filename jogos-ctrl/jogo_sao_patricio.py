import pygame
import random
import math
import sys

# ====================== INICIALIZAÇÃO ======================
pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
LARGURA = info.current_w
ALTURA = info.current_h
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("Caça ao Trevo Mágico - São Patrício 🍀")

clock = pygame.time.Clock()

# ====================== CORES E FONTES ======================
VERDE_ESCURO = (0, 80, 0)
VERDE_CLARO = (34, 139, 34)
VERDE_MUSGO = (107, 142, 35)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
DOURADO = (255, 215, 0)
CORES_ARCOIRIS = [
    (255, 0, 0), (255, 140, 0), (255, 255, 0),
    (0, 200, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)
]

fonte_titulo   = pygame.font.SysFont("comicsansms", 72, bold=True)
fonte_grande   = pygame.font.SysFont("comicsansms", 48, bold=True)
fonte_media    = pygame.font.SysFont("comicsansms", 32, bold=True)
fonte_vitoria  = pygame.font.SysFont("comicsansms", 65, bold=True)

# ====================== CONFIGURAÇÕES DO JOGO ======================
TAMANHO_GRADE = 6
TAMANHO_CELULA = min(LARGURA // (TAMANHO_GRADE + 4), ALTURA // (TAMANHO_GRADE + 6))
X_INICIO_GRADE = (LARGURA - TAMANHO_GRADE * TAMANHO_CELULA) // 2
Y_INICIO_GRADE = (ALTURA - TAMANHO_GRADE * TAMANHO_CELULA) // 2 + 80

Y_TENTATIVAS = Y_INICIO_GRADE + TAMANHO_GRADE * TAMANHO_CELULA + 40

trevo_x = random.randint(0, TAMANHO_GRADE - 1)
trevo_y = random.randint(0, TAMANHO_GRADE - 1)

encontrou = False
tentativas = 10

revelados = [[None for _ in range(TAMANHO_GRADE)] for _ in range(TAMANHO_GRADE)]
animacao_atual = None

mensagem_vitoria = ""
mensagem_derrota = ""

# ====================== IMAGENS ======================
try:
    img_leprechaun = pygame.image.load(r"C:\Users\bruno\Downloads\4817932-celebrando-o-dia-de-santo-patrick-vetor-removebg-preview.png").convert_alpha()
    img_leprechaun = pygame.transform.smoothscale(img_leprechaun, (300, 400))
except:
    img_leprechaun = None

try:
    img_pote = pygame.image.load(r"C:\Users\bruno\Downloads\695830-pote-de-ouro-do-dia-de-sao-patricio-com-trevo-gratis-vetor-removebg-preview.png").convert_alpha()
    img_pote = pygame.transform.smoothscale(img_pote, (300, 400))
except:
    img_pote = None

# ====================== SONS ======================
try:
    som_moeda = pygame.mixer.Sound("coin.wav")
    som_magico = pygame.mixer.Sound("magic.wav")
except:
    som_moeda = som_magico = None

# ====================== SHAMROCKS ======================
shamrocks = [(random.randint(0, LARGURA), random.randint(0, ALTURA), random.randint(15, 45)) for _ in range(40)]

# ====================== FUNÇÕES AUXILIARES ======================
def esta_proximo(lin, col):
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            nx = lin + di
            ny = col + dj
            if 0 <= nx < TAMANHO_GRADE and 0 <= ny < TAMANHO_GRADE:
                if nx == trevo_x and ny == trevo_y:
                    return True
    return False

# ====================== DESENHO ======================
def desenhar_arco_iris():
    centro_x = LARGURA // 2
    centro_y = Y_INICIO_GRADE - 110
    raio_base = min(LARGURA, ALTURA) // 4.2
    for i, cor in enumerate(CORES_ARCOIRIS):
        raio = raio_base - i * 28
        pygame.draw.arc(tela, cor, (centro_x - raio, centro_y - raio, raio * 2, raio * 2), 0, math.pi, 36)

def desenhar_fundo():
    for y in range(ALTURA):
        cor = (
            int(VERDE_ESCURO[0] + (VERDE_CLARO[0] - VERDE_ESCURO[0]) * (y / ALTURA)),
            int(VERDE_ESCURO[1] + (VERDE_CLARO[1] - VERDE_ESCURO[1]) * (y / ALTURA)),
            int(VERDE_ESCURO[2] + (VERDE_CLARO[2] - VERDE_ESCURO[2]) * (y / ALTURA))
        )
        pygame.draw.line(tela, cor, (0, y), (LARGURA, y))
    for x, y, tam in shamrocks:
        pygame.draw.circle(tela, (0, 100, 0), (x, y), tam // 3)
        pygame.draw.circle(tela, (0, 120, 0), (x - tam//2, y), tam//3)
        pygame.draw.circle(tela, (0, 120, 0), (x + tam//2, y), tam//3)
        pygame.draw.circle(tela, (0, 120, 0), (x, y - tam//2), tam//3)

def desenhar_grade():
    for i in range(TAMANHO_GRADE):
        for j in range(TAMANHO_GRADE):
            x = X_INICIO_GRADE + j * TAMANHO_CELULA
            y = Y_INICIO_GRADE + i * TAMANHO_CELULA
            rect = pygame.Rect(x, y, TAMANHO_CELULA, TAMANHO_CELULA)
            cor_cel = VERDE_CLARO if (i + j) % 2 == 0 else VERDE_MUSGO
            pygame.draw.rect(tela, cor_cel, rect)
            pygame.draw.rect(tela, PRETO, rect, 5)

def desenhar_moeda(cx, cy, scale=1.0, hot=False):
    r = int(34 * scale)
    pygame.draw.circle(tela, DOURADO, (int(cx), int(cy)), r)
    pygame.draw.circle(tela, (255, 245, 180), (int(cx - 7*scale), int(cy - 8*scale)), int(r * 0.35))
    pygame.draw.circle(tela, (180, 140, 0), (int(cx), int(cy)), int(r * 0.82), int(7*scale))
    if hot:
        desenhar_trevo(cx, cy - 3*scale, scale * 0.48)

def desenhar_trevo(cx, cy, scale=1.0):
    s = scale * 1.1
    leaf = (0, 180, 0)
    pygame.draw.ellipse(tela, leaf, (cx - 26*s, cy - 28*s, 32*s, 24*s))
    pygame.draw.ellipse(tela, leaf, (cx + 2*s, cy - 28*s, 32*s, 24*s))
    pygame.draw.ellipse(tela, leaf, (cx - 26*s, cy - 6*s, 32*s, 24*s))
    pygame.draw.ellipse(tela, leaf, (cx + 2*s, cy - 6*s, 32*s, 24*s))
    pygame.draw.line(tela, (0, 100, 0), (cx, cy + 22*s), (cx + 3*s, cy + 52*s), int(9*s))

def desenhar_simbolos():
    global animacao_atual
    for i in range(TAMANHO_GRADE):
        for j in range(TAMANHO_GRADE):
            if revelados[i][j] is None:
                continue
            cx = X_INICIO_GRADE + j * TAMANHO_CELULA + TAMANHO_CELULA // 2
            cy = Y_INICIO_GRADE + i * TAMANHO_CELULA + TAMANHO_CELULA // 2
            tipo = revelados[i][j]
            
            if animacao_atual and animacao_atual["lin"] == i and animacao_atual["col"] == j:
                frame = animacao_atual["frame"]
                scale = 0.5 + 1.1 * min(1.0, frame / 9)
                if frame > 12:
                    scale = 1.0 + 0.18 * math.sin(frame / 2.5)
                
                if tipo == "trevo":
                    desenhar_trevo(cx, cy, scale)
                else:
                    hot = (tipo == "coin_hot")
                    desenhar_moeda(cx, cy, scale, hot)
                
                if tipo != "trevo":
                    texto = "Está perto! ☘️" if (tipo == "coin_hot") else "Não é aqui!"
                    msg = fonte_media.render(texto, True, BRANCO)
                    tela.blit(msg, (cx - msg.get_width()//2, cy + 58))
                
                animacao_atual["frame"] += 1
                if animacao_atual["frame"] > 38:
                    animacao_atual = None
            else:
                if tipo == "trevo":
                    desenhar_trevo(cx, cy)
                else:
                    hot = (tipo == "coin_hot")
                    desenhar_moeda(cx, cy, 1.0, hot)

def desenhar_area_imagem_esquerda():
    x = 40
    y = ALTURA // 2 - 200
    if img_leprechaun:
        tela.blit(img_leprechaun, (x, y))

def desenhar_area_pote_direita():
    x = LARGURA - 380
    y = ALTURA // 2 - 200
    if img_pote:
        tela.blit(img_pote, (x, y))

# ====================== FUNÇÃO PARA TEXTO COM CONTORNO BRANCO SUAVE ======================
def desenhar_texto_com_contorno(texto, fonte, pos, cor_texto=PRETO, cor_contorno=BRANCO):
    """Desenha texto com contorno branco suave (fica parte da letra, só destaca)"""
    offsets = [(-2,-2), (-2,0), (-2,2), (0,-2), (0,2), (2,-2), (2,0), (2,2)]  # 8 direções suaves
    
    for dx, dy in offsets:
        surf = fonte.render(texto, True, cor_contorno)
        tela.blit(surf, (pos[0] + dx, pos[1] + dy))
    
    # Texto principal (preto) por cima
    surf = fonte.render(texto, True, cor_texto)
    tela.blit(surf, pos)

def desenhar_textos():
    # Título (mantém como estava)
    titulo = fonte_titulo.render("Caça ao Trevo Mágico!", True, BRANCO)
    sombra = fonte_titulo.render("Caça ao Trevo Mágico!", True, PRETO)
    tela.blit(sombra, (LARGURA//2 - titulo.get_width()//2 + 5, 24))
    tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 20))
    
    # Tentativas
    txt_tent = fonte_grande.render(f"Tentativas restantes: {tentativas}", True, BRANCO)
    tela.blit(txt_tent, (LARGURA//2 - txt_tent.get_width()//2, Y_TENTATIVAS))
    
    # ==================== TEXTOS FINAIS COM CONTORNO BRANCO SUAVE ====================
    if mensagem_vitoria:
        # Linha 1 - PARABÉNS!
        desenhar_texto_com_contorno("PARABÉNS!", fonte_vitoria, 
                                    (LARGURA//2 - fonte_vitoria.render("PARABÉNS!", True, PRETO).get_width()//2, ALTURA//2 - 130))
        
        # Linha 2
        desenhar_texto_com_contorno("Você encontrou o trevo da sorte!", fonte_media, 
                                    (LARGURA//2 - fonte_media.render("Você encontrou o trevo da sorte!", True, PRETO).get_width()//2, ALTURA//2 - 50))
        
        # Linha 3
        desenhar_texto_com_contorno("Boa sorte no seu dia! 🍀🌈", fonte_media, 
                                    (LARGURA//2 - fonte_media.render("Boa sorte no seu dia! 🍀🌈", True, PRETO).get_width()//2, ALTURA//2 + 15))
    
    elif mensagem_derrota:
        # Linha 1 - QUE PENA!
        desenhar_texto_com_contorno("QUE PENA!", fonte_vitoria, 
                                    (LARGURA//2 - fonte_vitoria.render("QUE PENA!", True, PRETO).get_width()//2, ALTURA//2 - 130))
        
        # Linha 2
        desenhar_texto_com_contorno("O trevo escapou desta vez...", fonte_media, 
                                    (LARGURA//2 - fonte_media.render("O trevo escapou desta vez...", True, PRETO).get_width()//2, ALTURA//2 - 50))
        
        # Linha 3
        desenhar_texto_com_contorno("Tente novamente! 🍀", fonte_media, 
                                    (LARGURA//2 - fonte_media.render("Tente novamente! 🍀", True, PRETO).get_width()//2, ALTURA//2 + 15))

# ====================== LOOP PRINCIPAL ======================
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
            rodando = False
        
        elif evento.type == pygame.MOUSEBUTTONDOWN and tentativas > 0 and not encontrou:
            mx, my = evento.pos
            if (X_INICIO_GRADE <= mx < X_INICIO_GRADE + TAMANHO_GRADE * TAMANHO_CELULA and
                Y_INICIO_GRADE <= my < Y_INICIO_GRADE + TAMANHO_GRADE * TAMANHO_CELULA):
                
                col = (mx - X_INICIO_GRADE) // TAMANHO_CELULA
                lin = (my - Y_INICIO_GRADE) // TAMANHO_CELULA
                
                if revelados[lin][col] is None:
                    tentativas -= 1
                    
                    if lin == trevo_x and col == trevo_y:
                        tipo = "trevo"
                        encontrou = True
                        mensagem_vitoria = "vitória"
                        if som_magico: som_magico.play()
                    else:
                        tipo = "coin_hot" if esta_proximo(lin, col) else "coin"
                        if som_moeda: som_moeda.play()
                    
                    revelados[lin][col] = tipo
                    animacao_atual = {"lin": lin, "col": col, "tipo": tipo, "frame": 0}

    desenhar_fundo()
    desenhar_arco_iris()
    desenhar_area_imagem_esquerda()
    desenhar_area_pote_direita()
    desenhar_grade()
    desenhar_simbolos()
    desenhar_textos()
    
    if tentativas == 0 and not encontrou:
        if revelados[trevo_x][trevo_y] is None:
            revelados[trevo_x][trevo_y] = "trevo"
            animacao_atual = {"lin": trevo_x, "col": trevo_y, "tipo": "trevo", "frame": 0}
        if not mensagem_derrota:
            mensagem_derrota = "derrota"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()