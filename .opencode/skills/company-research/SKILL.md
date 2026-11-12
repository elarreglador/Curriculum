# company-research

Skill de investigación de empresas. Recupera datos estructurados verificables desde fuentes
públicas y prepara las consultas que el agente debe resolver con sus herramientas web.

## Principio de diseño

El script cubre **solo lo estructurado y determinista** (identidad legal, sede, empleados,
ingresos, cotización, registro mercantil). Todo lo **narrativo y volátil** (noticias, cultura,
reputación, productos actuales) se resuelve con las herramientas web nativas del agente.

Motivo: los buscadores HTML sin clave (DuckDuckGo, Bing) responden hoy con páginas de
detección de bots. Reimplementar scraping frágil dentro del script sería frágil de verdad.

## Comandos

```bash
S=.opencode/skills/company-research/scripts/company_research.py

python3 $S "Inditex"                              # informe completo
python3 $S "Inditex" --ticker ITX.MC             # con mercado (tickerbursatil)
python3 $S "Apple" --section identity             # solo resolución de entidad
python3 $S "Inditex" --section profile            # ficha de Wikidata + resumen Wikipedia
python3 $S "Inditex" --section financials --ticker ITX.MC
python3 $S "Telefonica" --section registry        # registro mercantil
python3 $S "Inditex" --format json                # salida JSON estructurada
python3 $S "Inditex" --lang en                    # etiquetas en inglés
python3 $S "Inditex" --no-cache                   # ignora la caché
```

Secciones: `identity`, `profile`, `financials`, `registry`, `all`.

## Fuentes (todas sin clave salvo indicación)

| Sección | Fuente | Qué aporta |
|---|---|---|
| identity, profile | Wikidata | nombre legal, sede, país, fundación, empleados, forma jurídica, CEO, filiales, ingresos |
| profile | Wikipedia REST | resumen en prosa |
| financials | Yahoo Finance | ticker, bolsa, moneda, último cierre, capitalización, márgenes |
| registry | OpenCorporates | número de registro, constitución, estado (`OPENCORPORATES_API_KEY` opcional) |
| registry | SEC EDGAR | CIK y ticker para empresas de EE. UU. |

## Flujo del agente (ReAct)

1. **Normalizar.** Ejecutar `--section identity`. Si no devuelve entidad, la empresa no está
   en Wikidata: preguntar al usuario por el país o el nombre legal completo antes de seguir.
   Si hay varias candidatas, `--format json` incluye las alternativas en `identity`.
2. **Clasificar intención.** Mapear la pregunta del usuario a una sección:

   | Pregunta | Sección |
   |---|---|
   | ¿A qué se dedica? ¿Dónde? ¿Cuántos empleados? | `profile` |
   | ¿Cotiza? ¿Capitalización? ¿Ingresos? | `financials` |
   | ¿Quién es el CEO? ¿Qué filiales tiene? | `profile` |
   | ¿Existe legalmente? ¿Sede social? | `registry` |
   | ¿Noticias, cultura, productos, opinión? | ninguna: usar web |

3. **Recuperar.** Ejecutar el script con la sección correspondiente.
4. **Completar con web.** El script emite `consultas_pendientes` (claves `web`, `news`,
   `reputation`, `presence`). Resolverlas con `websearch` y `webfetch`, priorizando el dominio
   oficial que devuelve `Web oficial` en el perfil.
5. **Sintetizar.** Redactar con fuentes citadas. Si un dato no aparece en ninguna fuente,
   decirlo explícitamente en lugar de estimarlo.

   5.1 **Actualizar el registro de empresas.** Tras sintetizar, generar o actualizar la
   entrada de la empresa en `ofertas/empresas.json` (relativo a la raíz del proyecto)
   usando el helper `scripts/empresas.py`. El bloque `empresa_registro` del JSON de salida
   del script es un borrador: revíselo y complétalo antes de guardarlo (en especial
   `ubicacion` a nivel de provincia, `actividad`, `url_empleo` y las ofertas vistas si
   se ha revisado la web de empleo de la empresa).

    Al completar el borrador, **busca activamente la URL de empleo** (`url_empleo`)
    en la web oficial (sección careers/empleo/trabaja con nosotros) usando
    `webfetch` sobre `web`. Si la encuentras, anota también `ultima_revision` y
    `ultimas_ofertas_vistas` (lista de ofertas visibles, o `[]` si no hay). Si no
    la encuentras, deja `url_empleo` como `null` y anota `ultima_revision = hoy`
    (primer intento, queda pendiente). Si ya tenía `ultima_revision` (segundo
    intento fallido), elimina la empresa del registro (`empresas.py eliminar`).

   ```bash
   S=.opencode/skills/company-research/scripts
   python3 $S/empresas.py upsert --stdin <<'JSON'
   {
     "nombre": "...",
     "ubicacion": "...",
     "actividad": "...",
     "web": "...",
     "url_empleo": "...",
     "ultima_revision": "YYYY-MM-DD",
     "ultimas_ofertas_vistas": [
       {"titulo": "...", "url": "...", "ubicacion": "...", "publicada": "YYYY-MM-DD"}
     ],
     "fuentes": ["https://..."]
   }
   JSON
   ```

   Reglas del registro:
   - **Upsert por slug**: si la empresa ya existe, solo se sobrescriben los campos
     presentes y no vacíos; no se borra información previa.
   - `ultima_revision` es la fecha en que se revisaron las ofertas de empleo de la
     empresa. Solo actualízala si se revisó su web de empleo; en caso contrario,
     omítela para conservar la anterior.
   - `ultimas_ofertas_vistas` se reemplaza solo si se pasa la lista (puede ser `[]`
     si la revisión no encontró ofertas).
   - Un dato que no se pueda verificar se deja como `null` y se anota como
     `No consta` en el informe, nunca estimado.
   - Si `ofertas/` no existe, el helper la crea. El directorio ya está ignorado por git.
- `eliminar` borra el registro por nombre o slug. Con la política actual, una
  empresa sin `url_empleo` se elimina solo tras dos intentos fallidos (o si el
  usuario lo pide explícitamente).

## Caché

Ficheros JSON en `cache/`, TTL por `CACHE_TTL_HOURS` (24 h por defecto). Los datos
estructurados son estables; las noticias no se cachean porque no pasan por el script.

## Configuración

```bash
cp .opencode/skills/company-research/.env.example .env
```

| Variable | Obligatoria | Efecto |
|---|---|---|
| `OPENCORPORATES_API_KEY` | No | Levanta el límite de peticiones del registro mercantil |
| `CACHE_TTL_HOURS` | No | Vigencia de la caché (24) |

## Registro de empresas (`ofertas/empresas.json`)

Fichero JSON (lista de registros) con la información de las empresas investigadas,
usado como libreta de contactos/empleo. Se gestiona con `scripts/empresas.py`.

Campos de cada registro:

| Campo | Tipo | Descripción |
|---|---|---|
| `slug` | string | Clave de deduplicación (generada del nombre) |
| `nombre` | string | Nombre de la empresa |
| `ubicacion` | string | Provincia / sede principal |
| `actividad` | string | A qué se dedica la empresa |
| `web` | string | Web oficial |
| `url_empleo` | string | URL donde publican ofertas |
| `ultima_revision` | string (ISO) | Fecha de la última revisión de ofertas de empleo |
| `ultimas_ofertas_vistas` | array | Ofertas vistas en la última revisión (`titulo`, `url`, `ubicacion`, `publicada`) |
| `actualizado_en` | string (ISO) | Cuándo se tocó el registro |
| `fuentes` | array | URLs usadas para verificar los datos |

Comandos del helper:

```bash
E=.opencode/skills/company-research/scripts/empresas.py
python3 $E listar                       # JSON completo
python3 $E listar --formato tabla       # resumen
python3 $E mostrar "Inditex"            # un registro
python3 $E upsert --stdin               # añadir/actualizar (JSON por stdin)
python3 $E eliminar "Inditex"           # eliminar un registro (por nombre o slug)
python3 $E pendientes --limite 3        # empresas sin url_empleo (pendientes de investigacion)
```

## Reglas de verificación

- Preferir el dominio oficial y la memoria anual del año en curso frente a directorios.
- No invertir cifras de ingresos sin indicar año y fuente: los datasets públicos van atrasados.
- Wikidata es un punto de partida, no una fuente primaria. Contrastar antes de citar en un CV.
- Un resultado de `identity` no vacío no garantiza que sea la empresa correcta: comprobar
  descripción y país antes de construir nada sobre él.
