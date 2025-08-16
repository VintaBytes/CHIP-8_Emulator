# -----------------------------------------------------------------------------
# Emulador CHIP-8 (Agosto-2025)
#
# Enlaces útiles:
#   Guia (sin código): https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
#                      https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
#   Opcodes..........: https://chip8.gulrak.net/
#   Roms de prueba...: https://github.com/Timendus/chip8-test-suite?tab=readme-ov-file
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Importa la libreria e inicializa todos los módulos de Pygame 
# (gráficos, sonido, etc.)
# -----------------------------------------------------------------------------
import pygame, random
import config as cfg
from chip8_funciones import (
    load_game, setup_graphics, draw_graphics, fetch_opcode,
    decode_opcode, process_input, tick_timers
)
from chip8_instrucciones import (
    op_00E0, op_00EE, op_1NNN, op_2NNN, op_3XNN, op_4XNN, op_5XY0,
    op_6XNN, op_7XNN, op_8XY0, op_8XY1, op_8XY2, op_8XY3, op_8XY4,
    op_8XY5, op_8XY6, op_8XY7, op_8XYE, op_9XY0, op_ANNN, op_BNNN,
    op_CXNN, op_DXYN, op_EX9E, op_EXA1, op_FX0A, op_FX07, op_FX15,
    op_FX18, op_FX1E, op_FX29, op_FX33, op_FX55, op_FX65
)


# -----------------------------------------------------------------------------
# Inicialización de la ventana en Pygame
# -----------------------------------------------------------------------------
pygame.init()
pygame.display.set_caption(cfg.WINDOW_TITLE)  # título desde config
setup_graphics(cfg.SCALE)                      # escala desde config

# -----------------------------------------------------------------------------
# Estado inicial del emulador
# -----------------------------------------------------------------------------
memory = [0] * cfg.MEM_SIZE
v_reg  = [0] * 16
stack  = []
pc     = cfg.PROGRAM_START
index  = 0
delay_timer = 0
sound_timer = 0
gfx = [[0 for _ in range(cfg.SCREEN_W)] for _ in range(cfg.SCREEN_H)]

# -----------------------------------------------------------------------------
# Fuente integrada en memoria (necesario para FX29)
# -----------------------------------------------------------------------------
for i, b in enumerate(cfg.FONT_SET):
    memory[cfg.FONT_DIR + i] = b

# -----------------------------------------------------------------------------
# Cargar ROM por defecto desde config
# -----------------------------------------------------------------------------
rom_bytes = load_game(cfg.ROM_PATH)
for i, b in enumerate(rom_bytes):
    memory[cfg.PROGRAM_START + i] = b

# -----------------------------------------------------------------------------
# RNG para CXNN (semilla opcional)
# -----------------------------------------------------------------------------
rng = random.Random(cfg.RNG_SEED) if cfg.RNG_SEED is not None else random


# -----------------------------------------------------------------------------
# Buicle principal
# -----------------------------------------------------------------------------
clock = pygame.time.Clock()
accum_ms = 0.0
running = True

while running:
    dt_ms = clock.tick(cfg.CPU_HZ)   # velocidad “CPU” 
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False

    chip8_keys, pressed_once = process_input(events, cfg.KEY_MAPPINGS)

    # -------------------------
    # FETCH/DECODE 
    # -------------------------
    opcode = fetch_opcode(memory, pc)
    pc += 2
    f = decode_opcode(opcode)
    op, x, y, n, kk, nnn = f["op"], f["x"], f["y"], f["n"], f["kk"], f["nnn"]

    # -------------------------
    # DISPATCH
    # -------------------------
    if opcode == 0x00E0:
        gfx = op_00E0(gfx)
        draw_graphics(gfx, cfg.SCALE)

    elif opcode == 0x00EE: pc, stack = op_00EE(stack)
    elif op == 0x1: pc = op_1NNN(pc, nnn)
    elif op == 0x2: pc, stack = op_2NNN(pc, nnn, stack)
    elif op == 0x3: pc = op_3XNN(pc, v_reg, x, kk)
    elif op == 0x4: pc = op_4XNN(pc, v_reg, x, kk)
    elif op == 0x5 and n == 0x0: pc = op_5XY0(pc, v_reg, x, y)
    elif op == 0x6: v_reg = op_6XNN(v_reg, x, kk)
    elif op == 0x7: v_reg = op_7XNN(v_reg, x, kk)
    elif op == 0x8:
        if   n == 0x0: v_reg = op_8XY0(v_reg, x, y)
        elif n == 0x1: v_reg = op_8XY1(v_reg, x, y)
        elif n == 0x2: v_reg = op_8XY2(v_reg, x, y)
        elif n == 0x3: v_reg = op_8XY3(v_reg, x, y)
        elif n == 0x4: v_reg = op_8XY4(v_reg, x, y)
        elif n == 0x5: v_reg = op_8XY5(v_reg, x, y)
        elif n == 0x6: v_reg = op_8XY6(v_reg, x, y, cfg.QUIRK_SHIFT_USES_VY)
        elif n == 0x7: v_reg = op_8XY7(v_reg, x, y)
        elif n == 0xE: v_reg = op_8XYE(v_reg, x, y, cfg.QUIRK_SHIFT_USES_VY)
    elif op == 0x9 and n == 0x0: pc = op_9XY0(pc, v_reg, x, y)
    elif op == 0xA: index = op_ANNN(index, nnn)
    elif op == 0xB: pc = op_BNNN(pc, v_reg, nnn)
    elif op == 0xC: v_reg = op_CXNN(v_reg, x, kk, rng=rng)
    elif op == 0xD: 
        gfx, v_reg = op_DXYN(gfx, v_reg, x, y, n, memory, index)
        draw_graphics(gfx, cfg.SCALE)
    elif op == 0xE:
        if   kk == 0x9E: pc = op_EX9E(pc, v_reg, x, chip8_keys)
        elif kk == 0xA1: pc = op_EXA1(pc, v_reg, x, chip8_keys)
    elif op == 0xF:
        if   kk == 0x07: v_reg = op_FX07(v_reg, x, delay_timer)
        elif kk == 0x0A:
            v_reg, waiting = op_FX0A(v_reg, x, pressed_once)
            if waiting: pc -= 2
        elif kk == 0x15: delay_timer = op_FX15(delay_timer, v_reg, x)
        elif kk == 0x18: sound_timer = op_FX18(sound_timer, v_reg, x)
        elif kk == 0x1E:
            index, vf = op_FX1E(index, v_reg, x)
            if cfg.QUIRK_ADDI_SETS_VF:
                v_reg[0xF] = vf
        elif kk == 0x29: index = op_FX29(index, v_reg, x, cfg.FONT_DIR)
        elif kk == 0x33: memory = op_FX33(memory, index, v_reg, x)
        elif kk == 0x55: memory, index = op_FX55(memory, index, v_reg, x, increment_I=cfg.FX_BULK_INC_I)
        elif kk == 0x65: v_reg, index = op_FX65(memory, index, v_reg, x, increment_I=cfg.FX_BULK_INC_I)

    # Timers a 60 Hz
    delay_timer, sound_timer, accum_ms = tick_timers(delay_timer, sound_timer, accum_ms, dt_ms)

# -----------------------------------------------------------------------------
# FIN.
# -----------------------------------------------------------------------------
pygame.quit()
