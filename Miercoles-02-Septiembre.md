# Misiones: patrones de software para aplicaciones web

---

## Misión 1 — El portal no es un patrón

| Problema del relato | Capa | Patrón propuesto | Vecino rechazado y justificación | Cuándo NO aplicaría |
| :--- | :--- | :--- | :--- | :--- |
| **1. Código repetido en 40 archivos:** Verificación de sesión, bitácora y encabezado HTML duplicados en cada trámite suelto. | Políticas transversales | **Intercepting Filter** (Pipeline / Cadena de Middlewares) | Rechazado: **Front Controller**. El Front Controller solo centraliza el ruteo de peticiones hacia una acción; el Intercepting Filter es el que procesa de forma encadenada y reutilizable las validaciones previas y posteriores sin acoplar el código al destino. | En micro-scripts de consola o herramientas CLI aisladas que no gestionan peticiones HTTP ni ciclos de sesión web. |
| **2. Switch de bancos y choque de vocabulario:** 200 líneas de condicionales con códigos bancarios ajenos (00/01) frente a reglas internas. | Integración / Dominio | **Strategy** + **Adapter** | Rechazado: **Facade**. Facade simplifica una interfaz compleja propia sin alterar su contrato; Adapter traduce una interfaz externa incompatible al lenguaje del dominio, mientras que Strategy permite intercambiar el banco en tiempo de ejecución sin tocar el cliente. | Si la institución operara con una única pasarela de pagos estandarizada (un único SDK) que no requiera homologación de múltiples contratos. |
| **3. Consultas SQL acopladas a la vista:** Kardex y constancias duplican queries directas en el HTML para armar calificaciones. | Datos | **Repository** (apoyado en Data Mapper) | Rechazado: **Active Record** o **Table Gateway**. Estos atan la estructura física de la tabla a la clase; Repository abstrae la persistencia simulando una colección en memoria del historial académico, aislando por completo el SQL de la presentación. | En consultas analíticas ad-hoc de solo lectura o migraciones de base de datos donde mapear entidades de dominio agregue sobrecarga innecesaria. |
| **4. Efectos colaterales y doble cargo:** Caída del correo cancela el alta de materias y el doble clic genera cobros duplicados. | Aplicación / Dominio | **Unit of Work** (Transacción) + **Domain Events** (asíncronos) + **Idempotency Key** | Rechazado: **Observer síncrono**. El Observer tradicional corre en el mismo hilo de ejecución; si el observador de correo falla, revienta la transacción principal. Domain Events desacoplan el correo a una cola, y Unit of Work asegura atomicidad local (pago + alta). | En operaciones puramente de consulta (lectura) o sistemas sin requerimientos de consistencia inmediata en transacciones financieras. |
| **5. App móvil hace 12 peticiones y kiosco pide HTML:** Requerimientos de formato y volumen de datos dispares para el mismo trámite. | Presentación | **Backend for Frontend (BFF)** (API Gateway con agregación) | Rechazado: **Decorator** / **View Component**. Un Decorator altera la presentación de un objeto en memoria, pero no resuelve la sobrecarga de red (*chatty I/O*) ni reduce las 12 llamadas remotas del cliente móvil. | Si todos los clientes compartieran el mismo factor de forma, pantalla, canal de red y estructura de datos idéntica. |
| **6. Bloqueo por caídas externas:** Servicios caídos de CURP y banco congelan trámites no relacionados (kardex). | Integración | **Circuit Breaker** (con Timeout y Fallback) | Rechazado: **Retry** (Reintento automático). Reintentar de forma inmediata sobre un servicio caído satura el pool de conexiones del servidor y empeora la latencia global; Circuit Breaker interrumpe las llamadas fallidas de golpe para no degradar el portal. | En llamadas síncronas locales en memoria o dependencias estrictamente esenciales donde sin respuesta sea técnicamente imposible operar. |

---

## Misión 2 — Una petición, varios patrones: Flujo de «Pagar Inscripción»

A continuación se detalla el ciclo de vida de la petición HTTP (`POST /pagos/inscripcion`) estructurado cronológicamente a través de los componentes del marco web:

[Navegador / App Móvil]
│  (POST /pagos/inscripcion + Idempotency-Key)
▼

[Router Central] ─────────────────── Patrón: Front Controller
│

[Cadena de Middlewares] ──────────── Patrón: Intercepting Filter (+ Idempotency Guard)
│

[PagoInscripcionController] ──────── Patrón: Adapter / Data Transfer Object (DTO)
│

[InscripcionApplicationService] ──── Patrón: Facade / Service Layer
│

[PaymentStrategy + Adapter] ──────── Patrón: Strategy + Adapter (+ Circuit Breaker)
│

[Modelo de Dominio / ORM] ────────── Patrón: Unit of Work + Repository
│

[Bus de Eventos / Cola] ──────────── Patrón: Domain Events (Publish-Subscribe asíncrono)
▼
[Respuesta HTTP 200 OK al estudiante]


### 1. Recepción y Ruteo
* **Componente del marco:** Enrutador central (`web.php` en Laravel, `DispatcherServlet` en Spring, o `Router` en Express).
* **Patrón aplicado:** **Front Controller**.
* **Función:** Actúa como punto único de entrada para todas las solicitudes web. Centraliza la captura de la petición HTTP, evalúa la URI y delega la ejecución al controlador correspondiente, eliminando los archivos `.php` o scripts sueltos.

### 2. Filtros de Seguridad y Control de Duplicados
* **Componente del marco:** Pipeline de Middlewares / Filtros HTTP.
* **Patrón aplicado:** **Intercepting Filter** + **Idempotency Guard**.
* **Función:** Intercepta la petición antes de que toque la lógica de negocio. Valida que exista una sesión activa válida e inspecciona el encabezado `Idempotency-Key` enviado por el cliente. Si el alumno hizo doble clic, el filtro detecta que la primera solicitud sigue en proceso o ya fue procesada, bloqueando el cobro duplicado de inmediato.

### 3. Adaptador de Entrada y Enlace de Datos
* **Componente del marco:** `PagoInscripcionController`.
* **Patrón aplicado:** **Adapter** (adaptador de transporte HTTP a dominio) y **Data Transfer Object (DTO)**.
* **Función:** Extrae el cuerpo de la petición (JSON/Form-Data), valida los tipos de datos primarios y transforma los parámetros web en un comando fuertemente tipado (`PagarInscripcionCommand`) comprensible para la capa de aplicación.

### 4. Orquestación del Caso de Uso
* **Componente del marco:** `InscripcionApplicationService` o `PagarInscripcionUseCase`.
* **Patrón aplicado:** **Service Layer** / **Facade** (a nivel de aplicación).
* **Función:** Coordina las operaciones del caso de uso sin implementar lógica bancaria directa ni consultas a bajo nivel: recupera la información del estudiante, invoca la pasarela de pago seleccionada y asegura la coherencia del proceso global.

### 5. Integración con la Pasarela Bancaria
* **Componente del marco:** `PaymentStrategyResolver` que instancia el adaptador bancario concreto (`SpeiAdapter`, `TarjetaAdapter`, etc.).
* **Patrón aplicado:** **Strategy** + **Adapter** + **Circuit Breaker**.
* **Función:** **Strategy** selecciona la vía de pago solicitada; **Adapter** traduce la terminología interna al protocolo externo y homologa los códigos de respuesta (`00/01` del banco al estado interno `Acreditado`). Si la llamada remota al banco supera el umbral de tiempo o falla sistemáticamente, el **Circuit Breaker** interrumpe la conexión inmediatamente para evitar el colapso de hilos del servidor.

### 6. Persistencia Transaccional Atómica
* **Componente del marco:** `InscripcionRepository`, `PagoRepository` y el Administrador de Transacciones del ORM (Unit of Work).
* **Patrón aplicado:** **Unit of Work** + **Repository**.
* **Función:** Abre una transacción atómica de base de datos (`BEGIN TRANSACTION`). El repositorio actualiza el estado del pago a acreditado y efectúa el alta formal de las materias. Si la base de datos presenta algún fallo en cualquiera de las entidades, la transacción aplica un `ROLLBACK` completo, garantizando que no existan cobros registrados sin materias asignadas.

### 7. Desacople Asíncrono de Notificaciones
* **Componente del marco:** Event Dispatcher conectado a un broker de mensajería o cola de trabajos (Redis, RabbitMQ o colas integradas del marco).
* **Patrón aplicado:** **Domain Events** / **Publish-Subscribe** (asíncrono).
* **Función:** Tras confirmar el `COMMIT` en la base de datos, se publica el evento `PagoInscripcionAcreditado`. Un proceso en segundo plano (worker) consume el evento para enviar el correo de confirmación al alumno y notificar a caja. Si el servicio de correo se cae, la transacción de alta y cobro permanece intacta y el mensaje simplemente se reintenta en la cola.