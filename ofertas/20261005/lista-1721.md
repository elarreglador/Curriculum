# Ofertas por encaje — 2026-10-05 (perfil general: backend, cloud e IoT)

> Búsqueda interna. No se envía a ninguna empresa.
> Quinta búsqueda del ciclo. Las cuatro anteriores: `20261001/lista-1424.md` (general),
> `20261002/lista-1131.md` (general), `20261002/lista-1305.md` (firmware ESP32) y
> `20261003/lista-1055.md` (general). Esta repite el eje completo **con cinco pasadas**
> (tres locales, una nacional y una remota) e incorpora la de infraestructura como pasada
> propia, que el día 3 no se ejecutó.

## Criterios usados

- **Derivados de:** `sources/curriculum-base.md`
- **Términos:** `backend developer kubernetes iot` (local 1) · `devops platform engineer kubernetes linux` (local 2) · `iot zigbee mqtt domotica dispositivo` (local 3, `--minimo 20`) · `iot developer embedded python backend cloud` (nacional) · `backend python kubernetes iot` (remoto Europa)
- **Palabras clave:** iot, zigbee, embedded, embebido, firmware, kubernetes, docker, linux, devops, cloud, python, java, node, nodejs, node.js, javascript, mysql, rest, api, esp32, mqtt, node-red, raspberry, arduino, contenedores, infraestructura, backend, desarrollador, programador, m2m, sensores, automatizacion, domotica, electronica, redes, tcp, git
- **Descartes:** sap, salesforce, unity, unreal, cobol, mainframe, scrum master, product owner, call center, teleoperador, recruiter, comercial, account executive, .net, dotnet, c#, php, wordpress, shopify, rrhh, seleccion, marketing, ventas, frontend, front-end, disenador, ux, ui designer, qa, tester · (remota: + lemon.io, a.team, gig)
- **Banda de seniority:** `mid,senior` (las de nivel `principal`/`lead` se penalizan −15)
- **Geografía:** Valencia, Spain (`--ubicacion valencia,valencian`) · Spain sin filtro de ubicación · remoto filtrado por `spain,worldwide,europe,emea,united kingdom,netherland,ireland,portugal,remote`
- **Antigüedad máxima:** 21 días (45 en la pasada remota)
- **Parámetros:** `--paginas 2 --detalle 10` en las tres locales y la nacional; `--seniority mid,senior`; local 3 con `--minimo 20`; remota con `--minimo 40 --limite 40` (el subcomando `remoto` no acepta `--detalle`)

## Lista corta

Ordenada por encaje real, no por puntuación. **Tres de las cinco son empresas nuevas**
—Flywire, Fliinow y knowmad mood, ninguna aparecida en las cuatro listas anteriores—; una es
una vacante conocida que **hoy se hidrata por primera vez** (Mercadona) y una es una
repetición de la lista del día 3 (Siemens).

| # | Empresa | Puesto | Ubicación | Publicada | Encaje | Enlace |
|---|---|---|---|---|---|---|
| 1 | Flywire | Senior Data SRE / Cloud Platform Engineer | Valencia/València (híbrido semanal) | 2026-10-03 | 74 | https://es.linkedin.com/jobs/view/senior-data-sre-cloud-platform-engineer-at-flywire-4457375461 |
| 2 | Fliinow | Desarrollador Backend Senior – Java Springboot | Valencia/València (híbrido) | 2026-10-04 | 78 | https://es.linkedin.com/jobs/view/desarrollador-backend-senior-java-springboot-at-fliinow-4475379445 |
| 3 | knowmad mood | Ingeniero/a Software Java (100% teletrabajo) | Valencia (100 % remoto) | 2026-09-22 | 49 | https://es.linkedin.com/jobs/view/ingeniero-a-software-java-100%25-teletrabajo-at-knowmad-mood-4469058052 |
| 4 | Mercadona | Backend Developer Java Spring Boot | Albalat dels Sorells | 2026-09-23 | 54 | https://www.linkedin.com/jobs/view/4458882293 |
| 5 | Siemens (Sqills) | Backend Developer (m/f/d) Mobility Business | Valencia/València | 2026-10-02 | 54 | https://es.linkedin.com/jobs/view/backend-developer-m-f-d-mobility-business-at-siemens-4464157964 |

`Mercadona` es una **cuarta vacante** de Mercadona IT que las listas anteriores no habían
hidratado. Las otras tres son la de DevOps y la de Python-IA (ambas recomendadas en
`lista-1131.md`), y la de firmware BLE (descartada). Con la descripción de hoy se sabe que
**esta es la que baja el listón a un año**, y que acepta explícitamente el Ciclo en DAM.

## Detalle

### 1. Flywire — Senior Data SRE / Cloud Platform Engineer

- **Argumento:** es la lectura de su eje de CTO traducida al sector que mejor lo paga:
  **operar y hacer fiable la infraestructura que sostiene un servicio en producción**, en una
  empresa de pagos con 5.300 clientes y 1.400 empleados, y con el listón puesto en la
  conversación y no en el stack: el texto dice literalmente *«Based within a short commutable
  distance from Valencia, as this role requires regular weekly hybrid presence»*. Es decir, la
  empresa elige candidatos **por cercanía geográfica**, no la exige desde otra ciudad.
- **Qué cubre:** **Infrastructure as Code, CI/CD y fiabilidad de plataforma**, que es el
  contenido literal de «administré servidores Linux y optimicé entornos de ejecución para
  sostener un servicio continuo» · **contenedores y orquestación** (Docker, Fargate) ·
  **Kubernetes** (el CV lo declara; el matiz es que aquí es orquestación serverless con
  Fargate, y el suyo es un clúster propio) ·
  **Linux y scripting en Python o Bash** · **monitorización, alerting y reducción de MTTR**,
  que es la mitad de sus años como soporte técnico y como técnico Apple · **la
  infraestructura que da soporte a la plataforma de datos** (PostgreSQL, Kafka/PubSub) ·
  **SLIs, SLOs, RBAC y políticas de coste**: son políticas de operación, no de escritura de
  software · empresa de **cliente final** (`Sectores: Servicios financieros`), no consultora ·
  **plan de compra de acciones para empleados (ESPP)**.
- **Qué no cubre:** **«Deep Terraform Expertise: Master-level hands-on»** es el listón duro y
  el CV no declara Terraform ni IaC de ningún tipo: es la brecha más grande de la lista ·
  **5+ años en SRE/DevOps/Cloud Platform Engineering** a escala, con *
  *«proven experience building production cloud infrastructure at scale»* · **AWS y GCP como
  proveedores**, multi-cuenta y multi-proyecto: el CV declara K8s y Linux, no nubes ·
  **GitLab CI/CD** concreto · el puesto es **de datos** (el objeto es la plataforma de datos y
  AI, con Airflow, dbt y BigQuery), no de servicios de aplicación: es un giro de 30° dentro de
  su eje.
- **Verificar antes de postular:** publicada el 3, **2 días** · **salario: No consta** · el
  proceso incluye, según el texto, *«skills assessment»* además de entrevistas con el manager,
  los pares y el VP: es un proceso largo, y el *assessment* es donde un listón de Terraform
  master se nota · «hybrid presence» sin número de días declarados: **preguntarlo en el
  primer contacto**, porque es la condición que hace viable la candidatura.
- **Siguiente paso:** `nueva_candidatura.py "Flywire"`

### 2. Fliinow — Desarrollador Backend Senior – Java Springboot

- **Argumento:** producto propio en crecimiento, **equipo técnico pequeño, código a producción
  la misma semana**, y el CV tiene el recurso más escaso del mercado: **20 años de
  experiencia profesional real** con formación técnica. La lista del día 3 dejó como hallazgo
  que el listón de años es la barrera; aquí el texto es explícito en el lado contrario:
  *«No hace falta ser un experto»* en cloud, y *«Mínimo 3 años de experiencia profesional
  desarrollando con Java y Spring Boot»* es el listón declarado más bajo de toda la lista
  corta de hoy.
- **Qué cubre:** **Java 21 y Spring Boot 3.5**, que el CV declara como tecnología (aunque sin
  experiencia profesional documentada de framework, que es lo que hay que argumentar en la
  carta) ·
  **APIs REST de terceros, callbacks e IPNs, conciliación de estados, gestión de errores y
  reintentos**: es literalmente *«las que documentan mal y responden peor»*, que es lo que hizo
  en el dispositivo y el edificio · **Docker/Podman** · **GitHub Actions**,
  `conventional-commits`, `semantic-release` — su declarado *GitHub* y su trabajo de definir
  procesos y documentación técnica · **observabilidad y soporte en producción** (Sentry, logs,
  alertas): su eje de soporte técnico avanzado, ahora como backend · **PostgreSQL con
  modelado, SQL, migraciones y rendimiento de consultas** (el CV declara MySQL, que es el
  mismo oficio) · **tres entornos (dev, pre, producción)**: el mismo hábito de producción que
  el proyecto de Kubernetes del CV · **híbrido desde Valencia** y **contrato indefinido** ·
  sector **servicios financieros** (`Sectores`), cliente final.
- **Qué no cubre:** **titulación universitaria en Ingeniería Informática o Telecomunicaciones**:
  es requisito explícito y el CV tiene un **Ciclo Formativo de Grado Superior (DAM)**, no un
  grado. Es la brecha formal más dura de la lista, y es la que hay que decidir antes de
  escribir nada · **mínimo 3 años de Java/Spring Boot como experiencia profesional**, no como
  tecnología del CV · **Angular 19**: el puesto pide «aportar en el frontend Angular cuando la
  funcionalidad lo requiera», es participación menor pero declarada · **Testcontainers y WireMock**
  (valorado, no exigido) · **Google Cloud** como proveedor (el CV no declara proveedor de nube;
  la oferta dice que no hace falta ser experto, lo cual abre la puerta) · **inglés técnico de
  lectura** — con A2 es asumible, es lectura, no conversación.
- **Verificar antes de postular:** publicada el 4, **1 día**: la más fresca de todas las cuatro
  listas del ciclo · **salario: «Según valía y experiencia»**, o sea, **No consta** · es la
  única del día que **pregunta por el grado universitario**: la duda es si el DAM se acepta
  como equivalente, y eso solo se resuelve en la llamada o en el formulario.
- **Siguiente paso:** `nueva_candidatura.py "Fliinow"`

### 3. knowmad mood — Ingeniero/a Software Java (100% teletrabajo)

- **Argumento:** es la oferta que **elimina las dos barreras que el propio día 3 identificó como
  la puerta de entrada**: es **100 % teletrabajo desde Valencia** (geografía, la razón por la
  que la lista local se queda corta) y **no pide titulación en ningún sitio**. La prioridad la
  pone en lo que se demuestra —*«Experiencia sólida en Java, Spring Boot y microservicios»*—
  y no en un título. Contrato **indefinido**, **26 días de descanso**, y una compañía de
  3.000 personas con integración de talento: el precio de esa puerta abierta es que se
  trabaja por proyectos.
- **Qué cubre:** **Java, Spring Boot y microservicios** · **Java 17/21** (el CV declara Java;
  no el framework) · **bases de datos relacionales y no relacionales** (el CV declara MySQL) ·
  **entornos cloud AWS/Azure**, «valorable» (el CV tiene K8s y Linux, y eso es cloud en la
  práctica) · **colas: Kafka «preferible»** — el CV tiene MQTT, que es la alternativa ligera
  del mismo problema, y la carta puede decirlo así · **test unitarios y de integración**:
  el CV no lo declara, es la brecha real de esta · **metodología ágil** · **100 % remoto,
  indefinido, 26 días de descanso** (22 de vacaciones + 2 de libre disposición + 24 y 31 de
  diciembre), formación certificable con **Udemy Business** y **TechDays** —que es donde
  podría cubrir la brecha de framework sin coste.
- **Qué no cubre:** **es una consultora** (`Sectores: Servicios y consultoría de TI`), lo que
  la lista del día 3 marcó como el matiz que hay que aplicar criterio a criterio: aquí lo
  esperable es trabajar en el entorno de un cliente, no en un producto propio · **no declara
  años mínimos**, lo cual es una puerta, no un listón: es probable que el filtro real esté en
  la fase de criba, no en el texto · **Java con Spring Boot en producción**, que el CV
  declara como tecnología pero no como trayectoria · **testing**, que el CV no menciona en
  ninguna línea · el horario declarado es de oficina (8:30-18:00 L-V) con «modalidad
  100 % teletrabajo»: **en la práctica es remoto con horario de oficina**, conviene saberlo.
- **Verificar antes de postular:** publicada el 22, **13 días** · **probablemente abierta pero
  en el límite**: es la más antigua de la lista corta y conviene comprobarlo antes de escribir
  · **salario: No consta** · *«3.000 personas»* y *«transformación digital»* con planes de
  rotación entre proyectos: preguntar por la asignación concreta en la primera llamada.
- **Siguiente paso:** `nueva_candidatura.py "knowmad mood"`

### 4. Mercadona — Backend Developer Java Spring Boot

- **Argumento:** la cuarta de Mercadona IT y la que **baja el listón a un año**: *«Mínimo 1
  año desarrollando con Spring Boot»*. Es el requisito de experiencia más bajo de cualquier
  oferta del ciclo, y la vacante está en **Albalat dels Sorells, a 25 minutos de Valencia**.
- **Qué cubre:** **servicios web REST y microservicios con Spring Boot** · **APIs JSON-REST**,
  que es exactamente lo que declara el CV (APIs REST) · **JUnit, Mockito y Spring Test**:
  aquí sí se pide testing, a diferencia de knowmad mood · **MySQL, Oracle y PostgreSQL**: el
  CV declara MySQL, y es el mismo oficio con otro motor · **Docker y Kubernetes** y **Git**,
  declarados ambos · **arquitectura hexagonal y microservicios**, «valorable» · **patrones
  POO**, declarados en la formación DAM · formación aceptada: *«Grado en Informática /
  Telecomunicaciones **o Ciclo en DAM / DAW**»*: es una de las tres vacantes de Mercadona que
  nombran el DAM o aceptan cualquier ciclo formativo superior.
- **Qué no cubre:** **Spring Boot en producción**: el listón real es el framework, y el CV
  declara Java pero no el ecosistema Spring · **Kafka** («implementación de integraciones con
  Kafka») y **Jenkins** para CI/CD, que el CV no declara (tiene GitHub) · es la vacante de
  **backend puro**, sin cloud ni contenedores en el centro: el eje IoT del CV no aparece ·
  a 12 días, **probablemente cerrada o cerrándose**.
- **Verificar antes de postular:** publicada el 23, **12 días**, la más antigua de la lista
  corta · **salario declarado: 29.678 €-45.054 € brutos anuales según experiencia**, el único
  rango completo de backend del ciclo · es la tercera de las cuatro vacantes que aceptan
  ciclo formativo superior (la cuarta, la de BLE, exige grado de ingeniería y queda
  descartada): si se postulate a esta, conviene **nombrar las tres en la carta** y preguntar a
  qué puesto corresponde cada solicitud.
- **Siguiente paso:** `nueva_candidatura.py "Mercadona"` (misma carpeta: reutilizar o
  adaptar la que ya existe de `20261002`, si la hay)

### 5. Siemens (Sqills) — Backend Developer (m/f/d) Mobility Business

- **Argumento:** sin cambios respecto a la lista del día 3 (nº 1 entonces), y sigue siendo la
  mejor combinación de **cercanía geográfica** (desarrollo software en Valencia, sin filtro
  de titulación) y **backend crítico que toca el mundo real**: la venta y reserva de asientos
  de **Eurostar, Renfe y SNCF**. Repetida aquí solo porque la oferta sigue viva y porque la
  lista corta de hoy tiene huecos.
- **Qué cubre:** **Java y microservicios** de alto rendimiento · microservicios con **datos de
  pago** y endurecimiento de seguridad · **CI/CD propio del equipo** y *tooling* · **Terraform,
  Kubernetes e IaC** (parcial: el CV declara K8s, no Terraform) · **AWS** Lambda, DynamoDB,
  RDS, AmazonMQ, CloudWatch, ELB · monitorización en producción con OpenTelemetry, New Relic y
  PagerDuty · **refactor continuo, diseño de rendimiento y resiliencia** · híbrido declarado ·
  Sqills es la unidad de software de Siemens Mobility: cliente final.
- **Qué no cubre:** **Java de producción con Spring Boot y su ecosistema**: el equipo da por
  supuesto el framework, y es la misma brecha que en Fliinow y Mercadona, aquí con más
  recorrido de stack · **Kotlin y Go** como lenguajes secundarios del equipo · **Terraform /
  IaC**, que no aparece en el CV · **AWS como proveedor**, tampoco declarado.
- **Verificar antes de postular:** publicada el 2, **3 días** · **salario: No consta** · el
  filtro real de esta oferta es el idioma, no la antigüedad: *«Are you a match»* no pone años
  mínimos.
- **Siguiente paso:** `nueva_candidatura.py "Siemens"` · si se opta por una carta Java y otra
  de cloud (Flywire), conviene no escribirlas la misma semana.

## Marginales — con una condición que hay que aceptar antes de escribir nada

- **Fliinow — Desarrollador Backend Senior Java Springboot**: depende de cómo se interprete el
  grado universitario. Con una *«Titulación universitaria en Ingeniería Informática o
  Ingeniería de Telecomunicaciones»* explícita, el DAM es un *«Ciclo Formativo de Grado
  Superior»*: es un escalón real, pero es un listón que muchas empresas aceptan como
  equivalente cuando el candidato tiene 20 años de trayectoria profesional **si se dice y se
  argumenta**. Es la única del día que depende de una conversación y no de una tecnología que
  falte.
- **Logicalis Spain — Python Developer** (Madrid, 2026-09-21, encaje 54, **14 días,
  probablemente cerrada**). Teletrabajo, equipo de DevOps & Automation, **2+ años de Python en
  producción** (el listón más bajo de las ofertas Python del día), Kubernetes a nivel de
  usuario (`kubectl`, despliegues, logs), CI/CD, GitOps con Argo CD o Flux, pytest, Pydantic.
  Dos problemas: es **consultoría** (`Sectores: Servicios y consultoría de TI`) y pide **inglés
  técnico escrito**, que con A2 se sostiene, más 2 años de Python en producción que el CV no
  documenta como trayectoria profesional.
- **T-Systems Iberia — Lead Senior Backend Engineer (m/f/d)** (Granada, 2026-10-05, encaje 32).
  Es la vacante hermana del nº 2 del día 3, en `lead`: construir una plataforma backend
  multitenant para inferencia de IA (autenticación, metering, facturación, proxy), FastAPI. Tres
  cosas la dejan fuera: el nivel `lead` está fuera de la banda (`-15`); la sede es Granada, no
  Valencia; y el listón es de **5+ años de backend en producción a escala real** más
  *«Fluent in English (written and verbal)»*, y el texto pide **el CV en inglés**.
- **AgileEngine — GCP Cloud Engineer ID89421** (Valencia, 2026-10-02, encaje 74). Repetición del
  día 3: el `Sectores` es «Servicios y consultoría de TI» y el título lleva el número de
  referencia (`ID89421`), que es como AgileEngine etiqueta sus posiciones. El objeto es una
  **migración de AWS a GCP con Terraform, GKE, Helm y Azure DevOps**, con 4+ años de cloud
  engineering: el listón de proveedor de nube es justo lo que el CV no declara.
- **commercetools — Senior Search Backend Engineer** (Valencia, 2026-10-01, encaje 74). Ya
  evaluada como marginal en la lista del día 3. Sin cambios: **5+ años con JVM, Scala con
  programación funcional, ElasticSearch, MongoDB e IaC de búsqueda sobre Kubernetes con
  Terraform**. El ejemplo canónico de que la puntuación ordena y no decide.

## Descartadas

| Empresa | Puesto | Motivo |
|---|---|---|
| Joppy | Backend Engineer (Python) \| TOP AI Startup (Barcelona) | **Intermediaria**: el texto lo dice —*«One of the companies we work with at Joppy»*— y es la tercera vez que aparece en las listas del ciclo. Además **híbrido con 3 días/semana en Barcelona** y *«4+ years of hands-on backend engineering experience»*. |
| Rubiboo | Backend Engineer – remote Spain | **Intermediaria y sin cliente nombrado**: el texto es *«We're partnering with DeepMimic»*. El listón es de backend senior con async/typed Python y LLM, es decir, senior de producto. Salario declarado **40-45 k**, junto al de Mercadona BLE, los dos únicos datos de compensación de todo el ciclo. |
| Intellias | Senior Python Engineer (A2A Integration) (remoto España) | **Intermediaria** (`Sectores: Servicios de ingeniería y Servicios y consultoría de TI`) y cliente Fortune 500 no nombrado. El puesto es de **protocolo A2A y AWS AgentCore**, que es un listón de especialidad muy alto y muy reciente. Publicada hoy, lo cual es su único interés: es la señal de dónde va el mercado, no una candidatura. |
| Aircall | Senior Backend Software Engineer – Python (Madrid) | **7+ años** de backend engineering en la letra del texto, y *«Fluency in English is required»*. Ya estaba en la lista del día 3 con el mismo motivo; la hidratación confirma el 7+. |
| Deutsche Telekom | Senior / Principal DevOps Engineer, Industrial AI Cloud (Valencia) | **Duplicados de T-Systems**: T-Systems es la filial española de Deutsche Telekom, mismo programa, mismo cliente, mismo día. La vacante `lead` está en «Marginales»; la `principal` se penaliza fuera de banda. |
| modern>TALENT HUB | Administrador Sistemas \| Linux \| GCP \| Remoto España (Valencia) | Repetición del día 3: **10+ años** de administración de sistemas y una semana de guardia cada seis, en una plataforma que se define a sí misma como *«la plataforma de empleo»*: es una ETT de intermediación. |
| Prosodie-Ibérica | Administrador de sistemas Linux (Valencia) | Repetición del día 3: **descarte duro** por *«Titulación universitaria mínima en Telecomunicaciones, Informática o relacionado con IT»*, y el trabajo es la administración de sistemas de uno de sus principales clientes. Puntúa 74 solo por ubicación y fecha. |
| Capgemini Engineering | Senior Embedded Software Engineer \| Python · Software Engineer Python – Sistemas Embebidos (Madrid) | Las dos ya evaluadas (día 3, nº 5; y su hermana de listón `mid`). Sin novedad: B2 de inglés con reuniones, 2 días/semana en Madrid. **Contadas una sola vez.** |
| ruit | Senior Backend Engineer, Infrastructure · Integrations (Python) (Valencia) | Ya evaluadas en el día 3 (nº 3 y nº 5 de `lista-1131.md`), y la **candidatura ya está generada** en `output/20261003-ruit`. Sin cambios y sin nada que añadir: el trabajo que describen se parece al suyo, y el listón es inglés. |
| Maisa | Software Engineer (Backend) (Murcia, 100 % remoto) | Ya evaluada en el día 3 (nº 6). **3-7+ años de experiencia en ingeniería de software**, Go como lenguaje principal, Kafka y Redis. La brecha más grande de la lista del día 3 sigue siendo la misma hoy. |
| CloudLinux (TuxCare) | Python Software Engineer (remote work) (Madrid) | Ya evaluada en el día 3 (nº 4). Anuncio íntegramente en inglés, `Sectores: Organizaciones sin ánimo de lucro`. Sin cambios. |
| HURTADO & RIVAS SL (Axon / Rivas Robotics) | Programador/a de robots (Python / C++) (Picassent) | Ya descartada en `lista-1305.md` y `lista-1055.md`: 3 años en robótica, PyTorch, aprendizaje por refuerzo en simulación (Isaac Gym/Isaac Lab o MuJoCo), WebSocket, e inglés o chino. La brecha es de dominio, no de detalle. |
| Nextpower | Senior Embedded Software Developer (Linux) (Valencia) | Ya evaluada tres veces (1, 2 y 3 de octubre): **6-10 años** de embedded, *«Solid knowledge and experience modifying the Linux kernel»*, inglés y español **fluidos**. Sin cambios. |
| Mercadona | Firmware BLE Developer (Albalat dels Sorells) | Ya descartada dos veces: Nordic nRF52/53/54, Zephyr RTOS y BLE 5.4/PAWR, y **Grado en Ingeniería** (las otras tres vacantes de Mercadona sí aceptan ciclo formativo superior). Salario declarado 40.589-61.617 €: es, junto al 29.678-45.054 € de la vacante Java, el único dato de compensación del ciclo. |
| I3e IT Resources | Ingeniero de redes LAN/WAN/WIFI (Sagunto/Sagunt) | Repetición del día 3. **No es desarrollo**: 5 años de despliegue de red con BGP/OSPF/VLAN, balanceadores, y Cisco CCNP/CCNA como certificaciones deseadas. Encaja geográficamente y nada más. |
| Bcnvision group | Especialista en Automatización industrial (Paterna) | Repetición del día 3. **PLC**: Siemens S7-1200 y S7-1500 con TIA Portal, EPLAN y puesta en marcha de maquinaria. Su FP2 cubre el cableado y los cuadros —la mitad del puesto—, pero el PLC no aparece en el CV y es el núcleo del trabajo. |
| Airalo | Backend/PHP Engineer (Valencia) | **PHP**: la oferta es de otro lenguaje. |
| T-Systems Iberia | Senior DevOps Engineer for Industrial AI Cloud (Valencia) | Repetición del día 3 (nº 2 entonces, encaje 86, la más alta del ciclo). Sigue viva a 4 días y sin cambios. Pide **B2 de inglés**, que es el motivo por el que entonces quedó en la lista corta y no en primera posición. |

### Descartes automáticos (por filtrado de palabras o antigüedad)

Airalo (`Backend/PHP Engineer`: la oferta es de PHP), y las que quedaron por debajo del
umbral de puntuación en cada pasada (mínimo 30 en las locales 1 y 2, 20 en la de IoT, 30 en
la nacional, 40 en la remota). **El script no las enumera** —solo devuelve en el JSON lo que
pasa el filtro—, así que no se pueden listar aquí una a una: queda registrado el umbral con el
que se ejecutó cada pasada en la cabecera.

## Fuentes

| Dato | Fuente | Fecha |
|---|---|---|
| Ofertas locales, 3 pasadas (20 + 20 + 20 recogidas) | LinkedIn, endpoint público de invitado, `--geo "Valencia, Spain"` | 2026-10-05 |
| Ofertas nacionales (19 recogidas) | LinkedIn, endpoint público de invitado, `--geo "Spain"` | 2026-10-05 |
| Ofertas remotas Europa (15 recogidas, 0 en lista) | Remotive e Himalayas, vía `remoto`, filtrado por `--ubicacion` | 2026-10-05 |
| Descripciones completas | Hidratación `--detalle 10` de las tres pasadas locales y la nacional, más `detalle` explícito de los ids 4458882293, 4468123985, 4456166490 y 4428871243 | 2026-10-05 |
| Perfil y eje del candidato | `sources/curriculum-base.md` | 2026-10-05 |
| Listado de empresas ya candidatas | `output/` (wecity, grand-hotel-centenari, edicom, envira, octopus-energy, ruit) | 2026-10-05 |

**94 ofertas recogidas, 31 únicas** tras deduplicar entre pasadas: `Mercadona` ×3,
`T-Systems Iberia` ×2, `ruit` ×2, `Deutsche Telekom` ×2, `Capgemini Engineering` ×2.

### Notas sobre la fuente

- **La pasada de infraestructura local encontró una empresa que las cuatro búsquedas
  anteriores no habían visto: Flywire**, con el segundo día más fresco de todas las ofertas
  locales. El término `devops platform engineer kubernetes linux` con `--geo Valencia` es el
  que la produce; el día 3 no se ejecutó como pasada propia y esa es probablemente la razón.
  Lección operativa: **el eje de infraestructura es el que menos se agota**.
- **Las tres empresas nuevas de lista corta (Flywire, Fliinow, knowmad mood) no aparecen en
  ninguna de las cuatro listas anteriores.** Y las tres piden cosas que el CV no tiene y el CV
  no dice: **Terraform a nivel master** (Flywire), **3 años de Java/Spring Boot profesional**
  (Fliinow) y **testing** (knowmad mood, Mercadona). Lo que sí comparten las tres es que la
  empresa **no exige el idioma**: es un cambio frente al día 3, donde cuatro de las seis
  pedían inglés de trabajo. El único `Inglés técnico de lectura` es el de Fliinow.
- **La barrera del día ya no es solo el inglés: es la profundidad de stack, y hay tres
  muros concretos** — Terraform master, Spring Boot en producción y años de software
  profesional. knowmad mood es la única que no pone ninguno de los tres como número, y por
  eso es la que más merece una carta.
- **`Sectores` como detector de intermediaria, con el matiz del día 3 aplicado hoy.** Marca
  como «consultoría de TI» a T-Systems, AgileEngine, Prosodie, **knowmad mood** y Logicalis;
  marca «Servicios de ingeniería y consultoría de TI» a **Intellias**. Y en un caso el campo
  no dice nada pero el texto sí: **Rubiboo** (*«We're partnering with DeepMimic»*) y **Joppy**
  (*«One of the companies we work with at Joppy»*) son intermediarías con el `Sectores` limpio.
  **El texto es más fiable que el campo cuando el campo no está rellenado.**
- **La pasada remota Europa es la cuarta búsqueda consecutiva que sale vacía** (hoy, 15
  recogidas y 0 en lista; el 1 de octubre devolvió dos *gig* de baja calidad). Los descartes
  de hoy son *«Senior Independent Software Developer»*, *«Senior Independent
  AI Engineer / Architect»*, *«Senior back-end Engineer»*, *«Tier III Service Desk Engineer»* y
  *«Senior React Full-stack Developer»*: el nivel `senior` + `independent` no se casa con su
  trayectoria, y la lista es de *gig* y de *staffing* sin filtrar. Resultado legítimo, no un
  fallo.
- **Mercadona tiene cuatro vacantes y tres puertas distintas, y la que mejor encaja es la
  que se ha hidratado hoy.** Se confirma el hallazgo del día 3: *«Grado en Informática / Telecomunicaciones
  **o Ciclo en DAM / DAW**»* (Java Spring Boot) · *«Grado o Ciclo formativo superior en
  Informática / Telecomunicaciones»* (DevOps) · *«Grado en ingeniería Informática /
  Telecomunicaciones / Electrónica»* (Firmware BLE). Con la hidratación de hoy se sabe que la
  de Java Spring Boot —cuarta vacante, la única que no estaba aún leída— **baja el listón a
  un año**, el requisito de experiencia más bajo de cualquier oferta del ciclo, y es la
  única que publica su rango: **29.678 €-45.054 € brutos**.

### Hallazgo: el mercado local ha cambiado de sector, no de listón

Las cuatro búsquedas anteriores recorrieron el mismo eje. Lo que ha cambiado esta semana es
**quién contrata en Valencia**: aparecen una **empresa de pagos globales** (Flywire), una
**fintech de viajes con equipo propio** (Fliinow) y una **consultora de 3.000 personas con
teletrabajo** (knowmad mood), ninguna conocida. Sigue sin haber oferta de firmware ESP32 en
el mercado local —el único puesto de dispositivo en Valencia es el de Mercadona con Nordic y
Zephyr, ya descartado—, pero **la capa de operación de infraestructura se ha llenado de
gente nueva**.

La conclusión práctica no ha cambiado y es la que hay que llevarse a la carta: **el recorrido
completo ESP32 → Zigbee → MQTT → Node-RED → Kubernetes es lo que diferencia, y lo que hay que
enseñar es que cada peldaño se sostuvo solo**. Tres empresas nuevas contratan un backend o una
plataforma y piden el peldaño que el CV sí tiene (el de operación) más uno que no (el
framework o el proveedor de nube). **Cuando la brecha es de framework y no de criterio, la
candidatura se escribe; cuando la brecha es de años de profundidad en el stack, se sigue
buscando.** Fliinow y knowmad mood están en el primer caso; Flywire, en el segundo.