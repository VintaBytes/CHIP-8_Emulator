# -----------------------------------------------------------------------------
# CHIP-8 – Archivo de Configuración
# -----------------------------------------------------------------------------
# ROM a cargar (implementar menu para seleccionar desde el HD)
ROM_PATH = "./roms/2-ibm-logo1.ch8"

# Pantalla
SCREEN_W   = 64
SCREEN_H   = 32
SCALE      = 10
WINDOW_TITLE = "Emulador CHIP-8"

# Colores / grilla (opcional)
BG_COLOR   = (0, 0, 0)
FG_COLOR   = (255, 255, 255)
GRID_ON    = True
GRID_COLOR = (0, 0, 0)

# Memoria y layout
MEM_SIZE       = 0x1000
PROGRAM_START  = 0x200
FONT_DIR       = 0x50

# Timings
CPU_HZ    = 500          # “ciclos” lógicos por segundo (tope con clock.tick)
TIMER_HZ  = 60           # DT/ST a 60 Hz

# Quirks (compatibilidad de ROMs viejas/mas recientes)
QUIRK_SHIFT_USES_VY = False   # 8XY6/8XYE usan Vy y copian en Vx (legacy)
QUIRK_ADDI_SETS_VF  = True    # FX1E setea VF si I overflowea
FX_BULK_INC_I       = True    # FX55/FX65 incrementan I
DXYN_WRAP           = True    # Dibujo con wrap-around

# RNG (para CXNN). ¿reproducibilidad? = semilla (int); si no, None
RNG_SEED = None

# Teclado CHIP-8 ↔ pygame
import pygame
KEY_MAPPINGS = {
    0x0: pygame.K_x,
    0x1: pygame.K_1, 0x2: pygame.K_2, 0x3: pygame.K_3,
    0x4: pygame.K_q, 0x5: pygame.K_w, 0x6: pygame.K_e,
    0x7: pygame.K_a, 0x8: pygame.K_s, 0x9: pygame.K_d,
    0xA: pygame.K_z, 0xB: pygame.K_c,
    0xC: pygame.K_4, 0xD: pygame.K_r, 0xE: pygame.K_f, 0xF: pygame.K_v,
}

# Fuente (4x5 por dígito) – 16 * 5 bytes
FONT_SET = [
  0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
  0x20, 0x60, 0x20, 0x20, 0x70, # 1
  0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
  0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
  0x90, 0x90, 0xF0, 0x10, 0x10, # 4
  0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
  0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
  0xF0, 0x10, 0x20, 0x40, 0x40, # 7
  0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
  0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
  0xF0, 0x90, 0xF0, 0x90, 0x90, # A
  0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
  0xF0, 0x80, 0x80, 0x80, 0xF0, # C
  0xE0, 0x90, 0x90, 0x90, 0xE0, # D
  0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
  0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

