<div align="center">

# 🔴🟡 Conecta Cuatro

**Cuatro en línea en Python: juega contra personas o bots, enfrenta bots entre sí
y compite en una clasificación.**

[🌐 Jugar en el navegador](https://grabifv.github.io/CONECTA_CUATRO) ·
[📖 Documentación](docs/index.md) ·
[🤖 Crear un bot](#-crea-tu-propio-bot) ·
[🏆 Clasificación](results/leaderboard.json)

[![Tests](https://github.com/grabifv/CONECTA_CUATRO/actions/workflows/tests.yml/badge.svg)](https://github.com/grabifv/CONECTA_CUATRO/actions/workflows/tests.yml)
[![Torneo](https://github.com/grabifv/CONECTA_CUATRO/actions/workflows/tournament.yml/badge.svg)](https://github.com/grabifv/CONECTA_CUATRO/actions/workflows/tournament.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![Licencia MIT](https://img.shields.io/badge/licencia-MIT-green)](LICENSE)

</div>

```text
| . . . . . . . |
| . . . . . . . |
| . . . O . . . |      X = 🔴 empieza
| . . X X O . . |      O = 🟡
| . O X X X O . |
| O X O X X O . |      ¿dónde jugarías?
+---------------+
  1 2 3 4 5 6 7
```

## Índice

- [Qué puedes hacer](#-qué-puedes-hacer)
- [Empezar en 1 minuto](#-empezar-en-1-minuto)
- [El juego en la terminal](#-el-juego-en-la-terminal)
- [Los bots](#-los-bots)
- [Crea tu propio bot](#-crea-tu-propio-bot)
- [Torneos](#-torneos)
- [La web](#-la-web)
- [Cómo está organizado](#-cómo-está-organizado)
- [Desarrollo](#-desarrollo)

---

## ✨ Qué puedes hacer

| | Dónde | Qué |
|---|---|---|
| 👥 | terminal y web | **Persona contra persona** en el mismo ordenador |
| 🧑‍💻 | terminal y web | **Persona contra bot**, eligiendo el nivel |
| 🤖 | terminal y web | **Bot contra bot**, una o muchas partidas seguidas |
| 📊 | terminal | **Leaderboard** con victorias, derrotas y empates de cada persona y cada bot |
| 🏆 | GitHub Actions | **Torneo automático** entre todos los bots, con clasificación Elo |
| 🔍 | web | **Rayos X**: puntuación de cada columna y pistas mientras juegas |

Reglas: las fichas caen por la columna que eliges; gana quien alinee **cuatro**
en horizontal, vertical o diagonal; si el tablero se llena antes, es **empate**.
Más detalle e ideas de estrategia en [las reglas](docs/game/rules.md).

---

## 🚀 Empezar en 1 minuto

Solo necesitas **Python 3.10 o superior**.

```bash
git clone https://github.com/grabifv/CONECTA_CUATRO.git
cd CONECTA_CUATRO
python -m venv .venv
```

Activa el entorno:

| Windows | Linux / macOS |
|---|---|
| `.venv\Scripts\activate` | `source .venv/bin/activate` |

Instala y juega:

```bash
pip install -e .
conecta-cuatro
```

> ¿Sin instalar nada? Juega directamente en
> **[grabifv.github.io/CONECTA_CUATRO](https://grabifv.github.io/CONECTA_CUATRO)**.

---

## ⌨️ El juego en la terminal

`conecta-cuatro` (o `python -m conecta_cuatro`) abre este menú:

```text
===== CONECTA CUATRO =====
  1. Jugador vs Jugador
  2. Jugador vs Bot
  3. Bot vs Bot
  4. Ver leaderboard
  5. Salir
```

- Para jugar, escribe el **número de la columna** (1-7). Con `q` abandonas la
  partida, y las partidas abandonadas no cuentan.
- Al acabar una partida puedes pedir **revancha**; quien empieza se alterna.
- En **Bot vs Bot** eliges cuántas partidas se juegan y si quieres verlas
  jugada a jugada o solo el resultado final.

El **leaderboard** se guarda en `leaderboard_local.json` (no se sube a git: son
tus partidas) y se ordena por victorias:

```text
  #  Nombre                Tipo        V    D    E     % V
--------------------------------------------------------
  1  hard                  bot        12    1    2   80.0%
  2  Ana                   humano      5    3    1   55.6%
  3  medium                bot         4    6    3   30.8%
```

Personas y bots se cuentan por separado, así que una persona puede llamarse
igual que un bot sin mezclar sus resultados.

---

## 🤖 Los bots

Vienen cuatro, de menos a más fuerte:

| Bot | Cómo piensa | Tiempo por partida* |
|---|---|---|
| 🎲 **random** | elige una columna libre al azar | ~0 ms |
| 🌱 **easy** | mira una jugada: gana si puede, tapa si debe, si no juega al centro | ~4 ms |
| 🧠 **medium** | minimax a 4 jugadas con poda alfa-beta; valora tener fichas en el centro | ~20 ms |
| ⚔️ **hard** | minimax a 5 jugadas; cuenta las líneas de cuatro que siguen abiertas para cada jugador | ~300 ms |

<sub>* Medido en los servidores de GitHub durante el torneo.</sub>

Resultado del último torneo oficial (504 partidas, 0 descalificaciones):

```text
⚔️ hard   ≈ 1840 Elo   ████████████████████
🧠 medium ≈ 1735 Elo   ████████████████
🌱 easy   ≈ 1360 Elo   ███████
🎲 random ≈ 1065 Elo   █
```

Ninguno juega perfecto: **el primer puesto está libre** para el bot que lo
supere.

---

## 🛠️ Crea tu propio bot

¿Eres de otro equipo y quieres meter tu bot en el torneo? Sigue estos pasos.
Solo vas a **crear dos ficheros**; no tienes que tocar nada más del proyecto.

```text
players/custom/
├── zorro.py      tu bot: una clase con un método que elige la columna
└── zorro.yaml    su alta: dice qué fichero y qué clase cargar
```

> En los ejemplos el bot se llama **zorro**. Sustituye `zorro` / `Zorro` por el
> nombre de tu equipo en todo lo que copies.

### Paso 1 · Haz un fork y prepara tu copia

1. En GitHub, pulsa **Fork** (arriba a la derecha) para tener tu propia copia del
   repositorio.
2. Clona **tu** fork y crea una rama para tu bot:

   ```bash
   git clone https://github.com/TU_USUARIO/CONECTA_CUATRO.git
   cd CONECTA_CUATRO
   git switch -c bot-zorro
   ```

3. Crea el entorno e instala el proyecto con las herramientas de pruebas
   (en Windows, activa con `.venv\Scripts\activate`):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

### Paso 2 · Elige un nombre

Antes de escribir código, mira qué hay ya en
[`players/custom/`](players/custom/) y elige:

| Qué | Ejemplo | Regla |
|---|---|---|
| Nombre de los ficheros | `zorro.py`, `zorro.yaml` | minúsculas y `_`; que no existan ya |
| Nombre de la clase | `Zorro` | el mismo nombre en `CamelCase` |
| `get_name()` | `"zorro"` | **único** entre todos los bots |
| `get_icon()` | `"🦊"` | **un solo emoji**, que no use otro bot |

### Paso 3 · Escribe tu bot (`players/custom/zorro.py`)

Copia **una** de las dos plantillas.

<details open>
<summary><b>Plantilla A · Bot sencillo</b> (escribes tú la estrategia completa)</summary>

```python
"""Bot del equipo Zorro para Conecta Cuatro."""

from conecta_cuatro import game
from conecta_cuatro.player import Player


class Zorro(Player):
    """Gana si puede, tapa si debe y, si no, juega lo más al centro posible."""

    # ---- 1. Identidad: cambia estos cuatro datos ---------------------------

    @classmethod
    def get_name(cls) -> str:
        return "zorro"  # único entre todos los bots; minúsculas y guiones

    @classmethod
    def get_authors(cls) -> list[str]:
        return ["Ana García", "Luis Pérez"]  # los miembros del equipo

    @classmethod
    def get_description(cls) -> str:
        return "Gana si puede, tapa si debe y, si no, juega al centro."

    @classmethod
    def get_icon(cls) -> str:
        return "🦊"  # un solo emoji que no use otro bot

    # ---- 2. Estrategia: devuelve la columna donde jugar (empieza en 0) -----

    def choose_move(self, state: game.State) -> int:
        columnas = game.legal_moves(state)  # columnas con hueco
        yo = game.current_player(state)  # 1 o 2: tu ficha
        rival = game.other(yo)

        # a) Si alguna jugada gana ya, hazla.
        for c in columnas:
            if game.winner(game.apply_move(state, c)) == yo:
                return c

        # b) Si el rival ganaría jugando en c, tápala.
        #    (Se simula poniendo SU ficha: se le pasa el tablero como si fuera su turno.)
        for c in columnas:
            fila = game.landing_row(state, c)
            if fila is None:
                continue
            simulado = [list(f) for f in state]  # copia: nunca toques `state`
            simulado[fila][c] = rival
            if game.winner(simulado) == rival:
                return c

        # c) Si no, la columna más cercana al centro.
        centro = len(state[0]) // 2
        return min(columnas, key=lambda c: abs(c - centro))
```

</details>

<details>
<summary><b>Plantilla B · Bot con minimax</b> (la búsqueda ya está hecha; tú solo puntúas el tablero)</summary>

```python
"""Bot del equipo Búho: minimax con una evaluación propia."""

from conecta_cuatro import game
from conecta_cuatro.bots import MinimaxBot

#: Jugadas que mira hacia delante. Más = más fuerte, pero más lento:
#: tienes 2 segundos para TODA la partida (prueba 4-6).
PROFUNDIDAD = 4


class Buho(MinimaxBot):
    """Minimax con poda alfa-beta; solo hay que escribir `evaluate`."""

    @classmethod
    def get_name(cls) -> str:
        return "buho"

    @classmethod
    def get_authors(cls) -> list[str]:
        return ["Equipo Búho"]

    @classmethod
    def get_description(cls) -> str:
        return f"Minimax a {PROFUNDIDAD} jugadas; prefiere las fichas del centro."

    @classmethod
    def get_icon(cls) -> str:
        return "🦉"

    @classmethod
    def create(cls, seed: int) -> "Buho":
        return cls(depth=PROFUNDIDAD, seed=seed)

    def evaluate(self, state: game.State, player: int) -> float:
        """Lo bueno que es `state` para `player` (positivo = bueno).

        La búsqueda ya detecta sola las victorias y derrotas que ve; esto solo
        desempata el resto. Lee el tablero, no lo modifiques.
        """
        centro = len(state[0]) // 2
        puntos = 0.0
        for fila in state:
            for c, casilla in enumerate(fila):
                peso = len(state[0]) - abs(c - centro)  # más peso cerca del centro
                if casilla == player:
                    puntos += peso
                elif casilla != 0:
                    puntos -= peso
        return puntos
```

Si usas esta plantilla, el fichero se llama `buho.py` y la clase `Buho`:
cámbialos por los tuyos igual que en la A.

</details>

**Lo que tu bot recibe y debe devolver**

- `state` es el tablero: una lista de filas, de **arriba abajo**. Cada casilla
  vale `0` (vacía), `1` (🔴, empieza) o `2` (🟡).
- Tu ficha es `game.current_player(state)`.
- Devuelve un `int`: la **columna**, empezando en `0`, que no esté llena.
- **No modifiques `state`.** Para probar jugadas usa `game.apply_move(state, c)`,
  que devuelve un tablero nuevo.
- No des por hecho que el tablero mide 6×7: usa `len(state)` y `len(state[0])`.

Funciones útiles de `conecta_cuatro.game`:

| Función | Qué hace |
|---|---|
| `legal_moves(state)` | lista de columnas donde se puede jugar |
| `current_player(state)` | `1` o `2`: a quién le toca |
| `other(player)` | la ficha del rival |
| `apply_move(state, c)` | tablero nuevo tras jugar en `c` |
| `landing_row(state, c)` | fila donde caería la ficha (`None` si está llena) |
| `winner(state)` | `1`, `2` o `None` |
| `is_terminal(state)` | `True` si la partida ha terminado |
| `render(state)` | el tablero como texto, para depurar con `print` |

### Paso 4 · Dale de alta (`players/custom/zorro.yaml`)

Crea este fichero, **con el mismo nombre que tu bot**, junto a él:

```yaml
players:
  - file: zorro.py     # tu fichero .py
    class: Zorro       # tu clase
```

Sin este fichero tu bot no se carga. Como cada equipo tiene el suyo, varios
equipos pueden enviar a la vez **sin conflictos**.

### Paso 5 · Pruébalo en tu ordenador

```bash
pytest tests/test_custom_players.py
```

Comprueba tu bot en muchos tableros: que se carga, que sus jugadas son legales,
que no modifica el tablero y que acaba partidas contra `random`. Tiene que salir
todo en verde (`passed`).

```bash
conecta-cuatro-torneo --repetitions 1
```

Juega un torneo corto contra los bots del proyecto. Busca tu bot en la
clasificación: la columna `forfeits` tiene que ser **0**. Si no lo es, se ha
equivocado de columna, ha fallado o se ha pasado de tiempo.

```bash
ruff check players/custom
```

Revisa el estilo del código: es lo mismo que comprobará GitHub.

Y si quieres jugar tú contra él: `conecta-cuatro`, opción **2. Jugador vs Bot**.

### Paso 6 · Envíalo con un Pull Request

```bash
git add players/custom/zorro.py players/custom/zorro.yaml
git commit -m "Nuevo bot: zorro"
git push -u origin bot-zorro
```

En GitHub, en tu fork, pulsa **Compare & pull request** (hacia `main` de
`grabifv/CONECTA_CUATRO`). La descripción viene con una lista de comprobación:
rellénala.

GitHub probará tu bot automáticamente (check **Custom players**). Si sale en
rojo, abre el detalle, corrige, y haz `git push` de nuevo: el pull request se
actualiza solo. Cuando lo revisemos y lo aceptemos, tu bot aparece en la web y
entra en el siguiente torneo.

### Reglas del torneo

- ⏱️ **2 segundos para toda la partida**, no por jugada, medidos en los servidores
  de GitHub, que son más lentos que tu ordenador. Déjate margen.
- ❌ Una columna llena o inexistente, una excepción o pasarte de tiempo te hacen
  **perder esa partida**; el torneo sigue.
- 📦 Solo la biblioteca estándar de Python y `conecta_cuatro`: nada de `pip install`.
- 🔒 Nada de red, ficheros, subprocesos, `eval` ni `exec`. Se revisa el código y
  cualquier cosa sospechosa se rechaza.
- 📁 Solo tus dos ficheros en `players/custom/`; un pull request que toque otros
  ficheros no se acepta.

### Si algo falla

| Mensaje | Qué pasa | Solución |
|---|---|---|
| `already registered` | otro bot ya usa ese `get_name()` | elige otro nombre |
| `has no class 'Zorro'` | la `class` del `.yaml` no coincide con la del `.py` | escríbelas igual, con mayúsculas |
| `Player file not found` | el `file` del `.yaml` no coincide con el nombre del `.py` | revisa el nombre y la extensión |
| `could not be created` | falta alguno de los cuatro `get_...` | copia la plantilla completa |
| `illegal move` | has devuelto una columna llena o fuera del tablero | elige solo entre `game.legal_moves(state)` |
| `mutated the board` | has cambiado `state` | trabaja sobre `game.apply_move(...)` o una copia |
| `forfeits` > 0 por tiempo | tu bot piensa demasiado | baja la profundidad o simplifica |

¿Quieres saber más? La [API del jugador](docs/game/upload-a-bot/player-api.md)
explica todas las opciones, y la guía [enviar un jugador](docs/game/upload-a-bot/submit-a-player.md)
detalla la revisión.

---

## 🏆 Torneos

```bash
conecta-cuatro-torneo                            # todos contra todos, por puntos
conecta-cuatro-torneo --tournament league        # liga con Elo
conecta-cuatro-torneo --tournament championship  # grupos + eliminatorias
conecta-cuatro-torneo --opening 3,3 --opening '' # aperturas propias
conecta-cuatro-torneo --rows 7 --columns 8       # otro tamaño de tablero
```

- **Puntos:** victoria 3, empate 1, derrota 0. En el Elo, un empate cuenta como
  medio resultado para cada uno.
- **Partidas:** cada pareja juega desde tres aperturas (vacía, `3-3` y `0-6`),
  alternando quién empieza.
- **Seguridad:** cada partida corre en su propio proceso, así que un bot que se
  cuelga se corta y pierde, sin parar el torneo.
- **Automático:** en GitHub el torneo se repite en cada cambio de `main` y cada
  lunes, y propone la clasificación nueva en una Pull Request. Al fusionarla,
  la web se actualiza sola.

Todas las opciones: `conecta-cuatro-torneo --help` o la
[documentación del torneo](docs/game/advanced/tournament.md).

---

## 🌐 La web

La [web](https://grabifv.github.io/CONECTA_CUATRO) ejecuta **el mismo código
Python** que la terminal y el torneo, dentro del navegador gracias a
[Pyodide](https://pyodide.org). No hay servidor ni copia de las reglas en
JavaScript.

Tiene tablero de tamaño configurable, asientos para personas o cualquier bot,
rayos X, pistas, una línea de tiempo para repasar la partida, enlaces para
compartirla, cuadros de torneo propios y la clasificación oficial.

Para abrirla en local:

```bash
python scripts/build_web.py          # empaqueta el código Python en web/py.zip
python -m http.server -d web 8000    # http://localhost:8000
```

---

## 🗂️ Cómo está organizado

```text
CONECTA_CUATRO/
├── src/conecta_cuatro/
│   ├── game.py          reglas: tablero, jugadas, ganador, empate
│   ├── player.py        la clase Player que implementa cada bot
│   ├── cli.py           el juego en la terminal y su leaderboard
│   ├── tournament.py    torneos, tiempos y descalificaciones
│   ├── manifest.py      carga los bots desde los .yaml de players/
│   ├── elo.py           cálculo del Elo
│   └── bots/            estrategias reutilizables (minimax, greedy, random)
├── players/
│   ├── builtin/         random, easy, medium, hard
│   └── custom/          ← aquí van los bots nuevos
├── web/                 la página (HTML + JS + puente a Python)
├── results/             clasificación oficial del torneo
├── docs/                documentación en español e inglés (MkDocs)
└── tests/               pruebas automáticas
```

---

## 🧪 Desarrollo

```bash
pip install -e ".[dev]"     # herramientas de desarrollo
pytest                      # pruebas
ruff check .                # estilo
mypy                        # tipos
```

Cada push y cada Pull Request pasan por GitHub Actions: pruebas en Python 3.10,
3.12 y 3.14, comprobación de los bots enviados, compilación de la documentación
y publicación de la web.

Para ver la documentación en local:

```bash
pip install -e ".[docs]"
mkdocs serve                # http://127.0.0.1:8000
```

---

<div align="center">

Hecho por [grabifv](https://github.com/grabifv) · [Licencia MIT](LICENSE)

</div>
