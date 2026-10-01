# SeedCash Auditor

Cerebro privado de un auditor multiagente. Su único trabajo es revisar SeedCash (con SeedSigner como línea de base) y dejar por escrito el chequeo que falla, la clase de impacto, el archivo y la dirección del arreglo.

No modifica el árbol de SeedCash ni el de SeedSigner. No abre issues en GitHub hasta que tú confirmas el borrador concreto.

## Qué hay dentro

Los chequeos viven en `brain/invariants.md`. Cada skill y cada agente apuntan ahí; no repiten el fallo. `tools/lint_brain.py` rompe el build si esa regla se desalinea.

| Pieza | Para qué |
| --- | --- |
| `brain/` | Modelo de amenazas, arquitectura, invariantes, política de issues |
| `agents/` | Encargo de cada carril |
| `.grok/skills/` | Skills que Grok carga al trabajar en este repo |
| `.grok/workflows/` | Auditoría completa, reverificación y alta de issues |
| `tools/file_issue.py` | Borrador siempre; `gh` solo con confirmación |
| `checklists/release.md` | Orden antes de grabar una imagen |

Carriles: firma, CashTokens, canal QR, custodia de la semilla, lo que se ve contra lo que se firma, imagen del sistema, y el delta con SeedSigner.

## Árbol que se audita

La memoria del último árbol leído está en `brain/pin.md`. Un run nuevo hace `git rev-parse` sobre la ruta que le pases. Si el commit no coincide con el pin, el informe lo dice.

El checkout sucio de SeedSigner en `~/seedsigner-project/seedsigner` no es la línea de base. La etiqueta correcta está en el pin.

## Auditoría

Desde este directorio, en Grok:

```text
/audit-seedcash
```

Argumentos:

```json
{
  "auditor_root": "/Users/martialturorequena/Desktop/SeedCash_Auditor",
  "target_root": "/Users/martialturorequena/Desktop/images/image_2.0.2/org_2.0.2/seedcash",
  "os_root": "/Users/martialturorequena/Desktop/images/image_2.0.2/org_2.0.2/seedcash-os",
  "baseline_root": ""
}
```

`baseline_root` vacío significa que el carril del delta no abre un árbol de SeedSigner. Para comparar línea a línea, pasa un clon limpio de la etiqueta del pin.

La pasada corta, solo sobre las filas marcadas `open`:

```text
/reverify-corpus
```

Mismos `auditor_root`, `target_root` y `os_root`.

`/audit-seedcash` pone tres filtros detrás de los carriles. Están en `brain/review-layers.md`. Quote comprueba que la función sigue diciendo eso. Reach comprueba que el camino llega a una firma, a la semilla o al air gap. Impact tumba la clase de impacto cuando está inflada. Un hallazgo queda confirmado solo si los tres lo mantienen. Los que caen salen en la lista de eliminados, con la capa, el invariante y el motivo. Una pasada completa puede lanzar hasta unos 80 agentes: uno de orientación, siete carriles y, como mucho, 24 hallazgos por cada una de las tres capas.

Los flujos son de solo lectura sobre SeedCash. El informe lo escribe el propio flujo, campo a campo.

## Issues

Un hallazgo es un JSON con la forma de `schemas/finding.schema.json`. El ejemplo de la cadena de versión está en `examples/version-string.json` y es un hallazgo de la imagen: el filer lo rechaza contra el repo de la app hasta que pases `--repo` de la imagen.

Borrador, sin llamar a `gh issue create`:

```bash
python3 tools/file_issue.py --finding ruta/al/hallazgo.json
```

Publicar, solo después de leer ese borrador:

```bash
SEEDCASH_AUDITOR_CONFIRM=yes python3 tools/file_issue.py --finding ruta/al/hallazgo.json --confirm
```

El flujo `file-seedcash-issue` hace lo mismo y se detiene a pedir confirmación cuando `args.file` es `true`. Sin ese flag se queda en el borrador.

El repo de destino por defecto es el `issue_repo` de `brain/pin.md`.

## Comprobaciones de este repo

```bash
make test
```

Eso lintea el cerebro y corre los tests del filer. El filer de prueba no habla con GitHub.

## Privado

Aquí hay hipótesis de fallos que siguen abiertos en el pin. El remoto tiene que seguir siendo privado. `NOTICE.md` dice qué habría que quitar antes de un espejo público.
