import os
import json
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
from PIL import Image, ImageTk
import pygame
from datetime import datetime

# Configurações iniciais
VERSION = "1.0"
DATA_DIR = "rpg_data"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.txt")
QUESTS_FILE = os.path.join(DATA_DIR, "quests.txt")
PARTY_FILE = os.path.join(DATA_DIR, "party.txt")
ITEMS_FILE = os.path.join(DATA_DIR, "items.txt")
NPCS_FILE = os.path.join(DATA_DIR, "npcs.txt")
ENCOUNTERS_FILE = os.path.join(DATA_DIR, "encounters.txt")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
SOUND_DIR = "sounds"

# Paleta de cores cyber-medieval
CYBER_BLUE = "#00e5ff"
CYBER_PURPLE = "#9d00ff"
MEDIEVAL_GOLD = "#d4af37"
MEDIEVAL_RED = "#8b0000"
DARK_BG = "#0c0c1a"
LIGHT_TEXT = "#f0f0f0"
DARK_TEXT = "#0c0c1a"

# Fontes
TITLE_FONT = ("Georgia", 24, "bold")
HEADER_FONT = ("Segoe UI", 14, "bold")
BODY_FONT = ("Segoe UI", 11)
BUTTON_FONT = ("Segoe UI", 10, "bold")

# Inicializar pygame para sons
pygame.mixer.init()

# Criar diretórios se não existirem
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(SOUND_DIR, exist_ok=True)

class SoundSystem:
    def __init__(self):
        self.sounds = {}
        self.music_enabled = True
        self.sound_enabled = True
        self.load_sounds()
    
    def load_sounds(self):
        sounds_to_load = {
            "click": "click.wav",
            "level_up": "level_up.wav",
            "combat": "combat.wav",
            "magic": "magic.wav"
        }
        
        for name, file in sounds_to_load.items():
            path = os.path.join(SOUND_DIR, file)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except:
                    pass
    
    def play_sound(self, name):
        if not self.sound_enabled or name not in self.sounds:
            return
        self.sounds[name].play()

class Character:
    def __init__(self, name):
        self.name = name
        self.race = "Humano"
        self.character_class = "Guerreiro"
        self.level = 1
        self.hp = [100, 100]  # [atual, máximo]
        self.mana = [50, 50]
        self.sanity = [80, 100]
        self.honor = 50
        self.attributes = {
            "Força": 10,
            "Destreza": 10,
            "Constituição": 10,
            "Inteligência": 10,
            "Sabedoria": 10,
            "Carisma": 10
        }
        self.skills = []
        self.inventory = []
        self.image_path = ""
        self.bio = ""
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def take_damage(self, amount):
        self.hp[0] = max(0, self.hp[0] - amount)
        return self.hp[0] <= 0
    
    def heal(self, amount):
        self.hp[0] = min(self.hp[1], self.hp[0] + amount)
    
    def use_mana(self, amount):
        if self.mana[0] >= amount:
            self.mana[0] -= amount
            return True
        return False
    
    def restore_mana(self, amount):
        self.mana[0] = min(self.mana[1], self.mana[0] + amount)
    
    def adjust_sanity(self, amount):
        self.sanity[0] = max(0, min(100, self.sanity[0] + amount))
    
    def adjust_honor(self, amount):
        self.honor = max(0, min(100, self.honor + amount))
    
    def level_up(self):
        self.level += 1
        self.hp[1] += 10
        self.hp[0] = self.hp[1]
        self.mana[1] += 5
        self.mana[0] = self.mana[1]
        self.sanity[0] = min(100, self.sanity[0] + 5)
        return True
    
    def to_dict(self):
        return {
            "name": self.name,
            "race": self.race,
            "class": self.character_class,
            "level": self.level,
            "hp": self.hp,
            "mana": self.mana,
            "sanity": self.sanity,
            "honor": self.honor,
            "attributes": self.attributes,
            "skills": self.skills,
            "inventory": self.inventory,
            "image_path": self.image_path,
            "bio": self.bio,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data):
        char = cls(data["name"])
        char.race = data.get("race", "Humano")
        char.character_class = data.get("class", "Guerreiro")
        char.level = data.get("level", 1)
        char.hp = data.get("hp", [100, 100])
        char.mana = data.get("mana", [50, 50])
        char.sanity = data.get("sanity", [80, 100])
        char.honor = data.get("honor", 50)
        char.attributes = data.get("attributes", {
            "Força": 10, "Destreza": 10, "Constituição": 10,
            "Inteligência": 10, "Sabedoria": 10, "Carisma": 10
        })
        char.skills = data.get("skills", [])
        char.inventory = data.get("inventory", [])
        char.image_path = data.get("image_path", "")
        char.bio = data.get("bio", "")
        char.last_updated = data.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M"))
        return char

class Quest:
    def __init__(self, title):
        self.title = title
        self.description = ""
        self.objectives = []
        self.rewards = {"xp": 0, "gold": 0, "items": []}
        self.status = "Ativa"  # Ativa, Completa, Falhada
        self.assigned_to = ""
        self.created_date = datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "created_date": self.created_date
        }
    
    @classmethod
    def from_dict(cls, data):
        quest = cls(data["title"])
        quest.description = data.get("description", "")
        quest.objectives = data.get("objectives", [])
        quest.rewards = data.get("rewards", {"xp": 0, "gold": 0, "items": []})
        quest.status = data.get("status", "Ativa")
        quest.assigned_to = data.get("assigned_to", "")
        quest.created_date = data.get("created_date", datetime.now().strftime("%Y-%m-%d"))
        return quest

class Party:
    def __init__(self):
        self.name = "Grupo de Aventureiros"
        self.members = []
        self.inventory = []
        self.funds = 100
        self.reputation = 50
        self.created_date = datetime.now().strftime("%Y-%m-%d")
    
    def add_member(self, character_name):
        if character_name not in self.members:
            self.members.append(character_name)
    
    def remove_member(self, character_name):
        if character_name in self.members:
            self.members.remove(character_name)
    
    def add_funds(self, amount):
        self.funds += amount
    
    def spend_funds(self, amount):
        if self.funds >= amount:
            self.funds -= amount
            return True
        return False
    
    def to_dict(self):
        return {
            "name": self.name,
            "members": self.members,
            "inventory": self.inventory,
            "funds": self.funds,
            "reputation": self.reputation,
            "created_date": self.created_date
        }
    
    @classmethod
    def from_dict(cls, data):
        party = cls()
        party.name = data.get("name", "Grupo de Aventureiros")
        party.members = data.get("members", [])
        party.inventory = data.get("inventory", [])
        party.funds = data.get("funds", 100)
        party.reputation = data.get("reputation", 50)
        party.created_date = data.get("created_date", datetime.now().strftime("%Y-%m-%d"))
        return party

class NPC:
    def __init__(self, name):
        self.name = name
        self.race = "Humano"
        self.occupation = "Mercador"
        self.disposition = "Neutro"
        self.secret = ""
        self.quest_offer = ""
        self.image_path = ""
    
    def to_dict(self):
        return {
            "name": self.name,
            "race": self.race,
            "occupation": self.occupation,
            "disposition": self.disposition,
            "secret": self.secret,
            "quest_offer": self.quest_offer,
            "image_path": self.image_path
        }
    
    @classmethod
    def from_dict(cls, data):
        npc = cls(data["name"])
        npc.race = data.get("race", "Humano")
        npc.occupation = data.get("occupation", "Mercador")
        npc.disposition = data.get("disposition", "Neutro")
        npc.secret = data.get("secret", "")
        npc.quest_offer = data.get("quest_offer", "")
        npc.image_path = data.get("image_path", "")
        return npc

class Item:
    def __init__(self, name):
        self.name = name
        self.item_type = "Geral"
        self.description = ""
        self.weight = 0.0
        self.value = 0
        self.magical = False
        self.equippable = False
        self.image_path = ""
    
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.item_type,
            "description": self.description,
            "weight": self.weight,
            "value": self.value,
            "magical": self.magical,
            "equippable": self.equippable,
            "image_path": self.image_path
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(data["name"])
        item.item_type = data.get("type", "Geral")
        item.description = data.get("description", "")
        item.weight = data.get("weight", 0.0)
        item.value = data.get("value", 0)
        item.magical = data.get("magical", False)
        item.equippable = data.get("equippable", False)
        item.image_path = data.get("image_path", "")
        return item

class DataManager:
    @staticmethod
    def save_data(data, filename):
        try:
            with open(filename, 'w') as f:
                if isinstance(data, list):
                    for item in data:
                        json.dump(item, f)
                        f.write('\n')
                else:
                    json.dump(data, f)
                    f.write('\n')
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar dados: {str(e)}")
            return False
    
    @staticmethod
    def load_data(filename):
        data = []
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    for line in f:
                        data.append(json.loads(line))
            return data
        except:
            return []

class Generator:
    RACES = ["Humano", "Elfo", "Anão", "Halfling", "Draconato", "Gnomo", "Meio-Elfo", "Meio-Orc", "Tiefling"]
    CLASSES = ["Guerreiro", "Mago", "Clérigo", "Ladino", "Bárbaro", "Bardo", "Druida", "Monge", "Paladino", "Patrulheiro"]
    OCCUPATIONS = ["Ferreiro", "Mercador", "Nobre", "Sacerdote", "Ladrão", "Sábio", "Curandeiro", "Caçador", "Soldado", "Bardo"]
    DISPOSITIONS = ["Amigável", "Neutro", "Desconfiado", "Hostil", "Louco", "Enigmático"]
    ITEM_TYPES = ["Arma", "Armadura", "Poção", "Pergaminho", "Relíquia", "Joia", "Livro", "Ferramenta", "Componente"]
    MONSTER_TYPES = ["Goblin", "Orc", "Troll", "Esqueleto", "Zumbi", "Vampiro", "Lobo", "Urso", "Dragão", "Demônio", "Fada", "Elemental"]
    
    @staticmethod
    def generate_npc():
        npc = NPC(f"{random.choice(['Ara', 'Brin', 'Cor', 'Dae', 'Eli'])}{random.choice(['thas', 'wyn', 'dor', 'lia', 'van'])}")
        npc.race = random.choice(Generator.RACES)
        npc.occupation = random.choice(Generator.OCCUPATIONS)
        npc.disposition = random.choice(Generator.DISPOSITIONS)
        npc.secret = random.choice([
            "É um espião", "Tem um mapa do tesouro", "É um mago disfarçado",
            "Procura vingança", "Esconde uma relíquia poderosa"
        ])
        npc.quest_offer = random.choice([
            "Derrotar um monstro", "Recuperar um item roubado", "Proteger uma caravana",
            "Investigar ruínas antigas", "Entregar uma mensagem importante"
        ])
        return npc
    
    @staticmethod
    def generate_item():
        prefixes = ["Antigo", "Rúnico", "Brilhante", "Sombrio", "Sagrado", "Amaldiçoado", "Élfico", "Anão"]
        suffixes = ["do Poder", "da Sabedoria", "da Coragem", "da Perdição", "da Proteção", "da Sorte"]
        item_types = ["Espada", "Machado", "Cajado", "Armadura", "Escudo", "Amuleto", "Anel", "Poção", "Mapa"]
        
        item = Item(f"{random.choice(prefixes)} {random.choice(item_types)} {random.choice(suffixes)}")
        item.item_type = random.choice(Generator.ITEM_TYPES)
        item.description = random.choice([
            "Um item de aparência incomum que emana energia mágica",
            "Bem trabalhado com detalhes intrincados",
            "Mostra sinais de desgaste, mas ainda funcional",
            "Coberto de runas antigas e incompreensíveis"
        ])
        item.weight = round(random.uniform(0.1, 10.0), 1)
        item.value = random.randint(10, 1000)
        item.magical = random.choice([True, False])
        item.equippable = random.choice([True, False])
        return item
    
    @staticmethod
    def generate_encounter(level):
        encounter = {
            "name": f"Encontro com {random.choice(Generator.MONSTER_TYPES)}s",
            "monsters": [],
            "difficulty": random.choice(["Fácil", "Médio", "Difícil", "Mortal"]),
            "environment": random.choice(["Floresta", "Caverna", "Ruínas", "Pântano", "Cidade"]),
            "challenge": random.randint(1, 20)
        }
        
        monster_count = random.randint(1, 8)
        for _ in range(monster_count):
            monster = {
                "type": random.choice(Generator.MONSTER_TYPES),
                "hp": random.randint(5, 50) * level,
                "ac": random.randint(10, 20),
                "damage": f"{random.randint(1, 8)}d{random.randint(4, 12)}",
                "special": random.choice(["Nenhum", "Veneno", "Fogo", "Gelo", "Eletricidade", "Medo"])
            }
            encounter["monsters"].append(monster)
        
        return encounter

class ImageManager:
    def __init__(self):
        self.cache = {}
    
    def get_image(self, path, size=(100, 100)):
        if not path or not os.path.exists(path):
            return None
        
        key = f"{path}_{size[0]}_{size[1]}"
        if key not in self.cache:
            try:
                img = Image.open(path)
                img = img.resize(size, Image.LANCZOS)
                self.cache[key] = ImageTk.PhotoImage(img)
            except:
                return None
        return self.cache[key]

class CyberMedievalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Escudo do Mestre - Cyber Medieval")
        self.root.geometry("1200x800")
        self.root.configure(bg=DARK_BG)
        
        # Configurações
        self.sound_system = SoundSystem()
        self.image_manager = ImageManager()
        self.data_manager = DataManager()
        self.current_character = None
        self.current_quest = None
        self.current_npc = None
        self.current_item = None
        self.dark_mode = True
        
        # Carregar dados
        self.characters = self.load_characters()
        self.quests = self.load_quests()
        self.party = self.load_party()
        self.npcs = self.load_npcs()
        self.items = self.load_items()
        
        # Configurar tema
        self.setup_theme()
        
        # Criar interface
        self.create_main_frame()
        self.create_main_menu()
        
        # Tocar som de início
        self.sound_system.play_sound("click")
    
    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_create("cyber_medieval", parent="alt", settings={
            "TFrame": {"configure": {"background": DARK_BG}},
            "TLabel": {"configure": {"background": DARK_BG, "foreground": LIGHT_TEXT, "font": BODY_FONT}},
            "TButton": {"configure": {
                "background": MEDIEVAL_GOLD, 
                "foreground": DARK_BG, 
                "font": BUTTON_FONT,
                "borderwidth": 2,
                "relief": "raised"
            }},
            "TNotebook": {"configure": {"background": DARK_BG, "borderwidth": 0}},
            "TNotebook.Tab": {
                "configure": {"background": "#1a1a2e", "foreground": LIGHT_TEXT, "font": HEADER_FONT, "padding": [10, 5]},
                "map": {"background": [("selected", CYBER_PURPLE)], "foreground": [("selected", LIGHT_TEXT)]}
            }
        })
        self.style.theme_use("cyber_medieval")
    
    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, text="ESCUDO DO MESTRE", style="TLabel", 
                         font=TITLE_FONT, foreground=CYBER_BLUE)
        title.pack(side="left", padx=10)
        
        subtitle = ttk.Label(header_frame, text="Cyber Medieval RPG Manager", 
                            font=HEADER_FONT, foreground=MEDIEVAL_GOLD)
        subtitle.pack(side="left", padx=10)
        
        # Área de conteúdo
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True)
    
    def create_main_menu(self):
        self.clear_content()
        
        menu_frame = ttk.Frame(self.content_frame)
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Título do menu
        title = ttk.Label(menu_frame, text="Menu Principal", style="TLabel", font=TITLE_FONT)
        title.pack(pady=(0, 30))
        
        # Botões
        buttons = [
            ("Gerenciar Personagens", self.show_character_manager),
            ("Missões e Questlines", self.show_quest_manager),
            ("Gerenciar Grupo", self.show_party_manager),
            ("NPCs e Inimigos", self.show_npc_manager),
            ("Inventário e Itens", self.show_item_manager),
            ("Gerador de Encontros", self.show_encounter_generator),
            ("Painel do Mestre", self.show_master_panel),
            ("Sair", self.root.quit)
        ]
        
        for text, command in buttons:
            btn_frame = ttk.Frame(menu_frame)
            btn_frame.pack(fill="x", pady=8)
            
            btn = ttk.Button(btn_frame, text=text, command=command, style="TButton")
            btn.pack(ipady=10, ipadx=20, fill="x")
        
        # Rodapé
        footer = ttk.Label(menu_frame, text=f"Versão {VERSION} | Sistema Cyber-Medieval", 
                         font=("Segoe UI", 9), foreground=MEDIEVAL_GOLD)
        footer.pack(side="bottom", pady=20)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def load_characters(self):
        characters = []
        raw_data = self.data_manager.load_data(PLAYERS_FILE)
        for data in raw_data:
            characters.append(Character.from_dict(data))
        return characters
    
    def load_quests(self):
        quests = []
        raw_data = self.data_manager.load_data(QUESTS_FILE)
        for data in raw_data:
            quests.append(Quest.from_dict(data))
        return quests
    
    def load_party(self):
        raw_data = self.data_manager.load_data(PARTY_FILE)
        if raw_data:
            return Party.from_dict(raw_data[0])
        return Party()
    
    def load_npcs(self):
        npcs = []
        raw_data = self.data_manager.load_data(NPCS_FILE)
        for data in raw_data:
            npcs.append(NPC.from_dict(data))
        return npcs
    
    def load_items(self):
        items = []
        raw_data = self.data_manager.load_data(ITEMS_FILE)
        for data in raw_data:
            items.append(Item.from_dict(data))
        return items
    
    def save_characters(self):
        data = [char.to_dict() for char in self.characters]
        return self.data_manager.save_data(data, PLAYERS_FILE)
    
    def save_quests(self):
        data = [quest.to_dict() for quest in self.quests]
        return self.data_manager.save_data(data, QUESTS_FILE)
    
    def save_party(self):
        return self.data_manager.save_data([self.party.to_dict()], PARTY_FILE)
    
    def save_npcs(self):
        data = [npc.to_dict() for npc in self.npcs]
        return self.data_manager.save_data(data, NPCS_FILE)
    
    def save_items(self):
        data = [item.to_dict() for item in self.items]
        return self.data_manager.save_data(data, ITEMS_FILE)
    
    def show_character_manager(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Gerenciar Personagens", font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        new_btn = ttk.Button(btn_frame, text="Novo Personagem", 
                            command=self.create_new_character, style="TButton")
        new_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Voltar", 
                             command=self.create_main_menu, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        # Lista de personagens
        list_frame = ttk.LabelFrame(main_frame, text="Personagens", style="TFrame")
        list_frame.pack(fill="both", expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.char_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            bg="#1a1a2e", 
            fg=MEDIEVAL_GOLD, 
            font=BODY_FONT,
            selectbackground=CYBER_PURPLE,
            selectforeground=LIGHT_TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            height=15
        )
        self.char_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.char_listbox.yview)
        
        for char in self.characters:
            self.char_listbox.insert(tk.END, f"{char.name} ({char.race} {char.character_class} Nv.{char.level})")
        
        # Botões de gerenciamento
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)
        
        view_btn = ttk.Button(action_frame, text="Visualizar", 
                             command=self.view_character, style="TButton")
        view_btn.pack(side="left", padx=5)
        
        edit_btn = ttk.Button(action_frame, text="Editar", 
                             command=self.edit_character, style="TButton")
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ttk.Button(action_frame, text="Excluir", 
                               command=self.delete_character, style="TButton")
        delete_btn.pack(side="left", padx=5)
    
    def create_new_character(self):
        name = simpledialog.askstring("Novo Personagem", "Nome do personagem:")
        if name:
            new_char = Character(name)
            self.characters.append(new_char)
            self.save_characters()
            self.show_character_manager()
            self.sound_system.play_sound("click")
    
    def view_character(self):
        selected = self.char_listbox.curselection()
        if not selected:
            return
        
        char_index = selected[0]
        self.current_character = self.characters[char_index]
        self.show_character_sheet()
    
    def edit_character(self):
        selected = self.char_listbox.curselection()
        if not selected:
            return
        
        char_index = selected[0]
        self.current_character = self.characters[char_index]
        self.show_character_editor()
    
    def delete_character(self):
        selected = self.char_listbox.curselection()
        if not selected:
            return
        
        char_index = selected[0]
        char_name = self.characters[char_index].name
        
        if messagebox.askyesno("Confirmar", f"Excluir {char_name} permanentemente?"):
            del self.characters[char_index]
            self.save_characters()
            self.show_character_manager()
            self.sound_system.play_sound("click")
    
    def show_character_sheet(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        if not self.current_character:
            return
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, 
                         text=f"Ficha de {self.current_character.name}", 
                         font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        back_btn = ttk.Button(btn_frame, text="Voltar", 
                             command=self.show_character_manager, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        edit_btn = ttk.Button(btn_frame, text="Editar", 
                             command=self.show_character_editor, style="TButton")
        edit_btn.pack(side="left", padx=5)
        
        # Corpo da ficha
        body_frame = ttk.Frame(main_frame)
        body_frame.pack(fill="both", expand=True)
        
        # Coluna esquerda (informações básicas)
        left_frame = ttk.Frame(body_frame)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        # Imagem do personagem
        img_frame = ttk.LabelFrame(left_frame, text="Imagem")
        img_frame.pack(fill="x", pady=5)
        
        img_path = self.current_character.image_path
        img = self.image_manager.get_image(img_path, (200, 250)) if img_path else None
        
        if img:
            img_label = ttk.Label(img_frame, image=img)
            img_label.image = img
            img_label.pack(padx=10, pady=10)
        else:
            ttk.Label(img_frame, text="Sem imagem", font=BODY_FONT).pack(padx=10, pady=10)
        
        # Informações básicas
        info_frame = ttk.LabelFrame(left_frame, text="Informações Básicas")
        info_frame.pack(fill="x", pady=5)
        
        info_data = [
            ("Raça", self.current_character.race),
            ("Classe", self.current_character.character_class),
            ("Nível", self.current_character.level),
            ("Honra", self.current_character.honor)
        ]
        
        for label, value in info_data:
            frame = ttk.Frame(info_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{label}:", width=10, anchor="w").pack(side="left")
            ttk.Label(frame, text=value, font=BODY_FONT).pack(side="left")
        
        # Coluna direita (atributos e status)
        right_frame = ttk.Frame(body_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Atributos
        attrs_frame = ttk.LabelFrame(right_frame, text="Atributos")
        attrs_frame.pack(fill="x", pady=5)
        
        for attr, value in self.current_character.attributes.items():
            frame = ttk.Frame(attrs_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{attr}:", width=15, anchor="w").pack(side="left")
            ttk.Label(frame, text=value, font=HEADER_FONT).pack(side="left")
        
        # Status
        status_frame = ttk.LabelFrame(right_frame, text="Status")
        status_frame.pack(fill="x", pady=5)
        
        status_data = [
            ("Vida", f"{self.current_character.hp[0]}/{self.current_character.hp[1]}"),
            ("Mana", f"{self.current_character.mana[0]}/{self.current_character.mana[1]}"),
            ("Sanidade", f"{self.current_character.sanity[0]}/{self.current_character.sanity[1]}")
        ]
        
        for label, value in status_data:
            frame = ttk.Frame(status_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{label}:", width=10, anchor="w").pack(side="left")
            ttk.Label(frame, text=value, font=BODY_FONT).pack(side="left")
        
        # Bio
        bio_frame = ttk.LabelFrame(right_frame, text="Biografia")
        bio_frame.pack(fill="both", expand=True, pady=5)
        
        bio_text = scrolledtext.ScrolledText(bio_frame, width=60, height=10, font=BODY_FONT)
        bio_text.insert("1.0", self.current_character.bio)
        bio_text.configure(state="disabled")
        bio_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def show_character_editor(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        if not self.current_character:
            return
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, 
                         text=f"Editando: {self.current_character.name}", 
                         font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        save_btn = ttk.Button(btn_frame, text="Salvar", 
                             command=self.save_character, style="TButton")
        save_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Cancelar", 
                             command=self.show_character_sheet, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        # Corpo do editor
        body_frame = ttk.Frame(main_frame)
        body_frame.pack(fill="both", expand=True)
        
        # Coluna esquerda
        left_frame = ttk.Frame(body_frame)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        # Imagem
        img_frame = ttk.LabelFrame(left_frame, text="Imagem do Personagem")
        img_frame.pack(fill="x", pady=5)
        
        self.img_path_var = tk.StringVar(value=self.current_character.image_path)
        
        img_btn = ttk.Button(img_frame, text="Selecionar Imagem", 
                            command=self.select_character_image, style="TButton")
        img_btn.pack(pady=10)
        
        # Informações básicas
        info_frame = ttk.LabelFrame(left_frame, text="Informações Básicas")
        info_frame.pack(fill="x", pady=5)
        
        fields = [
            ("Nome:", "name", self.current_character.name),
            ("Raça:", "race", self.current_character.race),
            ("Classe:", "class", self.current_character.character_class),
            ("Nível:", "level", self.current_character.level),
            ("Honra:", "honor", self.current_character.honor)
        ]
        
        self.char_vars = {}
        
        for label, key, value in fields:
            frame = ttk.Frame(info_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=label, width=10).pack(side="left")
            var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=var, font=BODY_FONT)
            entry.pack(fill="x", expand=True)
            self.char_vars[key] = var
        
        # Coluna direita
        right_frame = ttk.Frame(body_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Atributos
        attrs_frame = ttk.LabelFrame(right_frame, text="Atributos")
        attrs_frame.pack(fill="x", pady=5)
        
        self.attr_vars = {}
        for attr in self.current_character.attributes:
            frame = ttk.Frame(attrs_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=f"{attr}:", width=15).pack(side="left")
            var = tk.StringVar(value=self.current_character.attributes[attr])
            spin = ttk.Spinbox(frame, from_=1, to=20, textvariable=var, width=5)
            spin.pack(side="left")
            self.attr_vars[attr] = var
        
        # Status
        status_frame = ttk.LabelFrame(right_frame, text="Status")
        status_frame.pack(fill="x", pady=5)
        
        status_fields = [
            ("Vida Atual:", "hp_current", self.current_character.hp[0]),
            ("Vida Máxima:", "hp_max", self.current_character.hp[1]),
            ("Mana Atual:", "mana_current", self.current_character.mana[0]),
            ("Mana Máxima:", "mana_max", self.current_character.mana[1]),
            ("Sanidade:", "sanity", self.current_character.sanity[0])
        ]
        
        self.status_vars = {}
        for label, key, value in status_fields:
            frame = ttk.Frame(status_frame)
            frame.pack(fill="x", pady=2)
            
            ttk.Label(frame, text=label, width=15).pack(side="left")
            var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.pack(side="left")
            self.status_vars[key] = var
        
        # Bio
        bio_frame = ttk.LabelFrame(right_frame, text="Biografia")
        bio_frame.pack(fill="both", expand=True, pady=5)
        
        self.bio_text = scrolledtext.ScrolledText(bio_frame, width=60, height=10, font=BODY_FONT)
        self.bio_text.insert("1.0", self.current_character.bio)
        self.bio_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def select_character_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.img_path_var.set(file_path)
    
    def save_character(self):
        try:
            # Atualizar campos básicos
            self.current_character.name = self.char_vars["name"].get()
            self.current_character.race = self.char_vars["race"].get()
            self.current_character.character_class = self.char_vars["class"].get()
            self.current_character.level = int(self.char_vars["level"].get())
            self.current_character.honor = int(self.char_vars["honor"].get())
            self.current_character.image_path = self.img_path_var.get()
            
            # Atualizar atributos
            for attr, var in self.attr_vars.items():
                self.current_character.attributes[attr] = int(var.get())
            
            # Atualizar status
            self.current_character.hp = [
                int(self.status_vars["hp_current"].get()),
                int(self.status_vars["hp_max"].get())
            ]
            self.current_character.mana = [
                int(self.status_vars["mana_current"].get()),
                int(self.status_vars["mana_max"].get())
            ]
            self.current_character.sanity[0] = int(self.status_vars["sanity"].get())
            
            # Atualizar bio
            self.current_character.bio = self.bio_text.get("1.0", "end-1c")
            self.current_character.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Salvar
            self.save_characters()
            self.sound_system.play_sound("click")
            self.show_character_sheet()
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos")
    
    def show_quest_manager(self):
        self.clear_content()
        self.sound_system.play_sound("click")

        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        header = ttk.Label(main_frame, text="Missões e Questlines", font=TITLE_FONT)
        header.pack(pady=10)

        quest_listbox = tk.Listbox(main_frame, bg="#1a1a2e", fg=CYBER_BLUE, font=BODY_FONT,
                                   selectbackground=CYBER_PURPLE, selectforeground=LIGHT_TEXT)
        quest_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for quest in self.quests:
            quest_listbox.insert(tk.END, f"{quest.title} ({quest.status})")

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Voltar", command=self.create_main_menu, style="TButton").pack(side="left", padx=5)
    
    def show_party_manager(self):
        self.clear_content()
        self.sound_system.play_sound("click")

        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        header = ttk.Label(main_frame, text="Gerenciar Grupo", font=TITLE_FONT)
        header.pack(pady=10)

        # Formulário de edição do grupo
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Nome do grupo
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill="x", pady=5)
        ttk.Label(name_frame, text="Nome do Grupo:").pack(side="left", padx=(0, 10))
        self.party_name_var = tk.StringVar(value=self.party.name)
        name_entry = ttk.Entry(name_frame, textvariable=self.party_name_var, font=BODY_FONT)
        name_entry.pack(fill="x", expand=True)
        
        # Fundos
        funds_frame = ttk.Frame(form_frame)
        funds_frame.pack(fill="x", pady=5)
        ttk.Label(funds_frame, text="Fundos (moedas):").pack(side="left", padx=(0, 10))
        self.party_funds_var = tk.IntVar(value=self.party.funds)
        funds_spin = ttk.Spinbox(funds_frame, from_=0, to=1000000, textvariable=self.party_funds_var, width=10)
        funds_spin.pack(side="left")
        
        # Reputação
        rep_frame = ttk.Frame(form_frame)
        rep_frame.pack(fill="x", pady=5)
        ttk.Label(rep_frame, text="Reputação:").pack(side="left", padx=(0, 10))
        self.party_rep_var = tk.IntVar(value=self.party.reputation)
        rep_spin = ttk.Spinbox(rep_frame, from_=0, to=100, textvariable=self.party_rep_var, width=10)
        rep_spin.pack(side="left")
        
        # Membros do grupo
        members_frame = ttk.LabelFrame(form_frame, text="Membros")
        members_frame.pack(fill="both", expand=True, pady=10)
        
        # Lista de membros
        scrollbar = ttk.Scrollbar(members_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.party_listbox = tk.Listbox(
            members_frame, 
            yscrollcommand=scrollbar.set,
            bg="#1a1a2e", 
            fg=MEDIEVAL_GOLD, 
            font=BODY_FONT,
            selectbackground=CYBER_PURPLE,
            selectforeground=LIGHT_TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            height=8
        )
        self.party_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.party_listbox.yview)
        
        for member in self.party.members:
            self.party_listbox.insert(tk.END, member)
        
        # Botões de membros
        member_btn_frame = ttk.Frame(members_frame)
        member_btn_frame.pack(fill="x", pady=5)
        
        add_btn = ttk.Button(member_btn_frame, text="Adicionar Membro", 
                            command=self.add_party_member, style="TButton")
        add_btn.pack(side="left", padx=5)
        
        remove_btn = ttk.Button(member_btn_frame, text="Remover Membro", 
                               command=self.remove_party_member, style="TButton")
        remove_btn.pack(side="left", padx=5)
        
        # Botões principais
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        save_btn = ttk.Button(btn_frame, text="Salvar Grupo", 
                             command=self.save_party_changes, style="TButton")
        save_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Voltar", 
                             command=self.create_main_menu, style="TButton")
        back_btn.pack(side="left", padx=5)
    
    def add_party_member(self):
        # Lista de personagens disponíveis
        available_chars = [char.name for char in self.characters if char.name not in self.party.members]
        
        if not available_chars:
            messagebox.showinfo("Info", "Todos os personagens já estão no grupo!")
            return
        
        selected = simpledialog.askstring("Adicionar Membro", "Nome do personagem:", 
                                         initialvalue=available_chars[0])
        if selected and selected in available_chars:
            self.party.add_member(selected)
            self.party_listbox.insert(tk.END, selected)
            self.sound_system.play_sound("click")
    
    def remove_party_member(self):
        selected = self.party_listbox.curselection()
        if not selected:
            return
            
        member_index = selected[0]
        member_name = self.party_listbox.get(member_index)
        self.party.remove_member(member_name)
        self.party_listbox.delete(member_index)
        self.sound_system.play_sound("click")
    
    def save_party_changes(self):
        try:
            self.party.name = self.party_name_var.get()
            self.party.funds = self.party_funds_var.get()
            self.party.reputation = self.party_rep_var.get()
            self.save_party()
            messagebox.showinfo("Sucesso", "Grupo salvo com sucesso!")
            self.sound_system.play_sound("click")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar grupo: {str(e)}")
    
    def show_npc_manager(self):
        self.clear_content()
        self.sound_system.play_sound("click")

        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        header = ttk.Label(main_frame, text="NPCs e Inimigos", font=TITLE_FONT)
        header.pack(pady=10)

        # Lista de NPCs
        list_frame = ttk.LabelFrame(main_frame, text="NPCs")
        list_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.npc_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            bg="#1a1a2e", 
            fg=MEDIEVAL_RED, 
            font=BODY_FONT,
            selectbackground=CYBER_PURPLE,
            selectforeground=LIGHT_TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            height=10
        )
        self.npc_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.npc_listbox.yview)
        
        for npc in self.npcs:
            self.npc_listbox.insert(tk.END, f"{npc.name} ({npc.occupation})")
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)
        
        new_btn = ttk.Button(action_frame, text="Novo NPC", 
                            command=self.create_new_npc, style="TButton")
        new_btn.pack(side="left", padx=5)
        
        view_btn = ttk.Button(action_frame, text="Visualizar", 
                             command=self.view_npc, style="TButton")
        view_btn.pack(side="left", padx=5)
        
        edit_btn = ttk.Button(action_frame, text="Editar", 
                             command=self.edit_npc, style="TButton")
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ttk.Button(action_frame, text="Excluir", 
                               command=self.delete_npc, style="TButton")
        delete_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(action_frame, text="Voltar", 
                             command=self.create_main_menu, style="TButton")
        back_btn.pack(side="right", padx=5)
    
    def create_new_npc(self):
        name = simpledialog.askstring("Novo NPC", "Nome do NPC:")
        if name:
            new_npc = NPC(name)
            self.npcs.append(new_npc)
            self.save_npcs()
            self.show_npc_manager()
            self.sound_system.play_sound("click")
    
    def view_npc(self):
        selected = self.npc_listbox.curselection()
        if not selected:
            return
        
        npc_index = selected[0]
        self.current_npc = self.npcs[npc_index]
        self.show_npc_sheet()
    
    def edit_npc(self):
        selected = self.npc_listbox.curselection()
        if not selected:
            return
        
        npc_index = selected[0]
        self.current_npc = self.npcs[npc_index]
        self.show_npc_editor()
    
    def delete_npc(self):
        selected = self.npc_listbox.curselection()
        if not selected:
            return
        
        npc_index = selected[0]
        npc_name = self.npcs[npc_index].name
        
        if messagebox.askyesno("Confirmar", f"Excluir {npc_name} permanentemente?"):
            del self.npcs[npc_index]
            self.save_npcs()
            self.show_npc_manager()
            self.sound_system.play_sound("click")
    
    def show_npc_sheet(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        if not self.current_npc:
            return
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, 
                         text=f"NPC: {self.current_npc.name}", 
                         font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        back_btn = ttk.Button(btn_frame, text="Voltar", 
                             command=self.show_npc_manager, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        edit_btn = ttk.Button(btn_frame, text="Editar", 
                             command=self.show_npc_editor, style="TButton")
        edit_btn.pack(side="left", padx=5)
        
        # Informações do NPC
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Imagem
        img_frame = ttk.LabelFrame(info_frame, text="Imagem")
        img_frame.pack(fill="x", pady=5)
        
        img_path = self.current_npc.image_path
        img = self.image_manager.get_image(img_path, (150, 200)) if img_path else None
        
        if img:
            img_label = ttk.Label(img_frame, image=img)
            img_label.image = img
            img_label.pack(padx=10, pady=10)
        else:
            ttk.Label(img_frame, text="Sem imagem", font=BODY_FONT).pack(padx=10, pady=10)
        
        # Dados
        data_frame = ttk.Frame(info_frame)
        data_frame.pack(fill="x", pady=10)
        
        fields = [
            ("Raça:", self.current_npc.race),
            ("Ocupação:", self.current_npc.occupation),
            ("Disposição:", self.current_npc.disposition),
            ("Segredo:", self.current_npc.secret),
            ("Missão oferecida:", self.current_npc.quest_offer)
        ]
        
        for label, value in fields:
            frame = ttk.Frame(data_frame)
            frame.pack(fill="x", pady=3)
            
            ttk.Label(frame, text=label, width=15, anchor="w").pack(side="left")
            ttk.Label(frame, text=value, font=BODY_FONT).pack(side="left")
    
    def show_npc_editor(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        if not self.current_npc:
            return
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, 
                         text=f"Editando NPC: {self.current_npc.name}", 
                         font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        save_btn = ttk.Button(btn_frame, text="Salvar", 
                             command=self.save_npc, style="TButton")
        save_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Cancelar", 
                             command=self.show_npc_sheet, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        # Formulário
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Campos
        fields = [
            ("Nome:", "name", self.current_npc.name),
            ("Raça:", "race", self.current_npc.race),
            ("Ocupação:", "occupation", self.current_npc.occupation),
            ("Disposição:", "disposition", self.current_npc.disposition),
            ("Segredo:", "secret", self.current_npc.secret),
            ("Missão oferecida:", "quest_offer", self.current_npc.quest_offer)
        ]
        
        self.npc_vars = {}
        
        for label, key, value in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill="x", pady=5)
            
            ttk.Label(frame, text=label, width=15).pack(side="left")
            var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=var, font=BODY_FONT)
            entry.pack(fill="x", expand=True)
            self.npc_vars[key] = var
        
        # Imagem
        img_frame = ttk.Frame(form_frame)
        img_frame.pack(fill="x", pady=10)
        
        ttk.Label(img_frame, text="Imagem:").pack(side="left", padx=(0, 10))
        self.npc_img_var = tk.StringVar(value=self.current_npc.image_path)
        img_btn = ttk.Button(img_frame, text="Selecionar...", 
                            command=self.select_npc_image, style="TButton")
        img_btn.pack(side="left")
    
    def select_npc_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.npc_img_var.set(file_path)
    
    def save_npc(self):
        try:
            self.current_npc.name = self.npc_vars["name"].get()
            self.current_npc.race = self.npc_vars["race"].get()
            self.current_npc.occupation = self.npc_vars["occupation"].get()
            self.current_npc.disposition = self.npc_vars["disposition"].get()
            self.current_npc.secret = self.npc_vars["secret"].get()
            self.current_npc.quest_offer = self.npc_vars["quest_offer"].get()
            self.current_npc.image_path = self.npc_img_var.get()
            
            self.save_npcs()
            self.sound_system.play_sound("click")
            self.show_npc_sheet()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar NPC: {str(e)}")
    
    def show_item_manager(self):
        self.clear_content()
        self.sound_system.play_sound("click")

        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        header = ttk.Label(main_frame, text="Inventário e Itens", font=TITLE_FONT)
        header.pack(pady=10)

        # Lista de itens
        list_frame = ttk.LabelFrame(main_frame, text="Itens")
        list_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.item_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            bg="#1a1a2e", 
            fg=MEDIEVAL_GOLD, 
            font=BODY_FONT,
            selectbackground=CYBER_PURPLE,
            selectforeground=LIGHT_TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            height=10
        )
        self.item_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.item_listbox.yview)
        
        for item in self.items:
            self.item_listbox.insert(tk.END, f"{item.name} ({item.item_type})")
        
        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)
        
        new_btn = ttk.Button(action_frame, text="Novo Item", 
                            command=self.create_new_item, style="TButton")
        new_btn.pack(side="left", padx=5)
        
        view_btn = ttk.Button(action_frame, text="Visualizar", 
                             command=self.view_item, style="TButton")
        view_btn.pack(side="left", padx=5)
        
        edit_btn = ttk.Button(action_frame, text="Editar", 
                             command=self.edit_item, style="TButton")
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ttk.Button(action_frame, text="Excluir", 
                               command=self.delete_item, style="TButton")
        delete_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(action_frame, text="Voltar", 
                             command=self.create_main_menu, style="TButton")
        back_btn.pack(side="right", padx=5)
    
    def create_new_item(self):
        name = simpledialog.askstring("Novo Item", "Nome do item:")
        if name:
            new_item = Item(name)
            self.items.append(new_item)
            self.save_items()
            self.show_item_manager()
            self.sound_system.play_sound("click")
    
    def view_item(self):
        selected = self.item_listbox.curselection()
        if not selected:
            return
        
        item_index = selected[0]
        self.current_item = self.items[item_index]
        self.show_item_sheet()
    
    def edit_item(self):
        selected = self.item_listbox.curselection()
        if not selected:
            return
        
        item_index = selected[0]
        self.current_item = self.items[item_index]
        self.show_item_editor()
    
    def delete_item(self):
        selected = self.item_listbox.curselection()
        if not selected:
            return
        
        item_index = selected[0]
        item_name = self.items[item_index].name
        
        if messagebox.askyesno("Confirmar", f"Excluir {item_name} permanentemente?"):
            del self.items[item_index]
            self.save_items()
            self.show_item_manager()
            self.sound_system.play_sound("click")
    
    def show_item_sheet(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        if not self.current_item:
            return
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, 
                         text=f"Item: {self.current_item.name}", 
                         font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        back_btn = ttk.Button(btn_frame, text="Voltar", 
                             command=self.show_item_manager, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        edit_btn = ttk.Button(btn_frame, text="Editar", 
                             command=self.show_item_editor, style="TButton")
        edit_btn.pack(side="left", padx=5)
        
        # Informações do item
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Imagem
        img_frame = ttk.LabelFrame(info_frame, text="Imagem")
        img_frame.pack(fill="x", pady=5)
        
        img_path = self.current_item.image_path
        img = self.image_manager.get_image(img_path, (150, 150)) if img_path else None
        
        if img:
            img_label = ttk.Label(img_frame, image=img)
            img_label.image = img
            img_label.pack(padx=10, pady=10)
        else:
            ttk.Label(img_frame, text="Sem imagem", font=BODY_FONT).pack(padx=10, pady=10)
        
        # Dados
        data_frame = ttk.Frame(info_frame)
        data_frame.pack(fill="x", pady=10)
        
        fields = [
            ("Tipo:", self.current_item.item_type),
            ("Peso:", self.current_item.weight),
            ("Valor:", self.current_item.value),
            ("Mágico:", "Sim" if self.current_item.magical else "Não"),
            ("Equipável:", "Sim" if self.current_item.equippable else "Não")
        ]
        
        for label, value in fields:
            frame = ttk.Frame(data_frame)
            frame.pack(fill="x", pady=3)
            
            ttk.Label(frame, text=label, width=10, anchor="w").pack(side="left")
            ttk.Label(frame, text=value, font=BODY_FONT).pack(side="left")
        
        # Descrição
        desc_frame = ttk.LabelFrame(info_frame, text="Descrição")
        desc_frame.pack(fill="x", pady=10)
        
        desc_text = scrolledtext.ScrolledText(desc_frame, height=5, font=BODY_FONT)
        desc_text.insert("1.0", self.current_item.description)
        desc_text.configure(state="disabled")
        desc_text.pack(fill="x", padx=5, pady=5)
    
    def show_item_editor(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        if not self.current_item:
            return
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, 
                         text=f"Editando Item: {self.current_item.name}", 
                         font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        save_btn = ttk.Button(btn_frame, text="Salvar", 
                             command=self.save_item, style="TButton")
        save_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Cancelar", 
                             command=self.show_item_sheet, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        # Formulário
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Campos
        fields = [
            ("Nome:", "name", self.current_item.name),
            ("Tipo:", "type", self.current_item.item_type),
            ("Peso:", "weight", self.current_item.weight),
            ("Valor:", "value", self.current_item.value),
        ]
        
        self.item_vars = {}
        
        for label, key, value in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill="x", pady=5)
            
            ttk.Label(frame, text=label, width=10).pack(side="left")
            var = tk.StringVar(value=value)
            entry = ttk.Entry(frame, textvariable=var, font=BODY_FONT)
            entry.pack(fill="x", expand=True)
            self.item_vars[key] = var
        
        # Flags
        flags_frame = ttk.Frame(form_frame)
        flags_frame.pack(fill="x", pady=10)
        
        self.item_magical_var = tk.BooleanVar(value=self.current_item.magical)
        magical_cb = ttk.Checkbutton(flags_frame, text="Item Mágico", 
                                    variable=self.item_magical_var)
        magical_cb.pack(side="left", padx=10)
        
        self.item_equippable_var = tk.BooleanVar(value=self.current_item.equippable)
        equippable_cb = ttk.Checkbutton(flags_frame, text="Equipável", 
                                       variable=self.item_equippable_var)
        equippable_cb.pack(side="left", padx=10)
        
        # Descrição
        desc_frame = ttk.LabelFrame(form_frame, text="Descrição")
        desc_frame.pack(fill="x", pady=10)
        self.item_desc_text = scrolledtext.ScrolledText(desc_frame, height=5, font=BODY_FONT)
        self.item_desc_text.insert("1.0", self.current_item.description)
        self.item_desc_text.pack(fill="x", padx=5, pady=5)
        
        # Imagem
        img_frame = ttk.Frame(form_frame)
        img_frame.pack(fill="x", pady=10)
        
        ttk.Label(img_frame, text="Imagem:").pack(side="left", padx=(0, 10))
        self.item_img_var = tk.StringVar(value=self.current_item.image_path)
        img_btn = ttk.Button(img_frame, text="Selecionar...", 
                            command=self.select_item_image, style="TButton")
        img_btn.pack(side="left")
    
    def select_item_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.item_img_var.set(file_path)
    
    def save_item(self):
        try:
            self.current_item.name = self.item_vars["name"].get()
            self.current_item.item_type = self.item_vars["type"].get()
            self.current_item.weight = float(self.item_vars["weight"].get())
            self.current_item.value = int(self.item_vars["value"].get())
            self.current_item.magical = self.item_magical_var.get()
            self.current_item.equippable = self.item_equippable_var.get()
            self.current_item.description = self.item_desc_text.get("1.0", "end-1c")
            self.current_item.image_path = self.item_img_var.get()
            
            self.save_items()
            self.sound_system.play_sound("click")
            self.show_item_sheet()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar item: {str(e)}")
    
    def show_encounter_generator(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Gerador de Encontros", font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        gen_btn = ttk.Button(btn_frame, text="Gerar Encontro", 
                            command=self.generate_new_encounter, style="TButton")
        gen_btn.pack(side="left", padx=5)
        
        save_btn = ttk.Button(btn_frame, text="Salvar Encontro", 
                             command=self.save_encounter, style="TButton")
        save_btn.pack(side="left", padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Voltar", 
                             command=self.create_main_menu, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        # Configuração
        config_frame = ttk.LabelFrame(main_frame, text="Configurações")
        config_frame.pack(fill="x", pady=10)
        
        level_frame = ttk.Frame(config_frame)
        level_frame.pack(fill="x", pady=5)
        
        ttk.Label(level_frame, text="Nível do Grupo:", width=15).pack(side="left")
        self.level_var = tk.IntVar(value=5)
        level_spin = ttk.Spinbox(level_frame, from_=1, to=20, textvariable=self.level_var, width=5)
        level_spin.pack(side="left")
        
        # Resultado
        result_frame = ttk.LabelFrame(main_frame, text="Encontro Gerado")
        result_frame.pack(fill="both", expand=True, pady=10)
        
        self.encounter_text = scrolledtext.ScrolledText(
            result_frame, width=80, height=20, font=BODY_FONT
        )
        self.encounter_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.encounter_text.configure(state="disabled")
        
        # Gerar primeiro encontro
        self.generate_new_encounter()
    
    def generate_new_encounter(self):
        level = self.level_var.get()
        encounter = Generator.generate_encounter(level)
        
        text = f"ENCONTRO: {encounter['name']}\n"
        text += f"Dificuldade: {encounter['difficulty']} | Ambiente: {encounter['environment']}\n"
        text += f"Desafio: {encounter['challenge']}\n\n"
        text += "MONSTROS:\n"
        
        for i, monster in enumerate(encounter['monsters'], 1):
            text += f"\n{i}. {monster['type']}\n"
            text += f"  PV: {monster['hp']} | CA: {monster['ac']}\n"
            text += f"  Dano: {monster['damage']} | Especial: {monster['special']}\n"
        
        self.current_encounter = encounter
        self.encounter_text.configure(state="normal")
        self.encounter_text.delete("1.0", "end")
        self.encounter_text.insert("1.0", text)
        self.encounter_text.configure(state="disabled")
        self.sound_system.play_sound("combat")
    
    def save_encounter(self):
        if not self.current_encounter:
            return
        
        # Salvar em arquivo de encontros
        with open(ENCOUNTERS_FILE, 'a') as f:
            f.write(json.dumps(self.current_encounter) + '\n')
        
        messagebox.showinfo("Sucesso", "Encontro salvo com sucesso!")
        self.sound_system.play_sound("click")
    
    def show_master_panel(self):
        self.clear_content()
        self.sound_system.play_sound("click")
        
        # Frame principal
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Painel do Mestre", font=TITLE_FONT)
        title.pack(side="left")
        
        # Botões de ação
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        back_btn = ttk.Button(btn_frame, text="Voltar", 
                             command=self.create_main_menu, style="TButton")
        back_btn.pack(side="left", padx=5)
        
        # Abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=10)
        
        # Aba de controle
        control_tab = ttk.Frame(notebook)
        notebook.add(control_tab, text="Controle de Sessão")
        
        # Aba de ferramentas
        tools_tab = ttk.Frame(notebook)
        notebook.add(tools_tab, text="Ferramentas Rápidas")
        
        # Aba de anotações
        notes_tab = ttk.Frame(notebook)
        notebook.add(notes_tab, text="Anotações")
        
        # Preencher aba de controle
        self.setup_control_tab(control_tab)
        
        # Preencher aba de ferramentas
        self.setup_tools_tab(tools_tab)
        
        # Preencher aba de anotações
        self.setup_notes_tab(notes_tab)
    
    def setup_control_tab(self, tab):
        # Grupo
        party_frame = ttk.LabelFrame(tab, text="Grupo")
        party_frame.pack(fill="x", pady=10, padx=10)
        
        # Membros do grupo
        for member in self.party.members:
            char = next((c for c in self.characters if c.name == member), None)
            if char:
                char_frame = ttk.Frame(party_frame)
                char_frame.pack(fill="x", pady=5, padx=5)
                
                ttk.Label(char_frame, text=f"{char.name}:", width=20, anchor="w").pack(side="left")
                
                # Vida
                hp_frame = ttk.Frame(char_frame)
                hp_frame.pack(side="left", padx=5)
                ttk.Label(hp_frame, text="Vida:").pack(side="left")
                hp_var = tk.StringVar(value=char.hp[0])
                hp_entry = ttk.Entry(hp_frame, textvariable=hp_var, width=5)
                hp_entry.pack(side="left")
                
                # Mana
                mana_frame = ttk.Frame(char_frame)
                mana_frame.pack(side="left", padx=5)
                ttk.Label(mana_frame, text="Mana:").pack(side="left")
                mana_var = tk.StringVar(value=char.mana[0])
                mana_entry = ttk.Entry(mana_frame, textvariable=mana_var, width=5)
                mana_entry.pack(side="left")
                
                # Sanidade
                sanity_frame = ttk.Frame(char_frame)
                sanity_frame.pack(side="left", padx=5)
                ttk.Label(sanity_frame, text="Sanidade:").pack(side="left")
                sanity_var = tk.StringVar(value=char.sanity[0])
                sanity_entry = ttk.Entry(sanity_frame, textvariable=sanity_var, width=5)
                sanity_entry.pack(side="left")
        
        # Botão para atualizar status
        update_btn = ttk.Button(party_frame, text="Atualizar Status", 
                               command=self.update_character_status, style="TButton")
        update_btn.pack(pady=10)
        
        # Controles de sessão
        session_frame = ttk.LabelFrame(tab, text="Controles da Sessão")
        session_frame.pack(fill="x", pady=10, padx=10)
        
        # Botões
        btn_frame = ttk.Frame(session_frame)
        btn_frame.pack(fill="x", pady=10)
        
        combat_btn = ttk.Button(btn_frame, text="Iniciar Combate", style="TButton",
                               command=self.start_combat)
        combat_btn.pack(side="left", padx=5)
        
        dice_btn = ttk.Button(btn_frame, text="Rolagem de Dados", style="TButton",
                             command=self.roll_dice)
        dice_btn.pack(side="left", padx=5)
        
        save_btn = ttk.Button(btn_frame, text="Salvar Estado", style="TButton",
                             command=self.save_game_state)
        save_btn.pack(side="left", padx=5)
    
    def update_character_status(self):
        for member in self.party.members:
            char = next((c for c in self.characters if c.name == member), None)
            if char:
                try:
                    # Atualizar HP
                    new_hp = int(self.char_hp_vars[char.name].get())
                    char.hp[0] = max(0, min(char.hp[1], new_hp))
                    
                    # Atualizar Mana
                    new_mana = int(self.char_mana_vars[char.name].get())
                    char.mana[0] = max(0, min(char.mana[1], new_mana))
                    
                    # Atualizar Sanidade
                    new_sanity = int(self.char_sanity_vars[char.name].get())
                    char.sanity[0] = max(0, min(100, new_sanity))
                except ValueError:
                    pass
        
        self.save_characters()
        messagebox.showinfo("Sucesso", "Status atualizados e salvos!")
        self.sound_system.play_sound("click")
    
    def start_combat(self):
        # Implementar uma interface de combate simples
        messagebox.showinfo("Combate", "Combate iniciado! Use o gerador de encontros para configurar.")
        self.sound_system.play_sound("combat")
    
    def roll_dice(self):
        # Implementar rolagem de dados
        dice = simpledialog.askstring("Rolagem de Dados", "Digite a expressão (ex: 2d6+1):")
        if dice:
            try:
                # Implementar parser de dados
                import re
                total = 0
                parts = re.split(r'(\d+d\d+|\+|\-|\d+)', dice)
                parts = [p.strip() for p in parts if p.strip()]
                
                # Processar cada parte
                for part in parts:
                    if part in ['+', '-']:
                        op = part
                    elif 'd' in part:
                        num, sides = part.split('d')
                        num = int(num) if num else 1
                        sides = int(sides)
                        rolls = [random.randint(1, sides) for _ in range(num)]
                        total += sum(rolls) if op == '+' else -sum(rolls)
                    else:
                        value = int(part)
                        total += value if op == '+' else -value
                
                messagebox.showinfo("Resultado", f"Rolagem: {dice}\nResultado: {total}")
            except:
                messagebox.showerror("Erro", "Formato inválido. Use algo como '2d6+1'.")
    
    def save_game_state(self):
        self.save_characters()
        self.save_party()
        self.save_quests()
        self.save_npcs()
        self.save_items()
        messagebox.showinfo("Sucesso", "Estado do jogo salvo!")
        self.sound_system.play_sound("click")
    
    def setup_tools_tab(self, tab):
        # Geradores rápidos
        gen_frame = ttk.LabelFrame(tab, text="Geradores Rápidos")
        gen_frame.pack(fill="x", pady=10, padx=10)
        
        # Botões
        btn_frame = ttk.Frame(gen_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Gerar NPC", command=self.generate_npc, style="TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Gerar Item", command=self.generate_item, style="TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Gerar Local", style="TButton").pack(side="left", padx=5)
        
        # Resultado
        result_frame = ttk.Frame(gen_frame)
        result_frame.pack(fill="x", pady=10)
        
        self.tool_result = scrolledtext.ScrolledText(result_frame, height=10, font=BODY_FONT)
        self.tool_result.pack(fill="x", padx=5, pady=5)
        self.tool_result.configure(state="disabled")
    
    def generate_npc(self):
        npc = Generator.generate_npc()
        text = f"NOME: {npc.name}\n"
        text += f"RAÇA: {npc.race}\n"
        text += f"OCUPAÇÃO: {npc.occupation}\n"
        text += f"DISPOSIÇÃO: {npc.disposition}\n"
        text += f"SEGREDO: {npc.secret}\n"
        text += f"OFERECE MISSÃO: {npc.quest_offer}\n"
        
        self.tool_result.configure(state="normal")
        self.tool_result.delete("1.0", "end")
        self.tool_result.insert("1.0", text)
        self.tool_result.configure(state="disabled")
        self.sound_system.play_sound("click")
    
    def generate_item(self):
        item = Generator.generate_item()
        text = f"NOME: {item.name}\n"
        text += f"TIPO: {item.item_type}\n"
        text += f"DESCRIÇÃO: {item.description}\n"
        text += f"PESO: {item.weight} | VALOR: {item.value}\n"
        text += f"MÁGICO: {'Sim' if item.magical else 'Não'} | EQUIPÁVEL: {'Sim' if item.equippable else 'Não'}\n"
        
        self.tool_result.configure(state="normal")
        self.tool_result.delete("1.0", "end")
        self.tool_result.insert("1.0", text)
        self.tool_result.configure(state="disabled")
        self.sound_system.play_sound("click")
    
    def setup_notes_tab(self, tab):
        # Anotações
        notes_frame = ttk.Frame(tab)
        notes_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.notes_text = scrolledtext.ScrolledText(notes_frame, font=BODY_FONT)
        self.notes_text.pack(fill="both", expand=True)
        
        # Carregar anotações existentes
        if os.path.exists(os.path.join(DATA_DIR, "notes.txt")):
            with open(os.path.join(DATA_DIR, "notes.txt"), 'r') as f:
                self.notes_text.insert("1.0", f.read())
        
        # Botão de salvar
        save_btn = ttk.Button(notes_frame, text="Salvar Anotações", 
                             command=self.save_notes, style="TButton")
        save_btn.pack(side="bottom", pady=10)
    
    def save_notes(self):
        notes = self.notes_text.get("1.0", "end-1c")
        with open(os.path.join(DATA_DIR, "notes.txt"), 'w') as f:
            f.write(notes)
        messagebox.showinfo("Sucesso", "Anotações salvas!")
        self.sound_system.play_sound("click")

if __name__ == "__main__":
    root = tk.Tk()
    app = CyberMedievalApp(root)
    root.mainloop()