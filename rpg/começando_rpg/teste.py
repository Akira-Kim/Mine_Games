import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pygame
import threading

# Configuração inicial
if not os.path.exists('dnd_data'):
    os.makedirs('dnd_data')
if not os.path.exists('dnd_images'):
    os.makedirs('dnd_images')
if not os.path.exists('dnd_fonts'):
    os.makedirs('dnd_fonts')

# Cores medievais
COR_FUNDO = "#1a0d00"  # Marrom muito escuro
COR_MOLDUA = "#3c1f0a"  # Marrom escuro
COR_DESTAQUE = "#e0a63a"  # Dourado
COR_TEXTO = "#f0d090"  # Amarelo claro

# Arquivos de dados
DATA_FILES = {
    'racas': 'dnd_data/racas.txt',
    'classes': 'dnd_data/classes.txt',
    'monstros': 'dnd_data/monstros.txt',
    'itens': 'dnd_data/itens.txt'
}

# Criar arquivos de dados iniciais se não existirem
def criar_arquivos_dados():
    for categoria, arquivo in DATA_FILES.items():
        if not os.path.exists(arquivo):
            with open(arquivo, 'w', encoding='utf-8') as f:
                if categoria == 'racas':
                    f.write("""Humano|Adaptáveis e versáteis|+1 em todos os atributos|humano.png
Elfo|Graciosos e conectados à natureza|Visão no escuro, Imunidade a sono|elfo.png
Anão|Resistentes e fortes|+2 Constituição, Visão no escuro|anao.png
Halfling|Pequenos e ágeis|Sortudo, Corajoso|halfling.png
Dragonborn|Descendentes de dragões|Sopro elementar, Resistência a dano|dragonborn.png""")
                elif categoria == 'classes':
                    f.write("""Guerreiro|Especialista em combate físico|Ataque Extra, Estilo de Combate|guerreiro.png
Mago|Usuário de magia arcana|Magia, Recuperação de Magia|mago.png
Clérigo|Canalizador de poder divino|Magia Divina, Domínio Sagrado|clerigo.png
Ladino|Especialista em furtividade|Ataque Furtivo, Habilidades|ladino.png
Bárbaro|Guerreiro selvagem|Fúria, Defesa sem Armadura|barbaro.png""")
                elif categoria == 'monstros':
                    f.write("""Goblin|Pequenas criaturas traiçoeiras|1/4|goblin.png
Dragão|Poderosos répteis voadores|7|dragao.png
Esqueleto|Mortos-vivos animados|1/4|esqueleto.png
Orc|Guerreiros brutais|1/2|orc.png
Mind Flayer|Criaturas psíquicas alienígenas|7|mindflayer.png""")
                elif categoria == 'itens':
                    f.write("""Espada Longa|Arma corpo-a-corpo versátil|Arma|espada.png
Poção de Cura|Restaura pontos de vida|Consumível|pocao.png
Cota de Malha|Armadura de metal interligado|Armadura|armadura.png
Varinha de Magos|Foco para magia arcana|Arcano|varinha.png
Escudo|Proteção adicional em combate|Defesa|escudo.png""")

# Ler dados de um arquivo
def ler_dados(categoria):
    arquivo = DATA_FILES[categoria]
    dados = []
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('|')
                if len(partes) >= 4:
                    dados.append(partes)
    return dados

# Classe principal da aplicação
class DnDLearningGame:
    def __init__(self, root):
        self.root = root
        self.root.title("A Ordem")
        self.root.geometry("1100x800")
        self.root.configure(bg=COR_FUNDO)
        
        # Variável para controle de tela cheia
        self.fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        
        # Carregar fonte medieval (se disponível)
        self.fonte_medieval = None
        try:
            self.fonte_medieval = font.Font(family="MedievalSharp", size=16)
        except:
            try:
                self.fonte_medieval = font.Font(family="Times", size=12, weight="bold")
            except:
                self.fonte_medieval = font.Font()
        
        # Inicializar pygame para música
        pygame.mixer.init()
        self.tocar_musica_fundo()
        
        # Criar arquivos de dados se não existirem
        criar_arquivos_dados()
        
        # Carregar imagens de conteúdo
        self.carregar_imagens()
        
        # Interface principal
        self.create_main_interface()
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        return "break"
    
    def tocar_musica_fundo(self):
        def play_music():
            try:
                # Tenta carregar a música se existir
                if os.path.exists('dnd_data/musica_fundo.mp3'):
                    pygame.mixer.music.load('dnd_data/musica_fundo.mp3')
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                else:
                    print("Arquivo de música não encontrado. Coloque 'musica_fundo.mp3' em dnd_data/")
            except Exception as e:
                print(f"Erro ao reproduzir música: {e}")
        
        music_thread = threading.Thread(target=play_music)
        music_thread.daemon = True
        music_thread.start()
    
    def carregar_imagens(self):
        self.imagens = {}
        
        # Carregar imagens das entidades
        for categoria in ['racas', 'classes', 'monstros', 'itens']:
            dados = ler_dados(categoria)
            for item in dados:
                img_path = f"dnd_images/{item[3]}"
                if os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        img = img.resize((200, 200), Image.LANCZOS)
                        
                        # Adicionar moldura medieval à imagem
                        moldurada = Image.new('RGB', (220, 220), tuple(int(COR_MOLDUA.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
                        moldurada.paste(img, (10, 10))
                        draw = ImageDraw.Draw(moldurada)
                        draw.rectangle([0, 0, 219, 219], outline=COR_DESTAQUE, width=2)
                        
                        self.imagens[item[3]] = ImageTk.PhotoImage(moldurada)
                    except Exception as e:
                        print(f"Erro ao carregar imagem {img_path}: {e}")
                        self.imagens[item[3]] = self.criar_imagem_exemplo(item[0])
                else:
                    self.imagens[item[3]] = self.criar_imagem_exemplo(item[0])
        
        # Imagem padrão para combate
        if 'default.png' not in self.imagens:
            self.imagens['default.png'] = self.criar_imagem_exemplo("D&D")
    
    def criar_imagem_exemplo(self, texto):
        img = Image.new('RGB', (200, 200), color=tuple(int(COR_MOLDUA.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
        d = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.truetype("dnd_fonts/medieval.ttf", 24)
        except:
            try:
                fnt = ImageFont.truetype("arial.ttf", 24)
            except:
                fnt = ImageFont.load_default()
        
        # Desenhar padrão medieval
        for i in range(0, 200, 10):
            for j in range(0, 200, 10):
                if (i//10 + j//10) % 2 == 0:
                    d.rectangle([i, j, i+8, j+8], fill=(110, 55, 20))
        
        # Adicionar texto
        bbox = d.textbbox((0, 0), texto, font=fnt)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text(((200-w)/2, (200-h)/2), texto, fill=COR_DESTAQUE, font=fnt)
        
        # Adicionar moldura
        d.rectangle([0, 0, 199, 199], outline=COR_DESTAQUE, width=2)
        
        return ImageTk.PhotoImage(img)
    
    def create_main_interface(self):
        # Limpar frame atual
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título "A Ordem"
        titulo_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        titulo_frame.pack(pady=20)
        
        titulo_label = tk.Label(titulo_frame, text="A Ordem", 
                               font=("MedievalSharp", 48, "bold") if "MedievalSharp" in font.families() else ("Times", 48, "bold"),
                               fg=COR_DESTAQUE, bg=COR_FUNDO)
        titulo_label.pack()
        
        # Subtítulo
        subtitulo_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        subtitulo_frame.pack(pady=(0, 30))
        
        subtitulo_label = tk.Label(subtitulo_frame, text="Um presentinho para meu amor não odiar RPG", 
                                  font=("MedievalSharp", 18) if "MedievalSharp" in font.families() else ("Times", 18, "italic"),
                                  fg=COR_DESTAQUE, bg=COR_FUNDO)
        subtitulo_label.pack()
        
        # Botões com emojis
        botoes = [
            ("🏹  Explorar Raças", self.show_racas),
            ("⚔️  Dominar Classes", self.show_classes),
            ("👹  Conhecer Monstros", self.show_monstros),
            ("🔮  Descobrir Itens Mágicos", self.show_itens),
            ("⚔️  Desafio de Combate!", self.combate),
            ("🎵  Parar/Continuar Música", self.toggle_music),
            ("🚪  Sair da Taverna", self.sair)
        ]
        
        for texto, comando in botoes:
            btn_frame = tk.Frame(main_frame, bg=COR_FUNDO)
            btn_frame.pack(pady=8)
            
            btn = tk.Button(btn_frame, text=texto, command=comando, 
                           font=self.fonte_medieval,
                           bg=COR_MOLDUA, fg=COR_DESTAQUE, activebackground='#7a5a39', 
                           activeforeground='#ffd700', bd=0, relief='flat',
                           padx=20, pady=5, width=30)
            btn.pack()
    
    def toggle_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    
    def sair(self):
        pygame.mixer.music.stop()
        self.root.destroy()
    
    def show_content(self, categoria, titulo):
        # Limpar frame atual
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        titulo_frame.pack(pady=10)
        
        titulo_label = tk.Label(titulo_frame, text=titulo, 
                              font=("MedievalSharp", 32, "bold") if "MedievalSharp" in font.families() else ("Times", 32, "bold"),
                              fg=COR_DESTAQUE, bg=COR_FUNDO)
        titulo_label.pack()
        
        # Botão voltar
        btn_voltar_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        btn_voltar_frame.pack(anchor='nw', padx=10, pady=10)
        
        btn_voltar = tk.Button(btn_voltar_frame, text="⬅️ Voltar à Taverna", command=self.create_main_interface,
                              font=self.fonte_medieval,
                              bg=COR_MOLDUA, fg=COR_DESTAQUE, activebackground='#7a5a39', 
                              activeforeground='#ffd700', bd=0, relief='flat',
                              padx=10, pady=5)
        btn_voltar.pack()
        
        # Frame para conteúdo com scroll
        container = tk.Frame(main_frame, bg=COR_FUNDO)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas e Scrollbar
        canvas = tk.Canvas(container, bg=COR_MOLDUA, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COR_MOLDUA)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buscar dados
        dados = ler_dados(categoria)
        
        # Exibir dados
        for i, item in enumerate(dados):
            frame = tk.Frame(scrollable_frame, bg=COR_MOLDUA, bd=0, highlightthickness=2, highlightbackground=COR_DESTAQUE)
            frame.pack(fill=tk.X, pady=10, padx=10)
            
            # Coluna da imagem
            img_frame = tk.Frame(frame, bg=COR_MOLDUA)
            img_frame.pack(side=tk.LEFT, padx=10, pady=10)
            
            if item[3] in self.imagens:
                img_label = tk.Label(img_frame, image=self.imagens[item[3]], bg=COR_MOLDUA)
                img_label.image = self.imagens[item[3]]
                img_label.pack()
            
            # Coluna de informações
            info_frame = tk.Frame(frame, bg=COR_MOLDUA)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
            
            tk.Label(info_frame, text=item[0], 
                    font=("MedievalSharp", 18, "bold") if "MedievalSharp" in font.families() else ("Times", 18, "bold"),
                    fg=COR_DESTAQUE, bg=COR_MOLDUA).pack(anchor='w')
            
            tk.Label(info_frame, text=item[1], 
                    font=("MedievalSharp", 12) if "MedievalSharp" in font.families() else ("Times", 12),
                    fg=COR_TEXTO, bg=COR_MOLDUA,
                    wraplength=500, justify='left').pack(anchor='w', pady=5)
            
            tk.Label(info_frame, text="Traços e Características:", 
                    font=("MedievalSharp", 14, "bold") if "MedievalSharp" in font.families() else ("Times", 14, "bold"),
                    fg='#ffaa00', bg=COR_MOLDUA).pack(anchor='w', pady=(10, 0))
            
            tk.Label(info_frame, text=item[2], 
                    font=("MedievalSharp", 11) if "MedievalSharp" in font.families() else ("Times", 11),
                    fg='#e0c080', bg=COR_MOLDUA,
                    wraplength=500, justify='left').pack(anchor='w')
    
    def show_racas(self):
        self.show_content('racas', '🏹 Raças de D&D')
    
    def show_classes(self):
        self.show_content('classes', '⚔️ Classes de Personagem')
    
    def show_monstros(self):
        self.show_content('monstros', '👹 Monstros e Criaturas')
    
    def show_itens(self):
        self.show_content('itens', '🔮 Itens Mágicos')
    
    def combate(self):
        # Limpar frame atual
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        titulo_frame.pack(pady=10)
        
        titulo_label = tk.Label(titulo_frame, text="⚔️ Desafio de Combate!", 
                              font=("MedievalSharp", 32, "bold") if "MedievalSharp" in font.families() else ("Times", 32, "bold"),
                              fg=COR_DESTAQUE, bg=COR_FUNDO)
        titulo_label.pack()
        
        # Botão voltar
        btn_voltar_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        btn_voltar_frame.pack(anchor='nw', padx=10, pady=10)
        
        btn_voltar = tk.Button(btn_voltar_frame, text="⬅️ Voltar à Taverna", command=self.create_main_interface,
                              font=self.fonte_medieval,
                              bg=COR_MOLDUA, fg=COR_DESTAQUE, activebackground='#7a5a39', 
                              activeforeground='#ffd700', bd=0, relief='flat',
                              padx=10, pady=5)
        btn_voltar.pack()
        
        # Frame de combate
        combat_frame = tk.Frame(main_frame, bg=COR_FUNDO)
        combat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Escolher monstro aleatório
        monstros = ler_dados('monstros')
        if not monstros:
            monstros = [["Goblin", "Pequenas criaturas traiçoeiras", "1/4", "goblin.png"]]
        monstro = random.choice(monstros)
        
        # Variáveis de estado
        self.vida_jogador = 30
        self.vida_monstro = random.randint(15, 25)
        self.monstro_atual = monstro
        self.turno_jogador = True  # Começa com o turno do jogador
        
        # Painel do monstro
        monster_frame = tk.Frame(combat_frame, bg=COR_MOLDUA, highlightthickness=2, highlightbackground="red")
        monster_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(monster_frame, text=monstro[0], 
                font=("MedievalSharp", 20, "bold") if "MedievalSharp" in font.families() else ("Times", 20, "bold"),
                fg='#ff6666', bg=COR_MOLDUA).pack(pady=10)
        
        if monstro[3] in self.imagens:
            img_label = tk.Label(monster_frame, image=self.imagens[monstro[3]], bg=COR_MOLDUA)
            img_label.image = self.imagens[monstro[3]]
            img_label.pack(pady=10)
        else:
            img_label = tk.Label(monster_frame, image=self.imagens['default.png'], bg=COR_MOLDUA)
            img_label.image = self.imagens['default.png']
            img_label.pack(pady=10)
        
        tk.Label(monster_frame, text=monstro[1], 
                font=("MedievalSharp", 10) if "MedievalSharp" in font.families() else ("Times", 10),
                fg='#ff9999', bg=COR_MOLDUA,
                wraplength=300).pack(pady=5)
        
        tk.Label(monster_frame, text=f"🔥 Nível de Desafio: {monstro[2]}", 
                font=("MedievalSharp", 12, "bold") if "MedievalSharp" in font.families() else ("Times", 12, "bold"),
                fg='#ffaa00', bg=COR_MOLDUA).pack(pady=5)
        
        self.monster_hp = tk.Label(monster_frame, 
                                  text=f"❤️ Vida: {self.vida_monstro}",
                                  font=("MedievalSharp", 14, "bold") if "MedievalSharp" in font.families() else ("Times", 14, "bold"),
                                  fg='#ff5555', bg=COR_MOLDUA)
        self.monster_hp.pack(pady=10)
        
        # Painel do jogador
        player_frame = tk.Frame(combat_frame, bg=COR_MOLDUA, highlightthickness=2, highlightbackground="green")
        player_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(player_frame, text="Seu Personagem", 
                font=("MedievalSharp", 20, "bold") if "MedievalSharp" in font.families() else ("Times", 20, "bold"),
                fg='#66ff66', bg=COR_MOLDUA).pack(pady=10)
        
        # Usar imagem de classe aleatória
        classes = ler_dados('classes')
        if classes:
            classe = random.choice(classes)
            classe_img = classe[3]
        else:
            classe_img = 'default.png'
        
        if classe_img in self.imagens:
            img_label = tk.Label(player_frame, image=self.imagens[classe_img], bg=COR_MOLDUA)
            img_label.image = self.imagens[classe_img]
            img_label.pack(pady=10)
        else:
            img_label = tk.Label(player_frame, image=self.imagens['default.png'], bg=COR_MOLDUA)
            img_label.image = self.imagens['default.png']
            img_label.pack(pady=10)
        
        self.player_hp = tk.Label(player_frame, 
                                text=f"❤️ Vida: {self.vida_jogador}",
                                font=("MedievalSharp", 14, "bold") if "MedievalSharp" in font.families() else ("Times", 14, "bold"),
                                fg='#55ff55', bg=COR_MOLDUA)
        self.player_hp.pack(pady=10)
        
        # Ações
        action_frame = tk.Frame(player_frame, bg=COR_MOLDUA)
        action_frame.pack(pady=20)
        
        # Botões de ação
        self.btn_atacar = tk.Button(action_frame, text="🗡️ Atacar", command=self.atacar,
                          font=self.fonte_medieval,
                          bg='#7a5a39', fg='gold', activebackground='#9a7a59', 
                          activeforeground='#ffd700', bd=0, relief='flat',
                          width=15)
        self.btn_atacar.pack(pady=5)
        
        self.btn_feitico = tk.Button(action_frame, text="🔮 Lançar Feitiço", command=self.feitico,
                          font=self.fonte_medieval,
                          bg='#7a5a39', fg='gold', activebackground='#9a7a59', 
                          activeforeground='#ffd700', bd=0, relief='flat',
                          width=15)
        self.btn_feitico.pack(pady=5)
        
        self.btn_curar = tk.Button(action_frame, text="❤️ Curar-se", command=self.curar,
                          font=self.fonte_medieval,
                          bg='#7a5a39', fg='gold', activebackground='#9a7a59', 
                          activeforeground='#ffd700', bd=0, relief='flat',
                          width=15)
        self.btn_curar.pack(pady=5)
        
        # Habilitar ações do jogador
        self.habilitar_acoes(True)
    
    def habilitar_acoes(self, estado):
        """Habilita ou desabilita os botões de ação do jogador"""
        estado_btn = tk.NORMAL if estado else tk.DISABLED
        self.btn_atacar.config(state=estado_btn)
        self.btn_feitico.config(state=estado_btn)
        self.btn_curar.config(state=estado_btn)
    
    def finalizar_turno(self):
        """Finaliza o turno do jogador e inicia o turno do monstro"""
        # Desabilitar ações do jogador
        self.habilitar_acoes(False)
        
        # Verificar se o monstro morreu
        if self.vida_monstro <= 0:
            messagebox.showinfo("Vitória!", f"Você derrotou o {self.monstro_atual[0]}! Parabéns!")
            self.create_main_interface()
            return
        
        # Turno do monstro
        self.root.after(1000, self.turno_monstro)
    
    def turno_monstro(self):
        """Executa o turno do monstro"""
        if self.vida_monstro > 0 and self.vida_jogador > 0:
            dano = random.randint(2, 6)
            self.vida_jogador -= dano
            
            # Atualizar display
            self.player_hp.config(text=f"❤️ Vida: {max(0, self.vida_jogador)}")
            messagebox.showinfo("Ataque!", f"O {self.monstro_atual[0]} causa {dano} de dano!")
            
            # Verificar se o jogador morreu
            if self.vida_jogador <= 0:
                messagebox.showinfo("Fim de Combate", "Você foi derrotado! Melhor sorte na próxima vez.")
                self.create_main_interface()
            else:
                # Habilitar ações para o próximo turno do jogador
                self.root.after(1000, lambda: self.habilitar_acoes(True))
    
    def atacar(self):
        """Ação de ataque do jogador"""
        dano = random.randint(3, 8)
        self.vida_monstro -= dano
        
        # Atualizar display
        self.monster_hp.config(text=f"❤️ Vida: {max(0, self.vida_monstro)}")
        messagebox.showinfo("Ataque!", f"Você causa {dano} de dano ao {self.monstro_atual[0]}!")
        
        # Finalizar turno do jogador
        self.finalizar_turno()
    
    def feitico(self):
        """Ação de lançar feitiço do jogador"""
        dano = random.randint(1, 12)
        self.vida_monstro -= dano
        
        # Atualizar display
        self.monster_hp.config(text=f"❤️ Vida: {max(0, self.vida_monstro)}")
        messagebox.showinfo("Feitiço!", f"Seu feitiço causa {dano} de dano ao {self.monstro_atual[0]}!")
        
        # Finalizar turno do jogador
        self.finalizar_turno()
    
    def curar(self):
        """Ação de cura do jogador"""
        cura = random.randint(4, 10)
        self.vida_jogador += cura
        
        # Atualizar display
        self.player_hp.config(text=f"❤️ Vida: {self.vida_jogador}")
        messagebox.showinfo("Cura!", f"Você recupera {cura} pontos de vida!")
        
        # Finalizar turno do jogador
        self.finalizar_turno()

# Iniciar aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = DnDLearningGame(root)
    root.mainloop()