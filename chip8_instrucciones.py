# -----------------------------------------------------------------------------
# Importamos las librerias 
# -----------------------------------------------------------------------------
import random
import config as cfg 

# -----------------------------------------------------------------------------
def op_00E0(gfx):
    """
    CLS: Clear screen.
    """
    gfx = [[0 for _ in range(64)] for _ in range(32)]
    return gfx


# -----------------------------------------------------------------------------
def op_1NNN(pc, nnn):
    """
    JP addr: Salta a la dirección nnn.
    """
    pc = nnn
    return pc


# -----------------------------------------------------------------------------
def op_6XNN(v_reg, x, kk):
    """
    LD Vx, byte: Vx = kk
    """
    v_reg[x] = kk
    return v_reg


# -----------------------------------------------------------------------------
def op_7XNN(v_reg, x, kk):
    """
    ADD Vx, byte: Vx += kk (sin carry)
    """
    v_reg[x] = (v_reg[x] + kk) & 0xFF
    return v_reg


# -----------------------------------------------------------------------------
def op_ANNN(index, nnn):
    """
    LD I, addr: I = nnn
    """
    index = nnn
    return index


# -----------------------------------------------------------------------------
def op_2NNN(pc, nnn, stack):
    """
    CALL addr: Llama a la subrutina en nnn.
    Empuja el PC actual a la pila y salta a nnn.
    """
    stack.append(pc)  # Guarda la dirección de retorno
    pc = nnn
    return pc, stack


# -----------------------------------------------------------------------------
def op_00EE(stack):
    """
    RET: Vuelve de una subrutina.
    Extrae de la pila la última dirección y salta a ella.
    """
    if stack:
        pc = stack.pop()
    else:
        raise RuntimeError("RET (00EE) llamado con la pila vacía")
    return pc, stack

# -----------------------------------------------------------------------------
def op_3XNN(pc, v_reg, x, kk):
    """
    SE Vx, byte: Salta la siguiente instrucción si Vx == kk.
    """
    if v_reg[x] == kk:
        pc += 2
    return pc

# -----------------------------------------------------------------------------
def op_4XNN(pc, v_reg, x, kk):
    """
    SNE Vx, byte: Salta la siguiente instrucción si Vx != kk.
    """
    if v_reg[x] != kk:
        pc += 2
    return pc


# -----------------------------------------------------------------------------
def op_5XY0(pc, v_reg, x, y):
    """
    SE Vx, Vy: Salta la siguiente instrucción si Vx == Vy.
    (Solo si el último nibble es 0, de ahí el '0' en 5XY0)
    """
    if v_reg[x] == v_reg[y]:
        pc += 2
    return pc


# -----------------------------------------------------------------------------
def op_9XY0(pc, v_reg, x, y):
    """
    SNE Vx, Vy: Salta la siguiente instrucción si Vx != Vy.
    (Solo si el último nibble es 0, de ahí el '0' en 9XY0)
    """
    if v_reg[x] != v_reg[y]:
        pc += 2
    return pc

# -----------------------------------------------------------------------------
def op_8XY0(v_reg, x, y):
    """LD Vx, Vy"""
    v_reg[x] = v_reg[y]
    return v_reg

# -----------------------------------------------------------------------------
def op_8XY1(v_reg, x, y):
    """OR Vx, Vy"""
    v_reg[x] |= v_reg[y]
    return v_reg

# -----------------------------------------------------------------------------
def op_8XY2(v_reg, x, y):
    """AND Vx, Vy"""
    v_reg[x] &= v_reg[y]
    return v_reg

# -----------------------------------------------------------------------------
def op_8XY3(v_reg, x, y):
    """XOR Vx, Vy"""
    v_reg[x] ^= v_reg[y]
    return v_reg

# -----------------------------------------------------------------------------
def op_8XY4(v_reg, x, y):
    """ADD Vx, Vy con carry"""
    total = v_reg[x] + v_reg[y]
    v_reg[0xF] = 1 if total > 0xFF else 0
    v_reg[x] = total & 0xFF
    return v_reg

# -----------------------------------------------------------------------------
def op_8XY5(v_reg, x, y):
    """SUB Vx, Vy (Vx = Vx - Vy) con borrow"""
    # 8XY5: Vx = Vx - Vy ; VF = 1 si Vx >= Vy, si no 0
    v_reg[0xF] = 1 if v_reg[x] >= v_reg[y] else 0
    v_reg[x] = (v_reg[x] - v_reg[y]) & 0xFF
    return v_reg

# -----------------------------------------------------------------------------
def op_8XY6(v_reg, x, y, quirk=cfg.QUIRK_SHIFT_USES_VY):
    """SHR Vx >> 1"""
    if quirk:
        v_reg[0xF] = v_reg[y] & 0x1
        v_reg[x]   = (v_reg[y] >> 1) & 0xFF
    else:
        v_reg[0xF] = v_reg[x] & 0x1
        v_reg[x] >>= 1
    return v_reg

# -----------------------------------------------------------------------------
def op_8XY7(v_reg, x, y):
    """SUBN Vx, Vy (Vx = Vy - Vx) con borrow"""
    # 8XY7: Vx = Vy - Vx ; VF = 1 si Vy >= Vx, si no 0
    v_reg[0xF] = 1 if v_reg[y] >= v_reg[x] else 0
    v_reg[x] = (v_reg[y] - v_reg[x]) & 0xFF# 
    return v_reg

# -----------------------------------------------------------------------------
def op_8XYE(v_reg, x, y, quirk=cfg.QUIRK_SHIFT_USES_VY):
    if quirk:
        v_reg[0xF] = (v_reg[y] & 0x80) >> 7
        v_reg[x]   = (v_reg[y] << 1) & 0xFF
    else:
        v_reg[0xF] = (v_reg[x] & 0x80) >> 7
        v_reg[x]   = (v_reg[x] << 1) & 0xFF
    return v_reg

# -----------------------------------------------------------------------------
def op_BNNN(pc, v_reg, nnn):
    """
    JP V0, addr: PC = nnn + V0
    """
    return (nnn + (v_reg[0] & 0xFF)) & 0x0FFF

# -----------------------------------------------------------------------------
def op_CXNN(v_reg, x, kk, rng=random):
    """
    RND Vx, byte: Vx = (random_byte & kk)
    rng debe exponer .randint(0, 255); por defecto, 'random' estándar de Python.
    """
    v_reg[x] = rng.randint(0, 255) & kk
    return v_reg

# -----------------------------------------------------------------------------
def op_DXYN(gfx, v_reg, x, y, n, memory, index):
    """
    DRW Vx, Vy, nibble: XOR de un sprite de 8xn en (Vx, Vy).
    - Wrap-around en bordes.
    - VF = 1 si hubo colisión (algún bit pasó de 1->0).
    """
    vx = v_reg[x] & 0xFF
    vy = v_reg[y] & 0xFF
    v_reg[0xF] = 0  # VF por defecto

    for row in range(n):
        sprite_byte = memory[(index + row) & 0x0FFF]
        py = (vy + row) % 32
        for col in range(8):
            if (sprite_byte & (0x80 >> col)) != 0:
                px = (vx + col) % 64
                if gfx[py][px] == 1:
                    v_reg[0xF] = 1
                gfx[py][px] ^= 1
    return gfx, v_reg


# -----------------------------------------------------------------------------
# E: Teclado 
# -----------------------------------------------------------------------------
def op_EX9E(pc, v_reg, x, chip8_keys):
    """SKP Vx: salta si la tecla Vx está presionada."""
    if chip8_keys[v_reg[x] & 0xF]:
        pc += 2
    return pc

# -----------------------------------------------------------------------------
def op_EXA1(pc, v_reg, x, chip8_keys):
    """SKNP Vx: salta si la tecla Vx NO está presionada."""
    if not chip8_keys[v_reg[x] & 0xF]:
        pc += 2
    return pc

# -----------------------------------------------------------------------------
def op_FX0A(v_reg, x, pressed_once):
    """
    LD Vx, K: espera una tecla y la guarda en Vx.
    Devuelve (v_reg, waiting) donde waiting=True si no hubo tecla (repetir opcode).
    """
    if pressed_once is None:
        return v_reg, True
    v_reg[x] = pressed_once & 0xF
    return v_reg, False

# -----------------------------------------------------------------------------
# F: Timers
# -----------------------------------------------------------------------------
def op_FX07(v_reg, x, delay_timer):
    """LD Vx, DT"""
    v_reg[x] = delay_timer & 0xFF
    return v_reg

# -----------------------------------------------------------------------------
def op_FX15(delay_timer, v_reg, x):
    """LD DT, Vx"""
    return v_reg[x] & 0xFF

# -----------------------------------------------------------------------------
def op_FX18(sound_timer, v_reg, x):
    """LD ST, Vx"""
    return v_reg[x] & 0xFF

# -----------------------------------------------------------------------------
# F: Índice/Memoria/Fuente
# -----------------------------------------------------------------------------
def op_FX1E(index, v_reg, x):
    """
    ADD I, Vx. Ajuste compatible: VF=1 si overflowea 0xFFF.
    """
    res = index + v_reg[x]
    vf = 1 if res > 0x0FFF else 0
    index = res & 0x0FFF
    return index, vf

# -----------------------------------------------------------------------------
def op_FX29(index, v_reg, x, FONT_DIR=0x50):
    """LD F, Vx: I = FONT_DIR + (Vx*5)"""
    return (FONT_DIR + (v_reg[x] & 0xF) * 5) & 0x0FFF

# -----------------------------------------------------------------------------
def op_FX33(memory, index, v_reg, x):
    """LD B, Vx: BCD de Vx en memory[I..I+2]"""
    val = v_reg[x] & 0xFF
    memory[index]     =  val // 100
    memory[index + 1] = (val // 10) % 10
    memory[index + 2] =  val % 10
    return memory

# -----------------------------------------------------------------------------
def op_FX55(memory, index, v_reg, x, increment_I=True):
    """LD [I], V0..Vx"""
    for i in range(x + 1):
        memory[index + i] = v_reg[i] & 0xFF
    if increment_I:
        index = (index + x + 1) & 0x0FFF
    return memory, index

# -----------------------------------------------------------------------------
def op_FX65(memory, index, v_reg, x, increment_I=True):
    """LD V0..Vx, [I]"""
    for i in range(x + 1):
        v_reg[i] = memory[index + i] & 0xFF
    if increment_I:
        index = (index + x + 1) & 0x0FFF
    return v_reg, index

