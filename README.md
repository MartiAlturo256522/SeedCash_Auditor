# SeedCash Auditor

Cerebro público de un auditor multiagente. Su único trabajo es revisar SeedCash (con SeedSigner como línea de base) y dejar por escrito el chequeo que falla, la clase de impacto, el archivo y la dirección del arreglo.

No modifica el árbol de SeedCash ni el de SeedSigner. No abre issues en GitHub hasta que tú confirmas el borrador concreto.

## Qué hay dentro

Los chequeos viven en `brain/invariants.md`. Cada skill y cada agente apuntan ahí; no repiten el fallo. `tools/lint_brain.py` rompe el build si esa regla se desalinea.

| Pieza | Para qué |
| --- | --- |
| `brain/` | Modelo de amenazas, arquitectura, invariantes, política de issues |
| `agents/` | Encargo de cada carril |
| `.grok/skills/` | Skills que Grok carga al trabajar en este repo |
| `.grok/workflows/` | Auditoría, reverificación y el filtro largo antes de un issue |
| `tools/file_issue.py` | Un hallazgo: borrador siempre; `gh` solo con confirmación |
| `tools/publish_findings.py` | El lote: un issue por hallazgo listo, saltando los que ya están abiertos |
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

`/audit-seedcash` lee primero los títulos de los issues ya abiertos y cerrados. Luego lanza los siete carriles y diez perspectivas más: construcción de la transacción, génesis, NFT y fungibles de CashTokens, PSBT, el UR que sale del aparato, Python, la Pi Zero, el hardware y la experiencia acumulada de SeedSigner. Detrás van tres filtros: Quote, Reach e Impact. Un informe confirmado todavía no es un issue.

Los hechos de BCH están en `brain/bch.md`. Lo aprendido en SeedSigner, en `brain/seedsigner-lessons.md`. Las perspectivas, en `brain/perspectives.json`.

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

El redactor exporta candidatos. No los publica.

```bash
python3 tools/export_findings.py --out findings-out
python3 tools/list_issues.py --state all
```

Para crear issues hace falta el flujo `publish-seedcash-issues` con `args.publish` en `true` y `args.target_root` apuntando al árbol. Ese flujo vuelve a leer el código con ocho agentes distintos por hallazgo: Quote, Reach, Impact, BCH, el especialista del campo, la experiencia de SeedSigner, los issues anteriores y un agente que intenta tumbar el hallazgo. Como mucho entran cuatro hallazgos. Si sobreviven, se detiene y pide confirmación. Solo entonces escribe `cleared/` y llama a `gh`. Un candidato sin esos ocho sellos lo rechaza `tools/gates.py`. Un título que ya existe, abierto o cerrado, se salta.

La política está en `brain/issue-policy.md`.

## Comprobaciones de este repo

```bash
make test
```

Eso lintea el cerebro y corre los tests del filer. El filer de prueba no habla con GitHub.

## Público

El remoto es público porque así se pidió. Las hipótesis nombran el chequeo, la clase de impacto, el archivo y la dirección del arreglo. `NOTICE.md` es el aviso. No hay transacciones de disparo ni procedimientos de reproducción.
