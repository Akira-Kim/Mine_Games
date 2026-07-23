import pygame
import sys
import random
import os

# Inicializa o pygame
pygame.init()

# Constantes da tela
LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Magos vs Soldados")

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)

# Relógio
clock = pygame.time.Clock()

# Fonte para pontuação
fonte = pygame.font.SysFont('Arial', 30)

# Variáveis de jogo
pontuacao = 0
spawn_timer = 0
spawn_interval = 2000  # 2 segundos

# Classes
class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, cor, controles, imagem_path=None):
        super().__init__()
        if imagem_path and os.path.exists(imagem_path):
            try:
                self.image = pygame.image.load(imagem_path).convert_alpha()
                # Redimensiona se necessário (opcional)
                self.image = pygame.transform.scale(self.image, (40, 60))
            except:
                # Fallback se a imagem não carregar
                self.image = pygame.Surface((40, 60))
                self.image.fill(cor)
        else:
            self.image = pygame.Surface((40, 60))
            self.image.fill(cor)
            
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.controles = controles
        self.vel = 5
        self.ultimo_tiro = 0
        self.cooldown_tiro = 500  # ms

    def update(self, teclas):
        if teclas[self.controles['cima']]:
            self.rect.y -= self.vel
        if teclas[self.controles['baixo']]:
            self.rect.y += self.vel
        if teclas[self.controles['esquerda']]:
            self.rect.x -= self.vel
        if teclas[self.controles['direita']]:
            self.rect.x += self.vel
        self.manter_na_tela()

    def manter_na_tela(self):
        self.rect.x = max(0, min(LARGURA - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(ALTURA - self.rect.height, self.rect.y))

    def pode_atirar(self):
        agora = pygame.time.get_ticks()
        return agora - self.ultimo_tiro > self.cooldown_tiro

class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BRANCO)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 8
        self.direcao = direcao

    def update(self):
        self.rect.x += self.vel * self.direcao
        if self.rect.right < 0 or self.rect.left > LARGURA:
            self.kill()

class Soldado(pygame.sprite.Sprite):
    def __init__(self, x, y, imagem_path=None):
        super().__init__()
        if imagem_path and os.path.exists(imagem_path):
            try:
                self.image = pygame.image.load(imagem_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (40, 60))
            except:
                self.image = pygame.Surface((40, 60))
                self.image.fill(VERMELHO)
        else:
            self.image = pygame.Surface((40, 60))
            self.image.fill(VERMELHO)
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = random.randint(1, 3)
        self.direcao = random.choice([-1, 1])

    def update(self):
        self.rect.x += self.vel * self.direcao
        if self.rect.right > LARGURA or self.rect.left < 0:
            self.direcao *= -1

# Controles dos jogadores
controles1 = {'cima': pygame.K_w, 'baixo': pygame.K_s, 'esquerda': pygame.K_a, 'direita': pygame.K_d, 'atirar': pygame.K_q}
controles2 = {'cima': pygame.K_UP, 'baixo': pygame.K_DOWN, 'esquerda': pygame.K_LEFT, 'direita': pygame.K_RIGHT, 'atirar': pygame.K_RSHIFT}

# Grupos
todos_sprites = pygame.sprite.Group()
projeteis = pygame.sprite.Group()
soldados = pygame.sprite.Group()

# Jogadores
# Modifique os caminhos para suas imagens
jogador1 = Jogador(100, ALTURA//2, AZUL, controles1, 'C:/Users/bruno/OneDrive/Área de Trabalho/Ufsj_p1/ic/8f2ded58003220d09de42706c38bb575-removebg-preview.png')
jogador2 = Jogador(600, ALTURA//2, VERDE, controles2, 'C:/Users/bruno/OneDrive/Área de Trabalho/Ufsj_p1/ic/65925c753581aaca708ce93e5015ef75-removebg-preview.png')
todos_sprites.add(jogador1, jogador2)

# Função para spawnar inimigos
def spawnar_inimigo():
    x = random.randint(0, LARGURA - 40)
    y = random.randint(50, ALTURA - 100)
    soldado = Soldado(x, y, 'C:/Users/bruno/OneDrive/Área de Trabalho/Ufsj_p1/ic/ee8111ec8b5cb30a55487b9d1c8e8f2f-removebg-preview.png')
    soldados.add(soldado)
    todos_sprites.add(soldado)

# Spawn inicial de inimigos
for i in range(5):
    spawnar_inimigo()

# Loop principal
running = True
while running:
    clock.tick(60)
    tempo_atual = pygame.time.get_ticks()
    
    # Controle de spawn de inimigos
    if tempo_atual - spawn_timer > spawn_interval:
        spawnar_inimigo()
        spawn_timer = tempo_atual
        # Aumenta a dificuldade reduzindo o intervalo
        spawn_interval = max(500, spawn_interval - 50)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

    teclas = pygame.key.get_pressed()

    # Atualiza jogadores
    jogador1.update(teclas)
    jogador2.update(teclas)

    # Atirar
    if teclas[controles1['atirar']] and jogador1.pode_atirar():
        projeteis.add(Projetil(jogador1.rect.right, jogador1.rect.centery, 1))
        jogador1.ultimo_tiro = tempo_atual
    if teclas[controles2['atirar']] and jogador2.pode_atirar():
        projeteis.add(Projetil(jogador2.rect.left, jogador2.rect.centery, -1))
        jogador2.ultimo_tiro = tempo_atual

    # Atualiza sprites
    soldados.update()
    projeteis.update()

    # Colisões
    for proj in projeteis:
        atingidos = pygame.sprite.spritecollide(proj, soldados, True)
        for soldado in atingidos:
            proj.kill()
            pontuacao += 10  # Pontuação por inimigo derrotado

    # Desenha na tela
    TELA.fill(PRETO)
    todos_sprites.draw(TELA)
    
    # Mostra pontuação
    texto_pontuacao = fonte.render(f'Pontuação: {pontuacao}', True, BRANCO)
    TELA.blit(texto_pontuacao, (10, 10))
    
    pygame.display.flip()

pygame.quit()
sys.exit()