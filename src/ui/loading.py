import time

import pygame

import src.config as config


def show_loading_screen(screen):
    screen.fill(config.COLOR_BG)
    loading_texts = [
        "INITIALIZING G.A.D.C.I. PROTOCOL...",
        "LOADING TERRAIN DATA... OK",
        "SYNCING WITH SATELLITE NETWORK... OK",
        "CALIBRATING SENSORS... OK",
        "SYSTEM STATUS: [||||||||||] 100%",
        "WELCOME, COMMANDER."
    ]
    for i, text in enumerate(loading_texts):
        screen.fill(config.COLOR_BG)
        for j in range(i + 1):
            txt = config.font_large.render(loading_texts[j], True, config.COLOR_TEXT)
            screen.blit(txt, (config.WINDOW_WIDTH // 2 - txt.get_width() // 2,
                              config.WINDOW_HEIGHT // 2 - (len(loading_texts) * 20) // 2 + j * 30))
        pygame.display.flip()
        time.sleep(0.3)
    time.sleep(0.3)
