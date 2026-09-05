# Análisis de `cinerex_django`

## Alcance y conclusión

Auditoría estática de los archivos disponibles: configuración Django, URLs, vistas, tag de template, templates, SQL y documentación. No se modificó el proyecto ni se pudo validar contra una instancia real de Django/MySQL o los servicios externos.

**Conclusión:** el proyecto no es apto para producción. Tiene autenticación falsificable, inyección de código SQL en los flujos principales, ausencia de protección contra solicitudes falsas, exposición de una operación administrativa, datos sin integridad y una compra vulnerable a fraude y operaciones simultáneas.

## Resumen de problemas

Los problemas más importantes son de seguridad y consistencia de datos: el login se puede falsificar, casi todas las consultas usan SQL concatenado, la compra no exige autenticación ni valida el asiento, y faltan CSRF, hash de contraseñas y permisos administrativos. Además, una venta puede quedar incompleta o duplicarse porque no existe una transacción; el esquema SQL no tiene relaciones ni restricciones suficientes. La configuración contiene secretos, `DEBUG=True` y hosts abiertos. La documentación describe otro dominio y faltan modelos, migraciones, formularios y pruebas.

## Patrón de diseño identificado

El proyecto sigue parcialmente el patrón **MVT (Model-View-Template)** propio de Django: las vistas reciben la petición y renderizan templates. Sin embargo, no hay una capa Model de Django ni separación clara de servicios; las vistas ejecutan SQL y llamadas HTTP directamente. El tag `sql_cine` intenta encapsular la consulta de asientos, pero no constituye un patrón sólido y además introduce riesgos de inyección y XSS. Sigue MVT de forma incompleta y no presenta un patrón GoF aplicado de manera clara.

## Hallazgos

### 1. Inyección SQL en autenticación

- **Severidad:** Crítica
- **Ubicación:** `taquilla/views.py`, login, líneas 7-12.
- **Problema:** correo y PIN se interpolan directamente en la consulta SQL.
- **Impacto:** evasión del inicio de sesión, lectura de información y posible modificación de datos.
- **Solución futura:** usar consultas parametrizadas o el ORM de Django; validar mediante `Form`; almacenar PIN/contraseña con hash usando `make_password` y `check_password`.

### 2. Autenticación falsificable mediante cookies

- **Severidad:** Crítica
- **Ubicación:** `taquilla/views.py`, líneas 20-24.
- **Problema:** basta enviar una cookie de acceso; esta también crea una sesión con `sid=1`. Las cookies no se validan contra una sesión real ni están firmadas por la aplicación.
- **Impacto:** suplantación de usuarios y acceso no autorizado.
- **Solución futura:** integrar `django.contrib.auth`, `login`, `logout`, `@login_required`, permisos y grupos. Eliminar todas las formas de evadir el inicio de sesión.

### 3. Compra sin autenticación ni autorización

- **Severidad:** Crítica
- **Ubicación:** `taquilla/views.py`, líneas 47-80.
- **Problema:** `/comprar/` acepta `fid`, `socio`, `asiento`, `tipo` y `pago` desde el cliente sin comprobar sesión, titularidad, existencia de función o disponibilidad del asiento.
- **Impacto:** compras a nombre de terceros, IDs arbitrarios y venta de asientos ocupados.
- **Solución futura:** tomar el socio del usuario autenticado, comprobar permisos y existencia de todos los objetos en servidor, y validar el asiento dentro de una transacción.

### 4. Inyección SQL en compra, puntos y asientos

- **Severidad:** Crítica
- **Ubicación:** `taquilla/views.py`, líneas 41-45 y 64-77; `taquilla/templatetags/sql_cine.py`, líneas 6-10.
- **Problema:** `fid`, `socio` y `asiento` se concatenan en `SELECT`, `UPDATE` e `INSERT`; el tag de asientos construye SQL con un valor recibido por GET.
- **Impacto:** modificación de saldo, lectura de datos y corrupción de ventas.
- **Solución futura:** consultas parametrizadas, validación de tipos y eliminación de SQL desde el tag de template.

### 5. Protección contra solicitudes falsas ausente en login y compra

- **Severidad:** Crítica
- **Ubicación:** `cinerex/settings.py`, líneas 5-10; `templates/login.html` y `templates/comprar.html`.
- **Problema:** no está habilitado `CsrfViewMiddleware` y los formularios no incluyen `{% csrf_token %}`.
- **Impacto:** un sitio externo puede forzar compras usando la sesión de una víctima.
- **Solución futura:** restaurar el middleware estándar, incluir tokens en formularios y aceptar compras únicamente por POST validado.

### 6. Posible ejecución de scripts maliciosos por marcar HTML como seguro

- **Severidad:** Alta
- **Ubicación:** `taquilla/views.py`, líneas 30-36; `taquilla/templatetags/sql_cine.py`, líneas 11-27; `templates/cartelera.html`.
- **Problema:** títulos, códigos de asiento y contenido de `/mods/` se interpolan en HTML y se muestran con `safe` o `mark_safe`.
- **Impacto:** ejecución de JavaScript almacenado o reflejado.
- **Solución futura:** pasar datos estructurados a los templates, conservar el autoescape y permitir HTML solo mediante una lista blanca sanitizada.

### 7. Endpoint administrativo público

- **Severidad:** Alta
- **Ubicación:** `cinerex/urls.py`, líneas 8-10.
- **Problema:** `admin_ocupacion/` apunta a `ocupacion` sin autenticación ni comprobación de rol.
- **Impacto:** exposición y manipulación de información operativa.
- **Solución futura:** proteger con `login_required`, permisos específicos de staff y separar las vistas administrativas.

### 8. Secretos y configuración de desarrollo expuestos

- **Severidad:** Alta
- **Ubicación:** `cinerex/settings.py`, líneas 1-4.
- **Problema:** `SECRET_KEY` fija, `DEBUG=True`, `ALLOWED_HOSTS=['*']`, usuario MySQL `root` y contraseña `password`.
- **Impacto:** exposición de errores, compromiso de sesiones y acceso amplio a la base.
- **Solución futura:** variables de entorno o secret manager, `DEBUG=False`, hosts explícitos y usuario de BD con privilegios mínimos.

### 9. PIN en texto plano y credenciales débiles

- **Severidad:** Alta
- **Ubicación:** `bd/cinerex.sql`, líneas 3-8.
- **Problema:** columna `pin VARCHAR(20)` y credencial inicial `caja@rex.mx / 0000`.
- **Impacto:** robo directo de cuentas.
- **Solución futura:** migrar al sistema de usuarios de Django, aplicar hash, eliminar credenciales de ejemplo y forzar rotación.

### 10. Manipulación arbitraria de puntos

- **Severidad:** Alta
- **Ubicación:** `taquilla/views.py`, líneas 70-73.
- **Problema:** se resta `precio` al socio enviado por el cliente sin comprobar identidad, existencia, saldo suficiente ni resultado no negativo.
- **Impacto:** fraude y saldos inválidos.
- **Solución futura:** usar el socio autenticado, actualizar condicionalmente por saldo y registrar un movimiento contable.

### 11. Compra no atómica y vulnerable a carreras

- **Severidad:** Alta
- **Ubicación:** `taquilla/views.py`, líneas 74-80.
- **Problema:** boleto, asiento y combo se escriben en consultas separadas, sin transacción, bloqueo ni condición `ocupado=0`.
- **Impacto:** doble venta y datos parciales si una operación falla.
- **Solución futura:** `transaction.atomic()`, bloqueo o actualización condicional, restricciones únicas e idempotencia del pedido.

### 12. Esquema sin integridad relacional

- **Severidad:** Alta
- **Ubicación:** `bd/cinerex.sql`, líneas 3-8.
- **Problema:** no se observan `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL` ni índices relevantes.
- **Impacto:** duplicados, registros huérfanos y consultas lentas.
- **Solución futura:** modelos y migraciones Django o DDL formal con claves, restricciones e índices.

### 13. Validación insegura de la respuesta de pago

- **Severidad:** Alta
- **Ubicación:** `taquilla/views.py`, líneas 58-69.
- **Problema:** el pago se aprueba si el texto contiene fragmentos XML, sin parseo, verificación del importe, pedido, moneda o firma.
- **Impacto:** falsos pagos, cobros incorrectos y fraude.
- **Solución futura:** cliente oficial, XML/JSON parseado, monto calculado en servidor, firma validada y estados idempotentes.

### 14. Sesiones y configuración Django incompletas

- **Severidad:** Alta
- **Ubicación:** `cinerex/settings.py`, líneas 4-10; `bd/cinerex.sql`.
- **Problema:** se usa `SessionMiddleware`, pero el SQL no crea `django_session` y no hay migraciones visibles. Además, `django.contrib.auth` aparece sin `django.contrib.contenttypes`.
- **Impacto:** el login puede fallar al escribir la sesión y el sistema de auth puede quedar incompleto.
- **Solución futura:** completar la configuración estándar, ejecutar migraciones y validar con `manage.py check` y `migrate`.

### 15. El formulario de compra puede perder `fid`

- **Severidad:** Alta
- **Ubicación:** `templates/comprar.html`; `cinerex/settings.py`, línea 11.
- **Problema:** el template usa `request.GET.fid`, pero los context processors están vacíos y la vista no pasa `fid` explícitamente.
- **Impacto:** el formulario puede enviar un identificador vacío y producir errores.
- **Solución futura:** pasar `fid` en el contexto o habilitar el context processor de request.

### 16. Rutas de función sin validación

- **Severidad:** Media/Alta
- **Ubicación:** `taquilla/views.py`, líneas 38-45; `taquilla/templatetags/sql_cine.py`.
- **Problema:** `fid` puede ser vacío, no numérico o inexistente; `funcion_old` expone directamente datos de asientos.
- **Impacto:** errores 500 y superficie antigua innecesaria.
- **Solución futura:** validar entrada, devolver 400/404 y eliminar la ruta obsoleta.

### 17. Campos POST ausentes producen 500

- **Severidad:** Media
- **Ubicación:** `taquilla/views.py`, líneas 7-9 y 47-55.
- **Problema:** se usa `request.POST['campo']` sin manejar campos faltantes.
- **Impacto:** `MultiValueDictKeyError` y respuestas 500 ante entradas incompletas.
- **Solución futura:** `Form` de Django, validación y errores mostrables.

### 18. Servicios externos lentos y errores silenciosos

- **Severidad:** Media
- **Ubicación:** `taquilla/views.py`, líneas 25-28 y 59-68.
- **Problema:** llamadas secuenciales a `127.0.0.1` pueden bloquear la cartelera; el pago puede esperar hasta 90 segundos. Excepciones se ignoran o solo se convierten en fallo genérico.
- **Impacto:** lentitud, indisponibilidad y falta de trazabilidad.
- **Solución futura:** timeouts pequeños, cache, circuit breaker, logs estructurados y procesamiento asíncrono.

### 19. Consultas repetidas y cursores poco controlados

- **Severidad:** Media
- **Ubicación:** `taquilla/views.py`, líneas 28-35; `sql_cine.py`, líneas 16-27.
- **Problema:** se consulta la función u ocupación por cada película durante el render.
- **Impacto:** degradación conforme crece la cartelera.
- **Solución futura:** consultas agrupadas, ORM/DTOs preparados en la vista, paginación y cache.

### 20. La documentación contradice el código

- **Severidad:** Alta
- **Ubicación:** `docs/ARQUITECTURA_OFICIAL.md`, líneas 1-10.
- **Problema:** documenta logística portuaria y prohíbe películas, boletos y login reimplementado, mientras el código implementa un cine con login artesanal.
- **Impacto:** requisitos y arquitectura ambiguos.
- **Solución futura:** decidir el dominio válido y actualizar código y documentación desde una única fuente de verdad.

### 21. Falta la base de una aplicación Django mantenible

- **Severidad:** Alta
- **Problema:** no se observan `models.py`, migraciones, formularios, tests, `apps.py` ni administración Django.
- **Impacto:** no hay validación declarativa, despliegues reproducibles ni pruebas de compra/concurrencia.
- **Solución futura:** crear modelos, migraciones, formularios, admin y pruebas unitarias, de integración y de concurrencia.

### 22. Configuración de despliegue incompleta

- **Severidad:** Media/Alta
- **Ubicación:** `cinerex/settings.py`.
- **Problema:** faltan configuración completa de estáticos, cookies seguras, HTTPS, HSTS, `SecurityMiddleware`, correo y rutas basadas en `BASE_DIR`; `DIRS=['templates']` depende del directorio actual.
- **Solución futura:** separar settings de desarrollo/producción, configurar estáticos, HTTPS, `HttpOnly`, `Secure`, `SameSite`, logging y servidor WSGI.

### 23. UX frágil y poco accesible

- **Severidad:** Media
- **Ubicación:** `templates/login.html`, `comprar.html`, `funcion.html`.
- **Problema:** faltan labels y validación visible; los errores devuelven `mal`; hay URLs hardcodeadas y mensajes basados en `alert`.
- **Solución futura:** URLs nombradas, formularios accesibles, mensajes Django y estados claros de éxito/error.

## Limitaciones

No se auditaron una base MySQL real, configuración de producción, `.env`, logs, CI, servidor web ni los servicios `banco-cine.local`/`127.0.0.1/mods`. Por tanto, esos componentes requieren una revisión adicional antes de cerrar el diagnóstico.
