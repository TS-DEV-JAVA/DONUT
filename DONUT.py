import os
import base64
import tempfile
import pygame
import math
import time
import threading
import shutil
import msvcrt
import random
import atexit
from colorama import Fore, Style, init

init(autoreset=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
audio_file_path = os.path.join(script_dir, "chill_base64_audio.txt")

def load_base64_audio(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r"
        cleaned = ''.join(c for c in data if c in allowed).replace('\n','').replace('\r','')
        return cleaned

base64_audio = load_base64_audio(audio_file_path)

def write_temp_wav(b64_string):
    audio_data = base64.b64decode(b64_string)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.write(audio_data)
    temp_file.close()
    return temp_file.name

pygame.mixer.init()
wav_path = write_temp_wav(base64_audio)
sound = pygame.mixer.Sound(wav_path)
sound.play(loops=-1)
muted = False

def cleanup():
    try:
        os.remove(wav_path)
    except:
        pass
atexit.register(cleanup)

def key_listener():
    global muted
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in (b'\x00', b'\xe0'):
                key2 = msvcrt.getch()
                if key2 == b'\x41':  # F7 key
                    muted = not muted
                    sound.set_volume(0 if muted else 1)
        time.sleep(0.01)

threading.Thread(target=key_listener, daemon=True).start()

def get_terminal_size():
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except:
        return 80, 24

SPRINKLE_COLORS = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN,
    Fore.MAGENTA, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX,
    Fore.LIGHTYELLOW_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTMAGENTA_EX
]

def get_chocolate_char(char):
    chocolate_map = {
        '.': Fore.YELLOW,
        ',': Fore.LIGHTYELLOW_EX,
        '-': Fore.LIGHTBLACK_EX,
        '~': Fore.BLACK,
        ':': Fore.YELLOW,
        ';': Fore.YELLOW,
        '=': Fore.LIGHTYELLOW_EX,
        '!': Fore.YELLOW,
        '*': Fore.LIGHTBLACK_EX,
        '#': Fore.YELLOW,
        '$': Fore.LIGHTBLACK_EX,
        '@': Fore.LIGHTYELLOW_EX,
    }
    return chocolate_map.get(char, Fore.WHITE) + char

def get_sprinkle_char():
    sprinkle_chars = ['*', '+', '.', '\'']
    color = random.choice(SPRINKLE_COLORS)
    char = random.choice(sprinkle_chars)
    return color + char

def get_colored_char(char):
    sprinkle_chance = 0.07
    if char in ".,-~:;=!*#$@":
        if random.random() < sprinkle_chance:
            return get_sprinkle_char()
        else:
            return get_chocolate_char(char)
    else:
        return Fore.WHITE + char

def run_donut():
    term_width, term_height = get_terminal_size()

    banner_lines = [
        Fore.MAGENTA + Style.BRIGHT + "-" * 40,
        Fore.YELLOW + Style.BRIGHT + "DONUT.PY !".center(40),
        Fore.CYAN + Style.BRIGHT + "TS (PLZ DONT  @)".center(40),
        Fore.GREEN + Style.BRIGHT + "PRESS F7 TO MUTE THE SOUND 🎵".center(40),
    ]
    banner_height = len(banner_lines)

    WIDTH = min(60, term_width)
    HEIGHT = max(12, term_height - banner_height - 2)
    HEIGHT = min(20, HEIGHT)

    R1 = 1.8
    R2 = 3.5
    K2 = 30
    K1 = WIDTH * K2 * 3 / (8 * (R1 + R2))

    A = 0
    B = 0

    offset_top = 4

    theta_step = 0.5
    phi_step = 0.5

    while True:
        start_time = time.time()

        output = [' '] * (WIDTH * HEIGHT)
        zbuffer = [0] * (WIDTH * HEIGHT)

        theta_deg = 0.0
        while theta_deg < 360:
            theta = math.radians(theta_deg)
            costheta = math.cos(theta)
            sintheta = math.sin(theta)

            phi_deg = 0.0
            while phi_deg < 360:
                phi = math.radians(phi_deg)
                cosphi = math.cos(phi)
                sinphi = math.sin(phi)

                circlex = R2 + R1 * costheta
                circley = R1 * sintheta

                x = circlex * (math.cos(B) * cosphi + math.sin(A) * math.sin(B) * sinphi) - circley * math.cos(A) * math.sin(B)
                y = circlex * (math.sin(B) * cosphi - math.sin(A) * math.cos(B) * sinphi) + circley * math.cos(A) * math.cos(B)
                z = K2 + math.cos(A) * circlex * sinphi + circley * math.sin(A)
                ooz = 1 / z

                xp = int(WIDTH / 2 + K1 * ooz * x)
                yp = int(HEIGHT / 2 - K1 * ooz * y)

                L = cosphi * costheta * math.sin(B) - math.cos(A) * costheta * sinphi - math.sin(A) * sintheta + cosphi * math.sin(B)
                luminance_index = max(0, min(11, int(L * 11)))

                idx = xp + yp * WIDTH

                if 0 <= idx < WIDTH * HEIGHT:
                    if ooz > zbuffer[idx]:
                        zbuffer[idx] = ooz
                        chars = ".,-~:;=!*#$@"
                        char = chars[luminance_index] if luminance_index < len(chars) else '.'
                        output[idx] = get_colored_char(char)

                phi_deg += phi_step
            theta_deg += theta_step

        os.system('cls' if os.name == 'nt' else 'clear')
        print('\n' * offset_top, end='')

        padding_h = ' ' * ((term_width - WIDTH) // 2 if term_width > WIDTH else 0)
        for i in range(0, WIDTH * HEIGHT, WIDTH):
            line = ''.join(output[i:i + WIDTH])
            print(padding_h + line)

        empty_lines_after_donut = term_height - HEIGHT - banner_height - offset_top
        if empty_lines_after_donut > 0:
            print('\n' * empty_lines_after_donut, end='')

        for line in banner_lines:
            pad = ' ' * ((term_width - len(line)) // 2 if term_width > len(line) else 0)
            print(pad + line)

        # FAST AS F*** spin speeds:
        A += 5
        B += 5

        time.sleep(0.005)  # very fast frame rate (~200 FPS)

threading.Thread(target=run_donut, daemon=True).start()

while True:
    time.sleep(0.01)