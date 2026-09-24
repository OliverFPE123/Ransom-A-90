import tkinter as tk
import time
import random
import math
import os
import pygame
from PIL import Image, ImageDraw, ImageTk

# ==== НАСТРОЙКИ ====
STOP_DELAY = 0.2
REACTION_TIME = 2.0
FLASH_TIME = 80
MOUSE_TOLERANCE = 3
CHECK_INTERVAL = 15
TRANSPARENT_COLOR = "black"
SCALE = 3
HD_SCALE = 2

SHAKE_AMPLITUDE = 30
SHAKE_INTERVAL = 15
SHAKE_STEP = 4
FACE_SHAKE_AMP = 8
FACE_SHAKE_INTERVAL = 50
WIN_SHAKE_INTERVAL = 30
WIN_SHAKE_STEP = 2
WIN_SHAKE_AMP = 5

SCREAM_DELAY = 1.0
DOWNLOAD_DELAY = 0.8
PROGRESS_TIME = 1.0
RANSOM_TIME = 78
CLOSE_DELAY = 2.0

SPAM_INTERVAL = 15.0
SPAM_MAX_WINDOWS = 8
SPAM_BATCH = 3
SCREAM_CHANCE = 0.3
GLITCH_FPS_MS = 80
SCREAM_NOISE_INTERVAL = 80

COIN_VALUE = 100
COIN_TARGET = 500
COIN_SPAWN_INTERVAL = 10.0
COIN_SIZE = 80
MAX_COINS = 6
CROSS_EVERY = 6

BSOD_DELAY = 1.0
SHORT_BEEP_INTERVAL = 80
BSOD_SHOW_AFTER = 3.0
GLITCH_AFTER_MUSIC = 1.0

MUSIC_PITCH = 1.5
ORIGINAL_MUSIC = "a90minwaregame.mp3"
PITCHED_MUSIC = "a90minwaregame_pitched.mp3"

SPAM_TITLES = [
    "Untitled (2)", "ERROR", "WHAT WOULD SHE THINK?",
    "MOSKNAR", "RANSOM", "SYSTEM", "NULL", "PANIC"
]


def create_pitched_music():
    if os.path.exists(PITCHED_MUSIC):
        print(f"[МУЗЫКА] {PITCHED_MUSIC} уже существует")
        return True
    if not os.path.exists(ORIGINAL_MUSIC):
        print(f"[МУЗЫКА] {ORIGINAL_MUSIC} не найден!")
        return False
    try:
        from pydub import AudioSegment
        print(f"[МУЗЫКА] Создаю {PITCHED_MUSIC} (питч {MUSIC_PITCH})...")
        sound = AudioSegment.from_mp3(ORIGINAL_MUSIC)
        pitched = sound.speedup(playback_speed=MUSIC_PITCH)
        pitched.export(PITCHED_MUSIC, format="mp3")
        print(f"[МУЗЫКА] Готово: {PITCHED_MUSIC}")
        return True
    except ImportError:
        print("[МУЗЫКА] pydub не установлен — pip install pydub")
        return False
    except Exception as e:
        print(f"[МУЗЫКА] ОШИБКА: {e}")
        return False


create_pitched_music()

print("=" * 50)
print("ПРОВЕРКА ФАЙЛОВ")
print("=" * 50)

REQUIRED_SOUNDS = [
    "a90.mp3", "a90scream.mp3", "a90screamold.mp3",
    "a90minwaregame.mp3", PITCHED_MUSIC,
    "glitch.mp3", "crucifix.mp3", "beep.mp3"
]
REQUIRED_IMAGES = [
    "a90_idle.png", "sstopsign.png", "a90screamer.png", "a_90crucifix.png"
]

for f in REQUIRED_SOUNDS + REQUIRED_IMAGES:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"[OK]    {f} ({size} байт)")
    else:
        print(f"[НЕТ]   {f} — ФАЙЛ НЕ НАЙДЕН!")

print("=" * 50)

pygame.mixer.init()
print(f"mixer: {pygame.mixer.get_init()}")
print("=" * 50)

_sounds_cache = {}
print("ЗАГРУЗКА ЗВУКОВ:")
for snd_name in REQUIRED_SOUNDS:
    if os.path.exists(snd_name):
        try:
            _sounds_cache[snd_name] = pygame.mixer.Sound(snd_name)
            print(f"[OK]    {snd_name} загружен")
        except Exception as e:
            print(f"[ОШИБКА] {snd_name}: {e}")
    else:
        print(f"[НЕТ]   {snd_name} не найден")
print("=" * 50)


root = tk.Tk()
root.title("A-90")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.configure(bg=TRANSPARENT_COLOR)
root.attributes("-transparentcolor", TRANSPARENT_COLOR)


def load_hd(name, scale=SCALE):
    img = Image.open(name).convert("RGBA")
    new_w = max(1, img.width // scale)
    new_h = max(1, img.height // scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


img_idle = load_hd("a90_idle.png")
img_stop = load_hd("sstopsign.png")
img_scream = load_hd("a90screamer.png", scale=1)
img_ransom_face = load_hd("a90_idle.png", scale=6)

_pil_scream = Image.open("a90screamer.png").convert("RGBA")
_pil_idle = Image.open("a90_idle.png").convert("RGBA")
_pil_crucifix = Image.open("a_90crucifix.png").convert("RGBA")

label = tk.Label(root, bg=TRANSPARENT_COLOR, image=img_idle, bd=0)
label.pack()

flash = tk.Toplevel(root)
flash.overrideredirect(True)
flash.attributes("-topmost", True)
flash.configure(bg="red")
flash.withdraw()

scream_win = tk.Toplevel(root)
scream_win.overrideredirect(True)
scream_win.attributes("-topmost", True)
scream_win.configure(bg="#8b0000")
scream_win.withdraw()

scream_canvas = tk.Canvas(scream_win, bg="#8b0000", highlightthickness=0)
scream_canvas.pack(fill="both", expand=True)

dl_win = tk.Toplevel(root)
dl_win.overrideredirect(True)
dl_win.attributes("-topmost", True)
dl_win.configure(bg="#8B0000")
dl_win.withdraw()

dl_canvas = tk.Canvas(dl_win, bg="#8B0000", highlightthickness=0)
dl_canvas.pack(fill="both", expand=True)

root.update_idletasks()
w = img_idle.width()
h = img_idle.height()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = (screen_w - w) // 2
y = (screen_h - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")


def build_dl_ui():
    dl_canvas.delete("all")
    cx = screen_w // 2
    cy = screen_h // 2
    dl_canvas.create_text(cx, cy - 60, text="DOWNLOADING.",
                          fill="white", font=("Arial", 28, "bold"))
    bar_w, bar_h = 600, 40
    bx = cx - bar_w // 2
    by = cy - 10
    dl_canvas.create_rectangle(bx - 3, by - 3, bx + bar_w + 3, by + bar_h + 3,
                                fill="#2b0000", outline="#ff3333", width=2)
    dl_canvas.create_rectangle(bx, by, bx, by + bar_h,
                                fill="#ff2222", outline="", tags="bar")
    for i in range(1, 12):
        sx = bx + int(bar_w * i / 12)
        dl_canvas.create_rectangle(sx, by, sx + 3, by + bar_h,
                                    fill="#2b0000", outline="")
    dl_canvas.create_text(cx, cy + 60, text="0%",
                          fill="white", font=("Arial", 18, "bold"),
                          tags="percent")


build_dl_ui()

state = {
    "running": True,
    "caught": False,
    "last_mouse": None,
    "check_id": None,
    "music_end_id": None,
    "flash_id": None,
    "stop_id": None,
    "scream_start_id": None,
    "scream_delay_id": None,
    "shake_id": None,
    "scream_noise_id": None,
    "download_id": None,
    "scream_active": False,
    "dl_active": False,
    "progress_id": None,
    "ransom_win": None,
    "ransom_timer_id": None,
    "ransom_gold_label": None,
    "ransom_face_label": None,
    "ransom_face_shake_id": None,
    "gold_zone": (0, 0, 0, 0),
    "gold_zone_id": None,
    "spam_windows": [],
    "spam_id": None,
    "spam_active": False,
    "final_scream_done": False,
    "coins": [],
    "coin_count": 0,
    "coin_target": COIN_TARGET,
    "coin_id": None,
    "coin_active": False,
    "coin_spawn_count": 0,
    "beep_id": None,
    "bsod_win": None,
    "bsod_shown": False,
    "crucifix_used": False,
    "crucifix_anim_id": None,
    "glitch_id": None,
    "crucifix_sound": _sounds_cache.get("crucifix.mp3"),
}

idle_sound = _sounds_cache.get("a90.mp3")
if idle_sound:
    idle_sound.play(loops=0)


def play_sound(name, loops=0):
    if not state["running"]:
        return
    snd = _sounds_cache.get(name)
    if snd is None:
        print(f"[ЗВУК] {name} не загружен")
        return
    try:
        snd.play(loops=loops)
        print(f"[ЗВУК] {name} играет")
    except Exception as e:
        print(f"[ЗВУК] ОШИБКА {name}: {e}")


def cleanup():
    state["running"] = False
    for key in ("check_id", "music_end_id", "flash_id", "stop_id",
                "scream_start_id", "scream_delay_id", "shake_id",
                "scream_noise_id", "download_id", "progress_id",
                "ransom_timer_id", "spam_id", "coin_id", "beep_id",
                "crucifix_anim_id", "gold_zone_id", "glitch_id",
                "ransom_face_shake_id"):
        if state.get(key):
            try:
                root.after_cancel(state[key])
            except Exception:
                pass
            state[key] = None
    pygame.mixer.stop()
    for win in (flash, scream_win, dl_win, state.get("ransom_win"),
                state.get("bsod_win")):
        try:
            if win:
                win.destroy()
        except Exception:
            pass
    for win, _ in state["spam_windows"]:
        try:
            win.destroy()
        except Exception:
            pass
    state["spam_windows"].clear()
    for win in state["coins"]:
        try:
            win.destroy()
        except Exception:
            pass
    state["coins"].clear()


# ==================== СТАРТ ====================

def show_flash():
    if not state["running"]:
        return
    flash.geometry(f"{screen_w}x{screen_h}+0+0")
    flash.deiconify()
    flash.lift()
    state["flash_id"] = root.after(FLASH_TIME, hide_flash)


def hide_flash():
    if state["running"]:
        flash.withdraw()


def show_stop():
    if state["running"]:
        label.config(image=img_stop)
        label.image = img_stop
        state["last_mouse"] = None
        state["stop_id"] = root.after(int(REACTION_TIME * 1000), survived_stop)


def survived_stop():
    if not state["running"] or state["caught"]:
        return
    cleanup()
    root.destroy()


# ==================== ПИКСЕЛЬНЫЕ ПОМЕХИ ====================

def draw_scream_noise(w, h):
    c = scream_canvas
    c.delete("all")
    c.create_rectangle(0, 0, w, h, fill="#8b0000")

    for _ in range(random.randint(400, 800)):
        px = random.randint(0, w)
        py = random.randint(0, h)
        size = random.randint(4, 14)
        color = random.choice([
            "#3a0000", "#5a0000", "#6b1010", "#7a1a1a",
            "#8b2500", "#a52a2a", "#c04000", "#d2691e",
            "#8b4513", "#654321", "#4a0e0e",
            "#ff0000", "#ff4500", "#b22222",
            "#000000", "#ffffff",
        ])
        c.create_rectangle(px, py, px + size, py + size,
                           fill=color, outline="")

    for _ in range(random.randint(10, 25)):
        y = random.randint(0, h)
        bar_h = random.randint(2, 8)
        color = random.choice(["#3a0000", "#5a0000", "#8b4513",
                                "#a52a2a", "#000000", "#ffffff"])
        c.create_rectangle(0, y, w, y + bar_h, fill=color, outline="")

    try:
        c.create_image(w // 2, h // 2, image=img_scream, anchor="center")
    except Exception:
        pass


# ==================== СКРИМЕР ====================

_shake = {"vx": 0, "vy": 0}


def shake():
    if not state.get("scream_active"):
        return
    _shake["vx"] += random.randint(-SHAKE_STEP, SHAKE_STEP)
    _shake["vy"] += random.randint(-SHAKE_STEP, SHAKE_STEP)
    _shake["vx"] = max(-SHAKE_AMPLITUDE, min(SHAKE_AMPLITUDE, _shake["vx"]))
    _shake["vy"] = max(-SHAKE_AMPLITUDE, min(SHAKE_AMPLITUDE, _shake["vy"]))
    _shake["vx"] = int(_shake["vx"] * 0.85)
    _shake["vy"] = int(_shake["vy"] * 0.85)

    sw, sh = screen_w * 2, screen_h * 2
    sx = -(screen_w // 2) + _shake["vx"]
    sy = -(screen_h // 2) + _shake["vy"]
    scream_win.geometry(f"{sw}x{sh}+{sx}+{sy}")
    state["shake_id"] = root.after(SHAKE_INTERVAL, shake)


def show_scream():
    sw, sh = screen_w * 2, screen_h * 2
    sx, sy = -(screen_w // 2), -(screen_h // 2)
    scream_win.geometry(f"{sw}x{sh}+{sx}+{sy}")
    scream_win.deiconify()
    scream_win.lift()
    scream_win.update_idletasks()

    draw_scream_noise(sw, sh)

    play_sound("a90scream.mp3")
    state["scream_active"] = True
    shake()

    def update_noise():
        if not state.get("scream_active"):
            return
        if not scream_win.winfo_exists():
            return
        try:
            draw_scream_noise(screen_w * 2, screen_h * 2)
        except Exception:
            pass
        state["scream_noise_id"] = root.after(SCREAM_NOISE_INTERVAL, update_noise)

    update_noise()


def start_scream():
    if not state["running"] or state["caught"]:
        return
    state["caught"] = True
    state["scream_delay_id"] = None
    for key in ("check_id", "music_end_id", "stop_id"):
        if state[key]:
            try:
                root.after_cancel(state[key])
            except Exception:
                pass
            state[key] = None
    pygame.mixer.stop()
    pygame.mixer.music.stop()
    root.withdraw()
    show_scream()
    state["download_id"] = root.after(
        int(DOWNLOAD_DELAY * 1000), show_downloading
    )


# ==================== DOWNLOADING ====================

def show_downloading():
    if not state["scream_active"]:
        return
    state["dl_active"] = True
    scream_win.withdraw()
    state["scream_active"] = False
    if state["scream_noise_id"]:
        try:
            root.after_cancel(state["scream_noise_id"])
        except Exception:
            pass
        state["scream_noise_id"] = None
    if state["shake_id"]:
        try:
            root.after_cancel(state["shake_id"])
        except Exception:
            pass
        state["shake_id"] = None
    dl_win.geometry(f"{screen_w}x{screen_h}+0+0")
    dl_win.deiconify()
    dl_win.lift()
    dl_win.update_idletasks()
    build_dl_ui()
    animate_progress(time.time())


def animate_progress(start_time):
    if not state["dl_active"]:
        return
    percent = min(1.0, (time.time() - start_time) / PROGRESS_TIME)
    cx, cy = screen_w // 2, screen_h // 2
    bar_w = 600
    bx = cx - bar_w // 2
    by = cy - 10
    filled = int(bar_w * percent)
    dl_canvas.delete("bar")
    dl_canvas.create_rectangle(bx, by, bx + filled, by + 40,
                                fill="#ff2222", outline="", tags="bar")
    dl_canvas.delete("percent")
    dl_canvas.create_text(cx, cy + 60, text=f"{int(percent * 100)}%",
                          fill="white", font=("Arial", 18, "bold"),
                          tags="percent")
    if percent >= 1.0:
        time.sleep(0.3)
        dl_win.withdraw()
        show_ransom()
        return
    state["progress_id"] = root.after(30, lambda: animate_progress(start_time))


# ==================== МОНЕТЫ + КРЕСТ ====================

def draw_coin(canvas, size=COIN_SIZE):
    c = size // 2
    r = size // 2 - 2
    canvas.create_oval(c - r + 3, c - r + 3, c + r + 3, c + r + 3,
                       fill="#7a5a00", outline="")
    canvas.create_oval(c - r, c - r, c + r, c + r,
                       fill="#ffd700", outline="#a87b00", width=3)
    canvas.create_oval(c - r + 8, c - r + 8, c + r - 8, c + r - 8,
                       outline="#a87b00", width=2)
    canvas.create_text(c, c, text="$", fill="#7a5a00",
                       font=("Arial", size // 3, "bold"))
    canvas.create_oval(c - r + 12, c - r + 10, c - r + 22, c - r + 20,
                       fill="#fff8b0", outline="")


def draw_cross(canvas, size=COIN_SIZE):
    c = size // 2
    r = size // 2 - 4
    canvas.create_rectangle(c - r, c - r, c + r, c + r,
                            fill="#220000", outline="#ff0000", width=2)
    canvas.create_rectangle(c - 6, c - r + 8, c + 6, c + r - 8,
                            fill="#ffd700", outline="#7a5a00", width=1)
    canvas.create_rectangle(c - r + 10, c - 12, c + r - 10, c + 0,
                            fill="#ffd700", outline="#7a5a00", width=1)
    canvas.create_oval(c - 2, c - r + 14, c + 2, c - r + 18,
                       fill="#ffffff", outline="")


def update_coin_label():
    if state.get("ransom_gold_label"):
        try:
            state["ransom_gold_label"].config(text=str(state["coin_count"]))
        except Exception:
            pass


def check_paid():
    if state["coin_count"] <= 0:
        pygame.mixer.stop()
        state["spam_active"] = False
        if state["spam_id"]:
            try:
                root.after_cancel(state["spam_id"])
            except Exception:
                pass
            state["spam_id"] = None
        cleanup()
        root.destroy()


def spawn_coin():
    if not state["running"] or not state["coin_active"]:
        return
    if len(state["coins"]) >= MAX_COINS:
        state["coin_id"] = root.after(int(COIN_SPAWN_INTERVAL * 1000), spawn_coin)
        return

    size = COIN_SIZE
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.configure(bg="black")
    win.attributes("-transparentcolor", "black")
    ww, wh = size + 20, size + 20
    px = random.randint(0, max(1, screen_w - ww))
    py = random.randint(0, max(1, screen_h - wh))
    win.geometry(f"{ww}x{wh}+{px}+{py}")
    canvas = tk.Canvas(win, width=ww, height=wh,
                       bg="black", highlightthickness=0)
    canvas.pack()

    state["coin_spawn_count"] += 1
    is_cross = (state["coin_spawn_count"] % CROSS_EVERY == 0)

    if is_cross:
        draw_cross(canvas, size)
    else:
        draw_coin(canvas, size)

    drag = {"dx": 0, "dy": 0}

    def on_press(event):
        drag["dx"] = event.x_root - win.winfo_x()
        drag["dy"] = event.y_root - win.winfo_y()

    def on_drag(event):
        win.geometry(f"+{event.x_root - drag['dx']}+{event.y_root - drag['dy']}")

    def on_release(event):
        gx1, gy1, gx2, gy2 = state.get("gold_zone", (0, 0, 0, 0))
        if gx1 <= event.x_root <= gx2 and gy1 <= event.y_root <= gy2:
            if is_cross:
                if not state["crucifix_used"]:
                    state["crucifix_used"] = True
                    crucifix_event()
                try:
                    win.destroy()
                except Exception:
                    pass
                if win in state["coins"]:
                    state["coins"].remove(win)
                return
            state["coin_count"] = max(0, state["coin_count"] - COIN_VALUE)
            update_coin_label()
            try:
                win.destroy()
            except Exception:
                pass
            if win in state["coins"]:
                state["coins"].remove(win)
            check_paid()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    state["coins"].append(win)
    if state["coin_active"] and state["running"]:
        state["coin_id"] = root.after(int(COIN_SPAWN_INTERVAL * 1000), spawn_coin)


def start_coins():
    state["coin_active"] = True
    state["coin_count"] = state["coin_target"]
    state["coin_spawn_count"] = 0
    update_coin_label()
    spawn_coin()


def stop_coins():
    state["coin_active"] = False
    if state["coin_id"]:
        try:
            root.after_cancel(state["coin_id"])
        except Exception:
            pass
        state["coin_id"] = None
    for win in list(state["coins"]):
        try:
            win.destroy()
        except Exception:
            pass
    state["coins"].clear()


# ==================== ТРЯСКА СПРАЙТА RANSOM ====================

def shake_ransom_face():
    if not state["running"]:
        return
    if not state.get("ransom_face_label"):
        return
    if not state["ransom_win"] or not state["ransom_win"].winfo_exists():
        return

    dx = random.randint(-FACE_SHAKE_AMP, FACE_SHAKE_AMP)
    dy = random.randint(-FACE_SHAKE_AMP, FACE_SHAKE_AMP)
    try:
        state["ransom_face_label"].place(
            x=15 + dx, y=15 + dy, width=120, height=120
        )
    except Exception:
        pass

    state["ransom_face_shake_id"] = root.after(FACE_SHAKE_INTERVAL,
                                                shake_ransom_face)


# ==================== РАСПЯТИЕ ====================

def _play_crucifix():
    if not state["running"]:
        return
    snd = state.get("crucifix_sound")
    if snd is None:
        print("[ЗВУК] crucifix не загружен!")
        return
    try:
        snd.play()
        print("[ЗВУК] crucifix играет")
    except Exception as e:
        print(f"[ЗВУК] ОШИБКА crucifix: {e}")


def crucifix_event():
    if not state["running"]:
        return
    if not state.get("ransom_win") or not state["ransom_win"].winfo_exists():
        return

    rw = state["ransom_win"]
    print("[РАСПЯТИЕ] Начало")

    pygame.mixer.stop()
    root.after(100, _play_crucifix)
    shake_ransom_face()

    state["spam_active"] = False
    for key in ("spam_id", "ransom_timer_id", "coin_id"):
        if state.get(key):
            try:
                root.after_cancel(state[key])
            except Exception:
                pass
            state[key] = None
    state["coin_active"] = False

    for win, _ in state["spam_windows"]:
        try:
            win.withdraw()
        except Exception:
            pass

    def start_anim():
        for child in rw.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

        canvas = tk.Canvas(rw, bg="#000000", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        rw.update_idletasks()
        ww = rw.winfo_width()
        wh = rw.winfo_height()
        cx = ww // 2
        cy = wh // 2

        spr_w, spr_h = 200, 200
        big = _pil_crucifix.resize(
            (spr_w * HD_SCALE, spr_h * HD_SCALE), Image.LANCZOS
        ).resize((spr_w, spr_h), Image.LANCZOS)
        a90_img = ImageTk.PhotoImage(big)
        canvas.a90_img = a90_img

        canvas.create_rectangle(0, 0, ww, wh, fill="#ffffff", tags="flash")

        def phase2():
            if not state["running"] or not rw.winfo_exists():
                return
            canvas.delete("all")
            canvas.create_rectangle(0, 0, ww, wh, fill="#000000")

            r = 130
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                fill="#8b0000", outline="#ff0000", width=5)
            canvas.create_oval(cx - r + 25, cy - r + 25,
                                cx + r - 25, cy + r - 25,
                                outline="#ff2222", width=3)

            for i in range(12):
                angle = i * math.pi / 6
                x1 = cx + int((r - 30) * math.cos(angle))
                y1 = cy + int((r - 30) * math.sin(angle))
                x2 = cx + int((r + 40) * math.cos(angle))
                y2 = cy + int((r + 40) * math.sin(angle))
                canvas.create_line(x1, y1, x2, y2, fill="#ffffff", width=2)

            for i in range(8):
                angle = i * math.pi / 4
                x1 = cx + int((r + 60) * math.cos(angle))
                y1 = cy + int((r + 60) * math.sin(angle))
                canvas.create_line(x1, y1, cx, cy,
                                   fill="#00ffff", width=3, dash=(5, 4))

            canvas.create_image(cx, cy, image=a90_img,
                                anchor="center", tags="a90")
            root.after(900, phase3)

        def phase3():
            if not state["running"] or not rw.winfo_exists():
                return
            canvas.delete("all")
            canvas.create_rectangle(0, 0, ww, wh, fill="#000000")

            for i in range(12):
                y = i * (wh // 12)
                canvas.create_oval(cx - 20, y, cx + 20, y + 25,
                                   outline="#c0c0c0", width=3)
                canvas.create_oval(cx - 15, y + 5, cx + 15, y + 20,
                                   outline="#808080", width=2)

            canvas.create_image(cx, cy - 60, image=a90_img,
                                anchor="center", tags="a90")

            anim = {"y": 0}

            def pull():
                if not state["running"] or not rw.winfo_exists():
                    return
                anim["y"] += 5
                try:
                    canvas.coords("a90", cx, cy - 60 + anim["y"])
                except Exception:
                    return
                if anim["y"] > wh:
                    canvas.delete("all")
                    canvas.create_rectangle(0, 0, ww, wh, fill="#000000")
                    canvas.create_text(cx, cy, text="SYSTEM CRASHED",
                                        fill="#ffffff",
                                        font=("Arial", 32, "bold"))
                    root.after(2000, lambda: (cleanup(), root.destroy()))
                    return
                state["crucifix_anim_id"] = root.after(50, pull)

            pull()

        root.after(150, phase2)

    root.after(1000, start_anim)


# ==================== RANSOM ====================

def update_gold_zone():
    if not state["running"]:
        return
    if state.get("ransom_win") and state["ransom_win"].winfo_exists():
        rw = state["ransom_win"]
        try:
            gx = rw.winfo_rootx() + 15
            gy = rw.winfo_rooty() + rw.winfo_height() - 80
            state["gold_zone"] = (gx, gy, gx + 200, gy + 70)
        except Exception:
            pass
    state["gold_zone_id"] = root.after(500, update_gold_zone)


def play_glitch():
    play_sound("glitch.mp3")


def show_ransom():
    rw = tk.Toplevel(root)
    rw.title("RANSOM")
    rw.attributes("-topmost", True)
    rw.configure(bg="#cc0000")
    state["ransom_win"] = rw

    rw_w, rw_h = 640, 360
    rx = (screen_w - rw_w) // 2
    ry = (screen_h - rw_h) // 2
    rw.geometry(f"{rw_w}x{rw_h}+{rx}+{ry}")
    rw.resizable(False, False)

    top = tk.Frame(rw, bg="#cc0000")
    top.place(x=0, y=0, width=rw_w, height=170)

    state["ransom_face_label"] = tk.Label(
        top, bg="#cc0000", image=img_ransom_face
    )
    state["ransom_face_label"].place(x=15, y=15, width=120, height=120)

    tk.Label(top, text="YOUR ITEMS\nHAVE BEEN\nENCRYPTED",
             bg="#cc0000", fg="white",
             font=("Arial", 26, "bold"),
             justify="left").place(x=160, y=20)

    warn_bg = tk.Frame(rw, bg="black")
    warn_bg.place(x=10, y=170, width=rw_w - 20, height=90)
    tk.Label(warn_bg,
             text=("IF YOU DO NOT PAY THIS RANSOM\n"
                   "BEFORE THE TIMER ENDS, YOUR ITEMS\n"
                   "WILL BE UNRECOVERABLE BY ANY MEANS."),
             bg="black", fg="white",
             font=("Arial", 13, "bold"),
             justify="center").pack(expand=True)

    bottom = tk.Frame(rw, bg="#cc0000")
    bottom.place(x=10, y=270, width=rw_w - 20, height=70)

    gold_box = tk.Frame(bottom, bg="#ffd700", bd=2, relief="solid")
    gold_box.pack(side="left", padx=(0, 10), fill="y")

    state["ransom_gold_label"] = tk.Label(
        gold_box, text=str(COIN_TARGET), bg="#ffd700", fg="black",
        font=("Arial", 26, "bold"), padx=15
    )
    state["ransom_gold_label"].pack(side="left")

    coin_canvas = tk.Canvas(gold_box, width=30, height=30,
                             bg="#ffd700", highlightthickness=0)
    coin_canvas.pack(side="left", padx=5)
    coin_canvas.create_oval(3, 3, 27, 27, fill="#ffd700",
                             outline="#7a5a00", width=2)
    coin_canvas.create_text(15, 15, text="$", fill="#7a5a00",
                             font=("Arial", 14, "bold"))

    timer_box = tk.Frame(bottom, bg="black", bd=2, relief="solid")
    timer_box.pack(side="left", fill="both", expand=True)
    tk.Label(timer_box, text="TIME:", bg="black", fg="white",
             font=("Arial", 26, "bold"), padx=15).pack(side="left")
    timer_label = tk.Label(timer_box, text="01:18", bg="black", fg="white",
                            font=("Arial", 26, "bold"), padx=15)
    timer_label.pack(side="right")

    rw.update_idletasks()
    gx = rw.winfo_rootx() + 15
    gy = rw.winfo_rooty() + rw.winfo_height() - 80
    state["gold_zone"] = (gx, gy, gx + 200, gy + 70)
    state["gold_zone_id"] = root.after(500, update_gold_zone)

    play_sound(PITCHED_MUSIC)
    state["glitch_id"] = root.after(int(GLITCH_AFTER_MUSIC * 1000), play_glitch)

    def tick(seconds_left):
        if not state["running"]:
            return
        if seconds_left < 0:
            stop_coins()
            if state["coin_count"] <= 0:
                cleanup()
                root.destroy()
            else:
                final_scream()
            return
        timer_label.config(text=f"{seconds_left // 60:02d}:{seconds_left % 60:02d}")
        state["ransom_timer_id"] = rw.after(1000, lambda: tick(seconds_left - 1))

    tick(RANSOM_TIME)
    start_spam()
    start_coins()


# ==================== ФИНАЛЬНЫЙ СКРИМЕР + BSOD ====================

def final_scream():
    if not state["running"] or state["final_scream_done"]:
        return
    state["final_scream_done"] = True
    pygame.mixer.stop()
    state["spam_active"] = False
    if state["spam_id"]:
        try:
            root.after_cancel(state["spam_id"])
        except Exception:
            pass
        state["spam_id"] = None
    try:
        if state["ransom_win"]:
            state["ransom_win"].withdraw()
    except Exception:
        pass
    for win, _ in state["spam_windows"]:
        try:
            win.withdraw()
        except Exception:
            pass

    sw, sh = screen_w * 2, screen_h * 2
    sx, sy = -(screen_w // 2), -(screen_h // 2)
    scream_win.geometry(f"{sw}x{sh}+{sx}+{sy}")
    scream_win.deiconify()
    scream_win.lift()
    scream_win.update_idletasks()
    draw_scream_noise(sw, sh)
    play_sound("a90screamold.mp3")
    state["scream_active"] = True
    shake()

    def update_noise():
        if not state.get("scream_active"):
            return
        if not scream_win.winfo_exists():
            return
        try:
            draw_scream_noise(screen_w * 2, screen_h * 2)
        except Exception:
            pass
        state["scream_noise_id"] = root.after(SCREAM_NOISE_INTERVAL, update_noise)

    update_noise()

    root.after(int(BSOD_DELAY * 1000), start_beeping)


def start_beeping():
    if not state["running"]:
        return
    play_sound("beep.mp3")
    state["beep_id"] = root.after(SHORT_BEEP_INTERVAL, start_beeping)
    if not state["bsod_shown"]:
        state["bsod_shown"] = True
        root.after(int(BSOD_SHOW_AFTER * 1000), show_bsod)


def show_bsod():
    if not state["running"]:
        return
    if state.get("beep_id"):
        try:
            root.after_cancel(state["beep_id"])
        except Exception:
            pass
        state["beep_id"] = None
    pygame.mixer.stop()

    scream_win.withdraw()
    state["scream_active"] = False
    if state["shake_id"]:
        try:
            root.after_cancel(state["shake_id"])
        except Exception:
            pass
        state["shake_id"] = None
    if state["scream_noise_id"]:
        try:
            root.after_cancel(state["scream_noise_id"])
        except Exception:
            pass
        state["scream_noise_id"] = None

    bsod = tk.Toplevel(root)
    bsod.overrideredirect(True)
    bsod.attributes("-topmost", True)
    bsod.configure(bg="#0000AA")
    bsod.geometry(f"{screen_w}x{screen_h}+0+0")

    text = ("A problem has been detected and Windows has been shut down "
            "to prevent damage to your computer.\n\n"
            "DRIVER_IRQL_NOT_LESS_OR_EQUAL\n\n"
            "If this is the first time you've seen this Stop error screen, "
            "restart your computer. If this screen appears again, follow "
            "these steps:\n\n"
            "Check to make sure any new hardware or software is properly "
            "installed. If this is a new installation, ask your hardware "
            "or software manufacturer for any Windows updates you might need.\n\n"
            "If problems continue, disable or remove any newly installed "
            "hardware or software. Disable BIOS memory options such as "
            "caching or shadowing. If you need to use Safe Mode to remove "
            "or disable components, restart your computer, press F8 to "
            "select Advanced Startup Options, and then select Safe Mode.\n\n"
            "Technical information:\n\n"
            "*** STOP: 0x000000D1 (0x0000000C, 0x00000002, 0x00000000, "
            "0xF86B5A89)\n\n"
            "*** a90.sys - Address F86B5A89 base at F86B5000, "
            "DateStamp 3dd9919eb\n\n"
            "Beginning dump of physical memory\n"
            "Physical memory dump complete.\n"
            "Contact your system administrator or technical support group "
            "for further assistance.\n\n"
            "Press ENTER to continue...")

    bsod_text = tk.Label(bsod, text=text,
                         bg="#0000AA", fg="#FFFFFF",
                         font=("Consolas", 14),
                         justify="left", anchor="nw",
                         padx=60, pady=60)
    bsod_text.pack(fill="both", expand=True)

    def on_enter(event=None):
        try:
            bsod.destroy()
        except Exception:
            pass
        cleanup()
        root.destroy()

    bsod.bind("<Return>", on_enter)
    root.bind("<Return>", on_enter)
    bsod.focus_force()
    state["bsod_win"] = bsod


# ==================== ГЛЮК-ОКНА ====================

def make_glitch_image(ww, wh, screaming):
    if ww < 50 or wh < 50:
        ww, wh = max(50, ww), max(50, wh)
    bw = ww * HD_SCALE
    bh = wh * HD_SCALE
    img = Image.new("RGB", (bw, bh), (170, 0, 0))
    d = ImageDraw.Draw(img)

    if screaming:
        try:
            spr = _pil_scream.resize((bw, bh), Image.LANCZOS)
            img.paste(spr, (0, 0), spr)
        except Exception:
            pass
    else:
        d.rectangle([0, 0, bw, bh], fill=(170, 0, 0))

        for _ in range(random.randint(8, 20)):
            y = random.randint(0, bh)
            h = random.randint(1, 5)
            color = random.choice([
                (255, 255, 255), (0, 0, 0),
                (255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (255, 0, 255), (0, 255, 255),
            ])
            d.rectangle([0, y, bw, y + h], fill=color)

        for _ in range(random.randint(40, 100)):
            px = random.randint(0, max(1, bw - 4))
            py = random.randint(0, max(1, bh - 4))
            color = random.choice([(255, 255, 255), (0, 0, 0),
                                    (255, 0, 0), (0, 255, 0)])
            d.rectangle([px, py, px + 3, py + 3], fill=color)

        if random.random() < 0.7:
            spr = random.choice([_pil_scream, _pil_idle])
            spr_small = spr.resize((100, 100), Image.LANCZOS)
            sx = random.randint(0, max(1, bw - 100))
            sy = random.randint(0, max(1, bh - 100))
            img.paste(spr_small, (sx, sy), spr_small)

    img = img.resize((ww, wh), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def spam_window():
    if not state["running"] or not state["spam_active"]:
        return
    if len(state["spam_windows"]) >= SPAM_MAX_WINDOWS:
        return

    win = tk.Toplevel(root)
    title = random.choice(SPAM_TITLES)
    win.title(title)
    win.attributes("-topmost", True)
    win.configure(bg="#1a1a1a")

    ww = random.randint(300, 520)
    wh = random.randint(180, 320)
    px = random.randint(0, max(1, screen_w - ww))
    py = random.randint(0, max(1, screen_h - wh))
    win.geometry(f"{ww}x{wh}+{px}+{py}")

    label_glitch = tk.Label(win, bg="#1a1a1a", bd=0)
    label_glitch.pack(expand=True, fill="both")

    screaming = random.random() < SCREAM_CHANCE

    def update_glitch():
        if not state["running"] or not win.winfo_exists():
            return
        try:
            img = make_glitch_image(ww, wh, screaming)
            label_glitch.config(image=img)
            label_glitch.image = img
        except Exception:
            pass
        win.after(GLITCH_FPS_MS, update_glitch)

    update_glitch()

    # === ТРЯСКА ОКНА ===
    _ws = {"vx": 0, "vy": 0}

    def win_shake():
        if not state["running"] or not win.winfo_exists():
            return
        _ws["vx"] += random.randint(-WIN_SHAKE_STEP, WIN_SHAKE_STEP)
        _ws["vy"] += random.randint(-WIN_SHAKE_STEP, WIN_SHAKE_STEP)
        _ws["vx"] = max(-WIN_SHAKE_AMP, min(WIN_SHAKE_AMP, _ws["vx"]))
        _ws["vy"] = max(-WIN_SHAKE_AMP, min(WIN_SHAKE_AMP, _ws["vy"]))
        _ws["vx"] = int(_ws["vx"] * 0.85)
        _ws["vy"] = int(_ws["vy"] * 0.85)
        try:
            win.geometry(f"{ww}x{wh}+{px + _ws['vx']}+{py + _ws['vy']}")
        except Exception:
            return
        win.after(WIN_SHAKE_INTERVAL, win_shake)

    win_shake()

    state["spam_windows"].append((win, label_glitch))


def spawn_spam_batch(count=SPAM_BATCH):
    for _ in range(count):
        spam_window()


def start_spam():
    state["spam_active"] = True
    spawn_spam_batch(SPAM_BATCH)
    state["spam_id"] = root.after(int(SPAM_INTERVAL * 1000), spam_window)


# ==================== ОБРАБОТЧИКИ ====================

def caught():
    if not state["running"] or state["caught"]:
        return
    if state["scream_delay_id"]:
        return
    state["scream_delay_id"] = root.after(
        int(SCREAM_DELAY * 1000), start_scream
    )


def survived():
    if state["running"]:
        cleanup()
        root.destroy()


def on_key(event):
    caught()


def check_mouse():
    if not state["running"] or state["caught"]:
        return
    mx = root.winfo_pointerx()
    my = root.winfo_pointery()
    if state["last_mouse"] is None:
        state["last_mouse"] = (mx, my)
    else:
        lx, ly = state["last_mouse"]
        if abs(mx - lx) > MOUSE_TOLERANCE or abs(my - ly) > MOUSE_TOLERANCE:
            caught()
            return
        state["last_mouse"] = (mx, my)
    state["check_id"] = root.after(CHECK_INTERVAL, check_mouse)


def check_music_end():
    if not state["running"] or state["caught"]:
        return
    if not pygame.mixer.get_busy():
        survived()
        return
    state["music_end_id"] = root.after(100, check_music_end)


root.bind("<Key>", on_key)

flash_delay_ms = max(0, int((STOP_DELAY - FLASH_TIME / 1000) * 1000))
state["flash_id"] = root.after(flash_delay_ms, show_flash)
state["stop_id"] = root.after(int(STOP_DELAY * 1000), show_stop)
state["check_id"] = root.after(CHECK_INTERVAL, check_mouse)
state["music_end_id"] = root.after(100, check_music_end)

root.mainloop()