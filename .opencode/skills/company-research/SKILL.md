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

## Reglas de verificación

- Preferir el dominio oficial y la memoria anual del año en curso frente a directorios.
- No invertir cifras de ingresos sin indicar año y fuente: los datasets públicos van atrasados.
- Wikidata es un punto de partida, no una fuente primaria. Contrastar antes de citar en un CV.
- Un resultado de `identity` no vacío no garantiza que sea la empresa correcta: comprobar
  descripción y país antes de construir nada sobre él.
