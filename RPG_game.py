import pygame
import sys
import random
import math


# Inisialisasi Pygame
pygame.init()
pygame.font.init()


# Konstanta Dimensi Screen & Map
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
MAP_WIDTH = 2000
MAP_HEIGHT = 1600


# ==================== PALET WARNA IMUT & COZY (PASTEL) ====================
COLOR_BG = (245, 238, 248)       # Ungu pastel sangat muda (soft aesthetic)
COLOR_TEXT = (92, 69, 112)        # Ungu tua pastel untuk teks kontras
COLOR_UI_BG = (255, 255, 255, 230)# Putih bersih transparan soft
COLOR_GOLD = (255, 184, 76)       # Oranye/Kuning madu pastel hangat
COLOR_ACTIVE = (139, 212, 169)    # Hijau mint imut
COLOR_HEART = (255, 143, 177)     # Pink stroberi manis
COLOR_BORDER = (220, 201, 235)    # Batasan ungu muda lembut


# Setup Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ucup's Cozy Fantasy Odyssey v5.0 - Family & Secret Ending Edition")
clock = pygame.time.Clock()


# Menggunakan font bawaan sistem yang membulat atau terlihat kasual
font_main = pygame.font.SysFont("Arial", 16, bold=True)
font_title = pygame.font.SysFont("Arial", 28, bold=True)
font_sub = pygame.font.SysFont("Arial", 20, bold=True)


# --- GAME STATES ---
START_SCREEN = 0
CHAR_SELECT = 1
PLAYING = 2
SECRET_ENDING_SCREEN = 3 # State baru untuk Secret Ending
game_state = START_SCREEN


# --- DATA KARAKTER YANG BISA DIPILIH ---
CHARACTERS = [
    {
        "class": "Baby Mage",
        "emoji": "🧙‍♂️",
        "desc": "Penyihir cilik imut. Bonus +50 Maks Mana.",
        "color": (163, 137, 212), # Ungu pastel lavender
        "bonus_stats": {"Mana": 150.0, "Gold": 400}
    },
    {
        "class": "Chibi Knight",
        "emoji": "⚔️",
        "desc": "Ksatria mungil pemberani. Bonus +300 Gold.",
        "color": (143, 191, 224), # Biru langit pastel
        "bonus_stats": {"Mana": 100.0, "Gold": 700}
    }
]
selected_char_idx = 0


# --- DATA MASTER ITEM ---
ITEM_DATABASE = {
    "Ramuan Mana": {"effect": {"Mana": 40}, "desc": "Memulihkan +40 Mana ✨"},
    "Permen Stroberi": {"effect": {"Happiness": 30}, "desc": "Permen manis manis manis +30 Hebat! 🍬"},
    "Roti Lemba": {"effect": {"Meal": 35, "Sleep": 10}, "desc": "Mengenyangkan & bikin rileks 🍞"},
    "Cincin Berlian": {"effect": {"Happiness": 50}, "desc": "Cincin lamaran berkilau penuh cinta 💍"},
}


# --- DATA HUBUNGAN (NPC RELATIONSHIP) ---
npc_relationships = {
    "Eldrin (Elven Chief)": {"level": 0, "status": "Stranger", "married": False},
    "Archmage Vael": {"level": 0, "status": "Stranger", "married": False},
    "Lyra (Mermaid Princess)": {"level": 0, "status": "Stranger", "married": False}
}


# Menandakan apakah player sudah memiliki keluarga
has_family = False
spouse_name = ""


def get_relation_status(level, is_married):
    if is_married: return "Pasangan Hidup 💍"
    if level >= 100: return "Saling Mencintai ❤️"
    if level >= 80: return "Bestie-ku ✨"
    if level >= 50: return "Teman Dekat"
    if level >= 20: return "Kenal Baik"
    return "Orang Asing"


# --- KLAS KAMERA ---
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height


    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)


    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)


    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, max(-(self.width - SCREEN_WIDTH), x))
        y = min(0, max(-(self.height - SCREEN_HEIGHT), y))
        self.camera = pygame.Rect(x, y, self.width, self.height)


# --- KLAS ENTITAS PEMAIN ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 40, 45)
        self.speed = 5
        self.char_class = "Baby Mage"
        self.color = (163, 137, 212)
       
        self.stats = {
            "Meal": 100.0,
            "Sleep": 100.0,
            "Happiness": 100.0,
            "Mana": 100.0,
            "Gold": 500,
        }
        self.max_mana = 100.0
        self.inventory = ["Permen Stroberi", "Roti Lemba"]
        self.score = 0


    def assign_profile(self, char_data):
        self.char_class = char_data["class"]
        self.color = char_data["color"]
        self.stats["Gold"] = char_data["bonus_stats"]["Gold"]
        self.stats["Mana"] = char_data["bonus_stats"]["Mana"]
        if "Mage" in self.char_class:
            self.max_mana = 150.0


    def draw(self, surf, cam_offset):
        pos = self.rect.move(cam_offset)
        pygame.draw.circle(surf, (247, 217, 193), (pos.x + 20, pos.y + 12), 12)
        pygame.draw.circle(surf, (255, 143, 177), (pos.x + 12, pos.y + 15), 3)  
        pygame.draw.circle(surf, (255, 143, 177), (pos.x + 28, pos.y + 15), 3)  
        pygame.draw.rect(surf, self.color, (pos.x + 8, pos.y + 22, 24, 22), border_radius=8)
        pygame.draw.polygon(surf, (110, 80, 150), [(pos.x + 8, pos.y + 6), (pos.x + 20, pos.y - 6), (pos.x + 32, pos.y + 6)])


        # Jika sudah menikah, pasang emoji hati di atas kepala player
        if has_family:
            heart_surf = font_main.render("❤️", True, (0,0,0))
            surf.blit(heart_surf, (pos.x + 12, pos.y - 25))


    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))


    def update_decay(self):
        # Jika sudah membangun keluarga, penurunan stats sedikit lebih ringan karena diurus pasangan!
        decay_modifier = 0.7 if has_family else 1.0
        self.stats["Meal"] = max(0.0, self.stats["Meal"] - 0.012 * decay_modifier)
        self.stats["Sleep"] = max(0.0, self.stats["Sleep"] - 0.008 * decay_modifier)
        self.stats["Happiness"] = max(0.0, self.stats["Happiness"] - 0.008 * decay_modifier)
        self.stats["Mana"] = max(0.0, self.stats["Mana"] - 0.005 * decay_modifier)


# --- KLAS ZONA AKTIVITAS ---
class ActivityZone(pygame.sprite.Sprite):
    def __init__(self, name, npc_name, x, y, color, activities):
        super().__init__()
        self.name = name
        self.npc_name = npc_name
        self.image = pygame.Surface((180, 180), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color + (50,), (90, 90), 90)
        pygame.draw.circle(self.image, color, (90, 90), 90, 4)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.activities = activities


# --- INISIALISASI GAME ---
player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
camera = Camera(MAP_WIDTH, MAP_HEIGHT)


zones = pygame.sprite.Group()
zones.add(ActivityZone("Elven Patch", "Eldrin (Elven Chief)", 200, 200, (168, 230, 207), [
    {"name": "Beli Roti Lemba", "cost": 30, "duration": 40, "effects": {"Gold": 0}, "get_item": "Roti Lemba"},
    {"name": "Piknik bareng Eldrin", "cost": 0, "duration": 100, "effects": {"Happiness": 20}, "relation_gain": 15, "target_npc": "Eldrin (Elven Chief)"},
    {"name": "Beli Cincin Berlian", "cost": 500, "duration": 50, "effects": {"Gold": 0}, "get_item": "Cincin Berlian"} # Toko Cincin Nikah
]))
zones.add(ActivityZone("Cosy Magic Tower", "Archmage Vael", 1400, 150, (179, 211, 234), [
    {"name": "Beli Ramuan Mana", "cost": 50, "duration": 30, "effects": {"Gold": 0}, "get_item": "Ramuan Mana"},
    {"name": "Mendengar Dongeng Sihir", "cost": 0, "duration": 80, "effects": {"Mana": 15}, "relation_gain": 15, "target_npc": "Archmage Vael"}
]))
zones.add(ActivityZone("Siren Lagoon", "Lyra (Mermaid Princess)", 200, 1200, (255, 211, 182), [
    {"name": "Mencari Permen Stroberi", "cost": 10, "duration": 70, "effects": {"Happiness": 5}, "get_item": "Permen Stroberi"},
    {"name": "Bernyanyi bareng Lyra", "cost": 0, "duration": 90, "effects": {"Happiness": 25}, "relation_gain": 20, "target_npc": "Lyra (Mermaid Princess)"}
]))


# Zona baru: Dungeon tempat kerja mengumpulkan Gold
zones.add(ActivityZone("Mystic Dungeon", "Dungeon Guard", 1400, 1100, (240, 178, 178), [
    {"name": "Grinding Monster Cilik", "cost": 0, "duration": 120, "effects": {"Mana": -30, "Gold": 350}},
    {"name": "Berpatroli Jaga Dungeon", "cost": 0, "duration": 90, "effects": {"Meal": -20, "Gold": 150}}
]))


# State Kendali Aktivitas
current_activity = None
activity_timer = 0
activity_max_duration = 0
fast_forward = False
active_zone_near = None


# Elemen Dekorasi Latar Belakang
env_objects = []
for _ in range(90):
    env_objects.append({
        "pos": (random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)),
        "char": random.choice(["🌸", "☁️", "🌱"]),
    })


# --- UTILITY BUTTON UI GAYA IMUT ---
def draw_button(surf, text, rect, is_hovered, base_color=(255, 174, 184), hover_color=(255, 143, 177)):
    color = hover_color if is_hovered else base_color
    pygame.draw.rect(surf, color, rect, border_radius=12)
    pygame.draw.rect(surf, (255, 255, 255), rect, 2, border_radius=12)
    txt_surf = font_main.render(text, True, (255, 255, 255))
    surf.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width())//2, rect.y + (rect.height - txt_surf.get_height())//2))


# ==================== MAIN GAME LOOP ====================
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
   
    # ------------------ EVENT HANDLING ------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
           
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # === START SCREEN ===
            if game_state == START_SCREEN:
                start_btn = pygame.Rect(SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 40, 240, 50)
                if start_btn.collidepoint(mouse_pos):
                    game_state = CHAR_SELECT
           
            # === CHAR SELECT ===
            elif game_state == CHAR_SELECT:
                for idx in range(len(CHARACTERS)):
                    box_rect = pygame.Rect(150 + idx * 400, 200, 300, 300)
                    if box_rect.collidepoint(mouse_pos):
                        selected_char_idx = idx
                       
                confirm_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 560, 200, 50)
                if confirm_btn.collidepoint(mouse_pos):
                    player.assign_profile(CHARACTERS[selected_char_idx])
                    game_state = PLAYING
                   
            # === SECRET ENDING SCREEN ===
            elif game_state == SECRET_ENDING_SCREEN:
                restart_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                if restart_btn.collidepoint(mouse_pos):
                    # Reset Game
                    player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
                    has_family = False
                    spouse_name = ""
                    for npc in npc_relationships:
                        npc_relationships[npc] = {"level": 0, "status": "Stranger", "married": False}
                    game_state = START_SCREEN


            # === PLAYING ===
            elif game_state == PLAYING:
                # 1. Klik Tombol Aktivitas Zona
                if current_activity is None and active_zone_near:
                    # Cek aktivitas biasa
                    for idx, act in enumerate(active_zone_near.activities):
                        btn_rect = pygame.Rect(SCREEN_WIDTH - 320, 220 + idx * 60, 290, 45)
                        if btn_rect.collidepoint(mouse_pos):
                            if player.stats["Gold"] >= act["cost"]:
                                player.stats["Gold"] -= act["cost"]
                                current_activity = act
                                activity_timer = 0
                                activity_max_duration = act["duration"]
                                fast_forward = False


                    # Tombol Spesial: LAMARAN / MENIKAH (Muncul jika status hubungan mumpuni & punya Cincin)
                    npc_name = active_zone_near.npc_name
                    if npc_name in npc_relationships and npc_relationships[npc_name]["level"] >= 100 and "Cincin Berlian" in player.inventory and not has_family:
                        propose_btn_rect = pygame.Rect(SCREEN_WIDTH - 320, 220 + len(active_zone_near.activities) * 60, 290, 45)
                        if propose_btn_rect.collidepoint(mouse_pos):
                            has_family = True
                            spouse_name = npc_name
                            npc_relationships[npc_name]["married"] = True
                            npc_relationships[npc_name]["status"] = get_relation_status(100, True)
                            player.inventory.remove("Cincin Berlian")
                            player.score += 500
                           
                            # Cek Syarat Secret Ending saat Menikah:
                            # Semua stat utama > 80 dan Gold sisa melimpah (> 1000)
                            if (player.stats["Meal"] >= 80 and player.stats["Sleep"] >= 80 and
                                player.stats["Happiness"] >= 80 and player.stats["Gold"] >= 1000):
                                game_state = SECRET_ENDING_SCREEN
                               
                # 2. Klik Gunakan Item
                if current_activity is None:
                    for idx, item_name in enumerate(player.inventory[:4]):
                        use_btn_rect = pygame.Rect(260, (SCREEN_HEIGHT - 130) + (idx * 26), 65, 22)
                        if use_btn_rect.collidepoint(mouse_pos):
                            item_data = ITEM_DATABASE[item_name]
                            for stat, bonus in item_data["effect"].items():
                                max_cap = player.max_mana if stat == "Mana" else 100.0
                                player.stats[stat] = min(max_cap, player.stats[stat] + bonus)
                            player.inventory.remove(item_name)
                            player.score += 5
                            break
                           
                # 3. Klik Fast Forward
                if current_activity and not fast_forward:
                    ff_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 50, 160, 40)
                    if ff_rect.collidepoint(mouse_pos):
                        fast_forward = True


    # ------------------ LOGIKA KENDALI PERGERAKAN & UPDATE ------------------
    if game_state == PLAYING:
        if current_activity is None:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
           
            if dx != 0 and dy != 0:
                dx, dy = dx * 0.7071, dy * 0.7071
            player.move(dx, dy)
            player.update_decay()


        camera.update(player)


        # Cari zona paling dekat
        active_zone_near = None
        for zone in zones:
            distance = math.hypot(player.rect.centerx - zone.rect.centerx, player.rect.centery - zone.rect.centery)
            if distance < 110:
                active_zone_near = zone
                break


        # Logika Aktivitas Berjalan
        if current_activity:
            step = 5 if fast_forward else 1
            activity_timer += step
           
            # Pengurangan/Penambahan berkala untuk mode normal (Non-Fast Forward)
            if not fast_forward and "effects" in current_activity:
                for stat, val in current_activity["effects"].items():
                    if stat != "Gold": # Gold diberikan instan di akhir agar menjadi gaji/hadiah utuh
                        max_cap = player.max_mana if stat == "Mana" else 100.0
                        player.stats[stat] = max(0.0, min(max_cap, player.stats[stat] + val / current_activity["duration"]))


            # Ketika aktivitas selesai
            if activity_timer >= activity_max_duration:
                if "effects" in current_activity:
                    for stat, val in current_activity["effects"].items():
                        # Jika fast forward, tambahkan/kurangkan stat non-gold secara penuh di akhir
                        if fast_forward and stat != "Gold":
                            max_cap = player.max_mana if stat == "Mana" else 100.0
                            player.stats[stat] = max(0.0, min(max_cap, player.stats[stat] + val))
                       
                        # Terapkan efek penambahan Gold di akhir (untuk normal maupun fast-forward)
                        if stat == "Gold":
                            player.stats["Gold"] += val
               
                if "get_item" in current_activity:
                    player.inventory.append(current_activity["get_item"])
               
                if "relation_gain" in current_activity:
                    npc = current_activity["target_npc"]
                    if npc in npc_relationships:
                        npc_relationships[npc]["level"] = min(100, npc_relationships[npc]["level"] + current_activity["relation_gain"])
                        npc_relationships[npc]["status"] = get_relation_status(npc_relationships[npc]["level"], npc_relationships[npc]["married"])
               
                player.score += random.randint(15, 25)
                current_activity = None


    # ------------------ RENDER GRAFIS ------------------
    if game_state == START_SCREEN:
        screen.fill(COLOR_BG)
        title_surf = font_title.render("✨ UCUP'S COZY ODYSSEY ✨", True, COLOR_TEXT)
        sub_surf = font_sub.render("Koleksi Item, Nikah & Bangun Keluarga Chibi", True, COLOR_HEART)
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(sub_surf, (SCREEN_WIDTH//2 - sub_surf.get_width()//2, SCREEN_HEIGHT//3 + 45))
       
        start_btn = pygame.Rect(SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 40, 240, 50)
        draw_button(screen, "MASUK DUNIA IMUT", start_btn, start_btn.collidepoint(mouse_pos))


    elif game_state == CHAR_SELECT:
        screen.fill(COLOR_BG)
        header = font_title.render("PILIH HERO CILIKMU", True, COLOR_TEXT)
        screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, 70))
       
        for idx, char in enumerate(CHARACTERS):
            box_rect = pygame.Rect(150 + idx * 400, 180, 300, 320)
            is_active = (selected_char_idx == idx)
            bg_color = (255, 255, 255) if is_active else (238, 226, 242)
            pygame.draw.rect(screen, bg_color, box_rect, border_radius=16)
            pygame.draw.rect(screen, COLOR_HEART if is_active else COLOR_BORDER, box_rect, 4, border_radius=16)
           
            name_s = font_sub.render(f"{char['emoji']} {char['class']}", True, COLOR_TEXT)
            screen.blit(name_s, (box_rect.x + (300 - name_s.get_width())//2, box_rect.y + 30))
            desc_s = font_main.render(char["desc"], True, COLOR_TEXT)
            screen.blit(desc_s, (box_rect.x + 20, box_rect.y + 120))
           
        confirm_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 540, 200, 50)
        draw_button(screen, "OK, KETUK SINI!", confirm_btn, confirm_btn.collidepoint(mouse_pos))


    # SCREEN SECRET ENDING BARU
    elif game_state == SECRET_ENDING_SCREEN:
        screen.fill((253, 242, 233)) # Warna emas pastel hangat khusus ending
        end_title = font_title.render("👑 SECRET ENDING UNLOCKED! 👑", True, COLOR_GOLD)
        end_sub = font_sub.render(f"The Cozy Royal Family Dynasty", True, COLOR_TEXT)
       
        story_1 = font_main.render(f"Ucup berhasil meminang {spouse_name} dengan Cincin Berlian!", True, COLOR_TEXT)
        story_2 = font_main.render("Dengan kekayaan melimpah (>1000 Gold) and hidup yang super sehat serta sejahtera,", True, COLOR_TEXT)
        story_3 = font_main.render("Keluarga kecil kalian hidup bahagia selamanya, melahirkan generasi Chibi baru yang damai. ✨", True, COLOR_TEXT)
       
        screen.blit(end_title, (SCREEN_WIDTH//2 - end_title.get_width()//2, SCREEN_HEIGHT//4))
        screen.blit(end_sub, (SCREEN_WIDTH//2 - end_sub.get_width()//2, SCREEN_HEIGHT//4 + 50))
        screen.blit(story_1, (SCREEN_WIDTH//2 - story_1.get_width()//2, SCREEN_HEIGHT//2 - 20))
        screen.blit(story_2, (SCREEN_WIDTH//2 - story_2.get_width()//2, SCREEN_HEIGHT//2 + 10))
        screen.blit(story_3, (SCREEN_WIDTH//2 - story_3.get_width()//2, SCREEN_HEIGHT//2 + 40))
       
        restart_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 150, 200, 50)
        draw_button(screen, "MAIN LAGI 🔄", restart_btn, restart_btn.collidepoint(mouse_pos), COLOR_ACTIVE, (100, 200, 140))


    elif game_state == PLAYING:
        screen.fill(COLOR_BG)
        cam_offset = camera.camera.topleft


        for obj in env_objects:
            screen.blit(font_main.render(obj["char"], True, (0,0,0)), cam_offset + pygame.math.Vector2(obj["pos"]))


        for zone in zones:
            screen.blit(zone.image, camera.apply(zone))
            lbl = font_sub.render(f"📍 {zone.name}", True, COLOR_TEXT)
            screen.blit(lbl, camera.apply_rect(pygame.Rect(zone.rect.centerx - lbl.get_width()//2, zone.rect.y - 30, 0, 0)))


        player.draw(screen, cam_offset)


        # --- BAR STATUS ATAS ---
        ui_top = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
        ui_top.fill(COLOR_UI_BG)
        screen.blit(ui_top, (0, 0))
        pygame.draw.line(screen, COLOR_BORDER, (0, 80), (SCREEN_WIDTH, 80), 2)


        stats_bars = [("Meal", "🍖", 100.0, (255, 179, 186)), ("Sleep", "💤", 100.0, (255, 255, 186)),
                      ("Happiness", "💖", 100.0, (255, 186, 210)), ("Mana", "🔮", player.max_mana, (186, 255, 201))]
       
        for i, (s_name, emoji, max_v, bar_pastel_color) in enumerate(stats_bars):
            val = player.stats[s_name]
            x_offset = 20 + (i * 180)
            screen.blit(font_main.render(f"{emoji} {s_name}", True, COLOR_TEXT), (x_offset, 14))
            pygame.draw.rect(screen, (230, 230, 230), (x_offset, 40, 150, 16), border_radius=6)
            pygame.draw.rect(screen, bar_pastel_color, (x_offset, 40, int(150 * (val / max_v)), 16), border_radius=6)


        screen.blit(font_sub.render(f"🪙 {player.stats['Gold']}", True, COLOR_GOLD), (SCREEN_WIDTH - 240, 14))
        screen.blit(font_sub.render(f"⭐ Skor: {player.score}", True, COLOR_TEXT), (SCREEN_WIDTH - 240, 42))


        # --- MENU INTERAKSI TOKO / NPC (KANAN) ---
        if active_zone_near and current_activity is None:
            panel_right = pygame.Surface((320, 440), pygame.SRCALPHA)
            panel_right.fill(COLOR_UI_BG)
            pygame.draw.rect(panel_right, COLOR_BORDER, (0, 0, 320, 440), 3, border_radius=16)
            screen.blit(panel_right, (SCREEN_WIDTH - 330, 120))


            screen.blit(font_sub.render(active_zone_near.name, True, COLOR_TEXT), (SCREEN_WIDTH - 310, 140))
            screen.blit(font_main.render(f"💬 Meet: {active_zone_near.npc_name}", True, COLOR_HEART), (SCREEN_WIDTH - 310, 170))


            # Render opsi aktivitas biasa
            for idx, act in enumerate(active_zone_near.activities):
                btn_rect = pygame.Rect(SCREEN_WIDTH - 320, 220 + idx * 60, 290, 45)
                btn_label = f"{act['name']} [{act['cost']}G]"
                draw_button(screen, btn_label, btn_rect, btn_rect.collidepoint(mouse_pos))


            # RENDER TOMBOL MARRY / BUILD FAMILY SPESIAL
            npc_name = active_zone_near.npc_name
            if npc_name in npc_relationships and npc_relationships[npc_name]["level"] >= 100 and "Cincin Berlian" in player.inventory and not has_family:
                propose_btn_rect = pygame.Rect(SCREEN_WIDTH - 320, 220 + len(active_zone_near.activities) * 60, 290, 45)
                draw_button(screen, "💍 Lamar & Bangun Keluarga", propose_btn_rect, propose_btn_rect.collidepoint(mouse_pos), COLOR_HEART, (255, 80, 130))


        # --- PANEL TAS INVENTORI ---
        panel_inv = pygame.Surface((340, 165), pygame.SRCALPHA)
        panel_inv.fill(COLOR_UI_BG)
        pygame.draw.rect(panel_inv, COLOR_BORDER, (0, 0, 340, 165), 2, border_radius=12)
        screen.blit(panel_inv, (15, SCREEN_HEIGHT - 180))
        screen.blit(font_sub.render("🎒 Kantong Tas Ucup:", True, COLOR_TEXT), (25, SCREEN_HEIGHT - 170))
       
        if not player.inventory:
            screen.blit(font_main.render("(Kosong melompong 🌟)", True, (170, 170, 170)), (25, SCREEN_HEIGHT - 130))
        else:
            for idx, item_name in enumerate(player.inventory[:4]):
                y_pos = (SCREEN_HEIGHT - 130) + (idx * 26)
                screen.blit(font_main.render(f"• {item_name}", True, COLOR_TEXT), (25, y_pos))
                use_btn = pygame.Rect(260, y_pos, 65, 22)
                is_h = use_btn.collidepoint(mouse_pos)
                draw_button(screen, "USE", use_btn, is_h, (186, 225, 255) if not is_h else (138, 199, 247))


        # --- PANEL HUBUNGAN PERSAHABATAN NPC ---
        panel_rel = pygame.Surface((300, 165), pygame.SRCALPHA)
        panel_rel.fill(COLOR_UI_BG)
        pygame.draw.rect(panel_rel, COLOR_BORDER, (0, 0, 300, 165), 2, border_radius=12)
        screen.blit(panel_rel, (370, SCREEN_HEIGHT - 180))
        screen.blit(font_sub.render("💕 Hubungan Emosional:", True, COLOR_HEART), (380, SCREEN_HEIGHT - 170))
       
        for idx, (npc_n, data) in enumerate(npc_relationships.items()):
            y_pos = (SCREEN_HEIGHT - 130) + (idx * 24)
            short_n = npc_n.split(" ")[0]
            txt = f"• {short_n}: Lv.{data['level']} [{data['status']}]"
            screen.blit(font_main.render(txt, True, COLOR_TEXT), (380, y_pos))


        # --- POPUP ANIMASI ---
        if current_activity:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))


            box = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 110, 400, 220)
            pygame.draw.rect(screen, (255, 255, 255), box, border_radius=20)
            pygame.draw.rect(screen, COLOR_HEART, box, 4, border_radius=20)


            screen.blit(font_sub.render("Sstt.. Lagi Beraktivitas 🌸", True, COLOR_TEXT), (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 80))
            desc = font_main.render(f"Aksi: {current_activity['name']}", True, COLOR_TEXT)
            screen.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, SCREEN_HEIGHT//2 - 20))


            progress = activity_timer / activity_max_duration
            pygame.draw.rect(screen, (240, 240, 240), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 15, 300, 16), border_radius=8)
            pygame.draw.rect(screen, COLOR_ACTIVE, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 15, int(300 * progress), 16), border_radius=8)


            if not fast_forward:
                ff_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 50, 160, 36)
                draw_button(screen, "⏩ Percepat Aksi", ff_rect, ff_rect.collidepoint(mouse_pos), COLOR_GOLD, (255, 160, 20))


    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()




