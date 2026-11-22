# `players/custom/` — los bots de los equipos

Cada equipo añade aquí **dos ficheros nuevos, con el mismo nombre**, y no toca
nada más:

```text
players/custom/
├── zorro.py      tu bot: una clase que hereda de Player
└── zorro.yaml    su alta: qué fichero y qué clase
```

`zorro.yaml`:

```yaml
players:
  - file: zorro.py
    class: Zorro
```

Todos los `.yaml` de esta carpeta se cargan, así que dos equipos que envían su
bot a la vez **nunca chocan** en el mismo fichero. Un `.py` sin su `.yaml` no se
carga nunca: quien revisa el pull request ve el código y su alta juntos.

Elige un nombre de fichero que no exista ya aquí y, dentro del bot, un
`get_name()` que no use nadie más. La guía completa está en el
[README](../../README.md#-crea-tu-propio-bot).
