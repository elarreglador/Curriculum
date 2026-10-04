# Información de la candidatura — ruit (RUIT COMPARATOR, S.L.)

> Documento de trabajo interno. No se envía a la empresa.
> Es la fuente de las cifras citadas en el CV y en la carta.

- **Fecha:** 2026-10-03
- **Puesto:** Senior Backend Engineer, Infrastructure
- **Link de la oferta:** https://es.linkedin.com/jobs/view/senior-backend-engineer-infrastructure-at-ruit-4472283267
- **Formulario de candidatura (el real):** https://tally.so/r/dWrgbN?via=reto — 6 páginas, ~10 minutos
- **Vacante hermana:** Senior Backend Engineer, Integrations (Python) · id 4472284210 · formulario https://tally.so/r/eq4zAE?via=reto

## Empresa

| Campo | Valor |
| --- | --- |
| Nombre comercial | ruit |
| Razón social | RUIT COMPARATOR, S.L. |
| CIF | B56766835 |
| Sector | Software B2B (SaaS de herramientas para negocios de segunda mano) |
| Fundación | No consta. El fundador sitúa el origen del producto en diciembre de 2023 |
| Tamaño (empleados) | 3 personas nombradas en la web oficial. Tracxn: 3 empleados |
| Sede | Lanzadera, Marina de Empresas, puerto de Valencia (València) |
| Producto o servicio principal | Plataforma de *crosslisting*: publicar y sincronizar inventario en Wallapop, Vinted, eBay, Shopify, WooCommerce, PrestaShop y TodoColección desde un solo panel |

- **Cifras verificables:** +3.000 negocios y +1M anuncios publicados (web oficial). Precios: Basic 9,99 €/mes, Premium 39 €/mes (antes 60 €), Premium Fundador 29 €/mes, Enterprise a medida. Financiación: «close to €1M» de Angels Capital, Decelera Ventures, Abac Capital y Successful Fund (declarado en la propia oferta); NextGenerationEU / ENISA en el pie de web. Tracxn registra una ronda Seed el 23/06/2026 con Decelera Ventures y totalkapital declarado 0 USD.
- **Cultura o valores:** declaración pública en la web — *customer obsession*, *ownership*, *excellence without ego*, *simplicity above all*, *radical honesty*, *first-principles thinking*. «Nobody is a specialist shut in one corner». Esse es el eje de la carta: *ownership* y *llegar a la causa*.
- **Mercado:** Wallapop es propiedad de Naver al 100 % desde 2025 (valoración ~600 M€). Vinted no cobra comisión al vendedor desde 2023. ruit vende la rentabilidad de cruzar varios marketplaces.

## Oferta

- **Puesto:** Senior Backend Engineer, Infrastructure (1 persona). Singleton: es la primera incorporación de backend más allá del fundador.
- **Responsabilidades (según el formulario de candidatura):**
  - Primeras semanas: integraciones, *crawling* y bugs de clientes de extremo a extremo, mientras se aprende cómo funciona ruit.
  - Primeros meses: PostgreSQL y Redis en servidores propios, PgBouncer, más *workers* web y de Celery según crece el tráfico, y monitorización que apunte a la causa.
  - Después: más tests end-to-end que reproducen tráfico grabado de marketplaces, e integraciones que detectan el cambio de una API no documentada y se reparan solas.
  - Transversal: integraciones, *crawling*, bugs de cliente, los clientes y frontend cuando hace falta. No hay puesto solo de DevOps.
- **Stack declarado:** Python con Django asíncrono, Celery, Redis y PostgreSQL en Docker. Observabilidad con Grafana, Loki, Tempo y OpenTelemetry. App web y móvil en Flutter/Dart, extensión de Chrome en TypeScript. Construcción íntegra con agentes de IA (Claude Code con agentes y subagentes).
- **Requisitos obligatorios:**
  - Python en producción, idealmente Django.
  - Haber llevado un sistema más allá de un único servidor y saber contar qué se rompió primero.
  - Monitorización montada y usada para encontrar la causa de un incidente.
  - Programar con agentes de IA a diario.
  - Inglés de trabajo.
  - Poder trabajar legalmente en España (no tramitan visados).
- **Deseables (implícitos en el texto):** integraciones mantenidas vivas cuando el otro lado cambia la API; reconstruir una API desde el tráfico de red de una app; conocimiento de Docker, PostgreSQL y Celery.
- **Condiciones:** presencial en Valencia, cinco días a la semana, en Lanzadera (Marina de Empresas). Salario en el percentil 75 del mercado, «la horquilla se comparte en la primera llamada». Unos 2.000 € al mes de presupuesto para agentes de IA, más presupuesto de formación, experimentos y servidores. Comida de los jueves y juegos de los viernes, a cargo de la empresa.
- **Proceso de selección:** formulario (6 páginas, ~10 min) → 45 min de valores y trayectoria por vídeo con Luis Grau (CEO) → 60 min técnicos por vídeo, sin programar, compartiendo pantalla y agentes → un día en Valencia con sesión de pizarra y comida con el equipo. Unas tres semanas en total; respuesta en 48 horas tras el día en Valencia.
- **Encaje con el perfil:**
  - *Python en producción e ir más allá de un servidor* → Covered: administración de servidores Linux en Living Properties y 20 años de trabajo con hardware y sistemas.
  - *Monitorización que encuentra la causa* → Covered: su rol de soporte técnico y negocio propio de diagnóstico, más el despliegue en Kubernetes con criterios de producción.
  - *Programar con agentes de IA* → Covered: es su forma de trabajar; y lo declaro en la carta y en el proyecto destacado.
  - *Django* → **No cubierto**: el CV base declara Python y Node.js, no Django. Se dice con todas sus letras en la carta.
  - *Celery, PgBouncer, Redis* → No declarados en el CV base.
  - *Ingeniería inversa de API desde tráfico de red* → No cubierto, aunque el equivalente más próximo es haber protocols Zigbee/MQTT.
  - *Inglés de trabajo* → **Riesgo conocido**: A2 sin certificado. No se oculta en la carta.

## Fuentes

| Dato | Fuente | Fecha |
| --- | --- | --- |
| Razón social, CIF, sede y equipo | https://ruit.es/en/about-us | 2026-10-03 |
| Producto, cifras de usuarios, precios | https://ruit.es/en · https://ruit.es/pricing | 2026-10-03 |
| Stack, responsabilidades y condiciones | https://tally.so/r/dWrgbN?via=reto (formulario de la vacante) | 2026-10-03 |
| Financiación, mercado y requisitos | Oferta LinkedIn id 4472283267 (hidratada) | 2026-10-03 |
| Ronda Seed 23/06/2026 y plantilla de 3 | Tracxn (agregador, dato no verificado en fuente primaria) | 2026-10-03 |
| Propiedad de Wallapop por Naver | https://www.catalannews.com/tech-science/item/south-korean-naver-buys-wallapop-app-6-august-2025 | 2026-10-03 |