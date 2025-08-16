# -----------------------------------------------------------------------------
# Importamos las librerias 
# -----------------------------------------------------------------------------
import pygame
import config as cfg 

# -----------------------------------------------------------------------------
def process_input(events, KEY_MAPPINGS):
    """
    A partir de 'events' del frame:
      - chip8_keys: lista de 16 bools (estado continuo)
      - pressed_once: 0x0..0xF si hubo KEYDOWN mapeado, o None
    """
    keys = pygame.key.get_pressed()
    chip8_keys = [False] * 16
    for k, pgk in KEY_MAPPINGS.items():
        chip8_keys[k] = keys[pgk]

    pressed_once = None
    for e in events:
        if e.type == pygame.KEYDOWN:
            for k, pgk in KEY_MAPPINGS.items():
                if e.key == pgk:
                    pressed_once = k
                    break
    return chip8_keys, pressed_once

# -----------------------------------------------------------------------------
def tick_timers(delay_timer, sound_timer, accumulator_ms, dt_ms):
    """
    Disminuye DT y ST a 60 Hz usando acumulador en ms.
    """
    accumulator_ms += dt_ms
    step = 1000.0 / 60.0
    while accumulator_ms >= step:
        if delay_timer > 0:
            delay_timer -= 1
        if sound_timer > 0:
            sound_timer -= 1
        accumulator_ms -= step
    return delay_timer, sound_timer, accumulator_ms


# -----------------------------------------------------------------------------
def load_game(ruta_archivo):
    """
    Lee un archivo binario y devuelve su contenido como una lista de bytes.

    Parámetros:
        ruta_archivo (str): Ruta al archivo a leer.

    Retorna:
        list[int]: Lista de enteros (0-255) representando cada byte del archivo.
    """
    with open(ruta_archivo, "rb") as f:
        contenido = f.read()  # Leo todo el archivo como bytes
    return list(contenido)


# -----------------------------------------------------------------------------
def setup_graphics(SCALE):
    """
    Inicializa la ventana de Pygame con el tamaño adecuado según
    la resolución CHIP-8 (64x32) y el factor de escala SCALE.
    """
    global pantalla
    ancho_px = 64 * SCALE+1
    alto_px = 32 * SCALE+1
    pantalla = pygame.display.set_mode((ancho_px, alto_px))
    pygame.display.set_caption("Emulador CHIP-8")
    pantalla.fill((0, 0, 0))
    pygame.display.flip()


# -----------------------------------------------------------------------------
def draw_graphics(gfx, SCALE):
    """
    Dibuja el contenido de gfx en la ventana usando SCALE para escalar cada píxel.
    gfx es una lista de 32 filas x 64 columnas, con valores 0 (apagado) o 1 (encendido).
    """
    
    pantalla.fill((0, 0, 0)) #Limpiar fondo (negro)

    # 2) Dibujar píxeles (blanco encendido, negro apagado)
    for y in range(32):
        for x in range(64):
            if gfx[y][x]:
                pygame.draw.rect(
                    pantalla,
                    (255, 255, 255),
                    (x * SCALE, y * SCALE, SCALE, SCALE)
                )

    # 3) Dibujar la grilla por encima de todo
    color_grid = (64, 64, 64)

    # Horizontales (32 celdas ⇒ 33 líneas, incluyendo bordes)
    for y in range(33):
        pygame.draw.line(
            pantalla, cfg.GRID_COLOR,
            (0, y * SCALE), (64 * SCALE, y * SCALE), 1
        )

    # Verticales (64 celdas ⇒ 65 líneas, incluyendo bordes)
    for x in range(65):
        pygame.draw.line(
            pantalla, cfg.GRID_COLOR,
            (x * SCALE, 0), (x * SCALE, 32 * SCALE), 1
        )

    pygame.display.flip()


# -----------------------------------------------------------------------------
def fetch_opcode(memory, pc):
    """
    Lee 2 bytes desde memory en la dirección pc y devuelve el opcode de 16 bits.
    """
    # global pc, memory
    return (memory[pc] << 8) | memory[pc + 1]


def decode_opcode(opcode: int):
    """
    Descompone el opcode de 16 bits en campos útiles para el decodificador.

    Devuelve:
        dict con:
          op  : nibble alto (tipo de instrucción)
          nnn : dirección de 12 bits
          n   : nibble bajo (normalmente tamaño/sufijo)
          x   : registro X (0..F)
          y   : registro Y (0..F)
          kk  : byte inmediato (0..255)
    """
    return {
        "op":  (opcode & 0xF000) >> 12,
        "nnn":  opcode & 0x0FFF,
        "n":    opcode & 0x000F,
        "x":   (opcode & 0x0F00) >> 8,
        "y":   (opcode & 0x00F0) >> 4,
        "kk":   opcode & 0x00FF,
    }

