# Emulador CHIP-8 en Python (Pygame)
<span><img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue"/></span>

Un intérprete/mini-emulador de **CHIP-8** escrito en Python, con renderizado por **Pygame** y enfoque didáctico.

## Captura de pantalla

<span><img src="https://github.com/VintaBytes/Lissajous/blob/main/imagen1.png?raw=true"  width="480px"/></span>

## ¿Qué es CHIP-8?

**CHIP-8** no es una máquina física, sino un **lenguaje interpretado** creado a mediados de los 70 (atribuido a Joseph Weisbecker en el entorno del RCA 1802) para facilitar la escritura de juegos en microcomputadoras como la **COSMAC VIP** y **Telmac 1800**. Su “máquina virtual” es muy compacta:

* **Pantalla**: 64×32 píxeles monocromo (blanco/negro).
* **Teclado**: 16 teclas hexadecimales (0x0–0xF).
* **Memoria**: 4 KiB (0x000–0xFFF), con programas iniciando a **0x200**.
* **Registros**: V0..VF (8-bit), **I** (12-bit), **PC** (program counter), temporizadores **DT/ST** a 60 Hz.
* **Instrucciones**: 2 bytes (16-bit) por opcode; dibujo por **XOR** con bandera de colisión en **VF**.

---

## Arquitectura del emulador

El proyecto está dividido en módulos **funcionales** (sin clases), para que sea fácil de leer, testear y extender.

* **`main.py`**
  Punto de entrada. Inicializa Pygame, carga la ROM, copia la fuente a memoria, mantiene el **bucle principal** (eventos, fetch/decode/dispatch), actualiza temporizadores y dibuja cuando corresponde.

* **`config.py`**
  Archivo único de configuración: tamaño de pantalla y **SCALE**, ruta de ROM, distribución de **teclado**, constantes de memoria (`MEM_SIZE`, `PROGRAM_START`, `FONT_DIR`), set de **quirks** (compatibilidad entre variantes), temporizaciones (**CPU\_HZ**, **TIMER\_HZ**) y **FONT\_SET** (sprites 0–F).

* **`chip8_funciones.py`**
  Utilidades “core” del intérprete:

  * `load_game` (lee binario de ROM),
  * `fetch_opcode` / `decode_opcode` (trae y descompone el opcode),
  * `process_input` (lee teclado mapeado a teclas CHIP-8),
  * `tick_timers` (decrementa **DT**/**ST** a 60 Hz),
  * `setup_graphics` / `draw_graphics` (abre ventana y pinta el framebuffer `gfx` con grilla opcional).

* **`chip8_instrucciones.py`**
  Implementación **funcional** de los opcodes (cada instrucción es una función pura que recibe y devuelve estado). Entre muchas, ya están:

  * Limpieza y salto: `00E0 (CLS)`, `1NNN (JP)`, `2NNN/00EE (CALL/RET)`, condiciones `3XNN/4XNN/5XY0/9XY0`, `BNNN`.
  * Registros y aritmética: `6XNN`, `7XNN`, y bloque `8XY0..8XYE` (OR/AND/XOR/ADD/SUB/SHL/SHR con **VF**).
  * Dibujo: `DXYN` (XOR + **colisión en VF**, con **wrap-around**).
  * Aleatorio: `CXNN` (con RNG inyectable para reproducibilidad).
  * Índice/memoria/temporizadores/teclado: `ANNN`, `FX07/15/18`, `FX1E/29/33/55/65`, `EX9E/EXA1`, `FX0A`.

> **Quirks configurables**:
>
> * `QUIRK_SHIFT_USES_VY` (shift sobre `Vy` o `Vx` en `8XY6/8XYE`)
> * `QUIRK_ADDI_SETS_VF` (si `FX1E` setea `VF` en overflow de `I`)
> * `FX_BULK_INC_I` (si `FX55/FX65` incrementan `I`)
> * `DXYN_WRAP` (dibujo con envolvente en bordes)
> * `RNG_SEED` (semilla para `CXNN`)

---

## Estado del proyecto

Este es un **proyecto experimental** con foco didáctico. La base de CHIP-8 está implementada y probada con ROMs de test, y la intención es **expandir** a **Super-CHIP-8** (SCHIP) próximamente:

**Roadmap a Super-CHIP-8**

* Modo alta resolución **128×64** (`00FF/00FE`).
* Scrolls de pantalla (`00CN`, `00FB`, `00FC`).
* Sprites extendidos (8×16), y ajustes de fuente.
* Optimizaciones de render (dirty rects), beep integrado y selector de ROM.

---

## Requisitos

* **Python** 3.10+
* **Pygame** 2.5+
* OS: Linux / macOS / Windows
* (Opcional) **Entorno virtual** (`venv`)

### Instalación rápida

```bash
# 1) Clonar el repo
git clone https://github.com/tuusuario/tu-repo-chip8.git
cd tu-repo-chip8

# 2) (opcional) crear entorno virtual
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3) Instalar dependencias
python -m pip install --upgrade pip
pip install pygame

# 4) Ejecutar
python main.py
```

> **Elegir ROM**: editá `config.py` y cambia `ROM_PATH` por la ROM que quieras usar.
> **Escala / FPS lógicos**: ajustá `SCALE`, `CPU_HZ` y `TIMER_HZ` en `config.py`.
> **Fuente**: el set `FONT_SET` se copia a memoria en `FONT_DIR` al iniciar.

### Mapeo de teclado (por defecto)

```
Chip-8:   1  2  3  C        PC:   1  2  3  4
          4  5  6  D              q  w  e  r
          7  8  9  E              a  s  d  f
          A  0  B  F              z  x  c  v
```

(El mapeo exacto se edita en `config.py` → `KEY_MAPPINGS`. Por ejemplo, `0x0` está en `X`, `0x1` en `1`, `0x2` en `2`, etc.)

---

## Estructura básica de memoria

* **`PROGRAM_START`** = `0x200`: dirección donde se carga la ROM.
* **`FONT_DIR`** = `0x50`: dirección donde se copia `FONT_SET` (sprites 0..F).
* **`MEM_SIZE`** = `0x1000` (4 KiB).

---

## Cómo está implementado el bucle principal (a grandes razgos)

En cada iteración:

1. Se procesan eventos de Pygame y el estado del teclado CHIP-8.
2. **Fetch**: se leen 2 bytes en `PC` → opcode de 16-bit.
3. **Decode**: se extraen `op`, `x`, `y`, `n`, `kk`, `nnn`.
4. **Dispatch**: se llama la función correspondiente (por ejemplo, `DXYN`, `6XNN`, etc.).
5. Se actualizan **DT/ST** a 60 Hz y se dibuja si hubo cambios.

---

## Contribuir

Se aceptan PRs y sugerencias: mejoras de compatibilidad, más ROMs de prueba, soporte SCHIP, refactors, etc.
Si encontrás un bug, por favor adjuntá ROM y pasos de reproducción.

Este proyecto se distribuye bajo la licencia MIT.
