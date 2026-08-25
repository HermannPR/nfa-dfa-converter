# Actividad integradora

Conversor de expresiones regulares a autómatas (regex → NFA → DFA) con exportación a DOT/PNG e interfaz gráfica en Tkinter.

## Qué hace

Pipeline completo de teoría de autómatas:

1. **`postfix.py`** — inserta la concatenación explícita (`.`), pasa la expresión a notación postfix (shunting-yard con precedencias `*` > `.` > `+`).
2. **`NFA.py`** — construye el NFA con la construcción de Thompson, lo exporta a DOT (`nfa_to_dot`) e incluye `simulate_nfa` para probar cadenas.
3. **`nfa_to_dfa.py`** — determiniza por subconjuntos (`nfa_2_dfa`, con estado trampa) y exporta el DFA a DOT (`dfa_to_dot`).
4. Graphviz (`dot`) convierte los `.dot` en PNG: `nfaa.png` y `dfa.png`.

`main.py` ejecuta el pipeline de forma no interactiva con la expresión de ejemplo `a*b+c`. `gui.py` ofrece la interfaz Tkinter: ingresa la expresión, genera ambos autómatas, los muestra con zoom y desplazamiento, modo oscuro, y permite simular cadenas sobre el NFA.

## Requisitos e instalación

```bash
pip install pillow pandas numpy
```

Además se requiere el binario `dot` de Graphviz disponible en el PATH (necesario para exportar los PNG).

## Ejecutar

Interfaz gráfica:

```bash
python gui.py
```

Línea de comandos (genera `nfaa.dot`/`nfaa.png` y `dfa.dot`/`dfa.png` con `a*b+c`):

```bash
python main.py
```

## Estructura

```
Actividad integradora/
├── main.py          # pipeline CLI (ejemplo a*b+c)
├── postfix.py       # concatenación explícita + infix → postfix
├── NFA.py           # Thompson NFA + nfa_to_dot + simulate_nfa
├── nfa_to_dfa.py    # determinización por subconjuntos + dfa_to_dot
├── gui.py           # GUI Tkinter (zoom, modo oscuro, simulación)
├── nfaa.dot / nfaa.png   # salidas del NFA
└── dfa.dot / dfa.png     # salidas del DFA
```

## Estado

Actividad integradora entregada (curso de autómatas); interfaz y comentarios en español.

## Screenshots

Visualizador de Autómatas (NFA/DFA) — GUI Tkinter con zoom, modo oscuro y simulación.

![Visualizador de Autómatas](docs/screenshot.png)
