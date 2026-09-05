# Análisis de `hotelluna_spring`

## Alcance y conclusión

Auditoría estática de `pom.xml`, código Java, templates, propiedades, SQL, documentación y artefactos `target`. No se modificó el proyecto. No se pudo probar el banco, correo ni los servicios externos.

**Conclusión:** la aplicación no debe exponerse públicamente. Un componente general puede interceptar toda la aplicación, la autenticación se puede falsificar, existe inyección de código SQL, no hay autorización consistente y las reservas no tienen transacciones ni control de disponibilidad.

## Resumen de problemas

Los fallos centrales son que un servlet personalizado intercepta todas las rutas, la autenticación depende de una cookie falsificable y el login y las reservas concatenan datos en SQL. Check-in, reserva y facturación no tienen autorización; las reservas tampoco comprueban disponibilidad ni son transaccionales. Hay contraseñas en texto plano, credenciales de base expuestas, XSS en facturas y servicios externos sin timeout. El modelo SQL es demasiado débil para representar fechas, habitaciones, pagos y relaciones, y la documentación corresponde a otro sistema.

## Patrón de diseño identificado

El proyecto está planteado sobre **MVC**, usando controladores Spring MVC y vistas Thymeleaf. También intenta usar **Front Controller** mediante `DispatcherServlet`, normalmente proporcionado por Spring. No obstante, `FrontControllerServlet` declara `/*` y no delega correctamente, por lo que interfiere con ese patrón. No se observa una capa de servicio o repositorio bien separada. MVC y Front Controller están presentes, pero aplicados de forma incompleta y conflictiva.

## Hallazgos

### 1. Servlet global puede inutilizar Spring MVC

- **Severidad:** Crítica
- **Ubicación:** `src/main/java/mx/luna/web/FrontControllerServlet.java`, líneas 7-15; `HotelApp.java`, líneas 5-6.
- **Problema:** `@WebServlet(urlPatterns="/*")` intercepta todas las rutas, pero `service()` solo responde para `/reservar` y no delega al `DispatcherServlet`.
- **Impacto:** `/`, `/login`, recursos estáticos y controladores pueden devolver respuestas vacías o no ejecutarse.
- **Solución futura:** eliminar el servlet, como indica la documentación, o limitarlo a una ruta concreta y delegar correctamente.

### 2. Cookie falsificable con privilegios de gerente

- **Severidad:** Crítica
- **Ubicación:** `HomeCtrl.java`, líneas 14-16; `LoginCtrl.java`, líneas 16-17.
- **Problema:** cualquier cliente que envíe una cookie administrativa recibe `eid=1`; no se valida su valor, firma, sesión ni rol.
- **Impacto:** suplantación y acceso como gerente.
- **Solución futura:** Spring Security real, sesiones gestionadas por el framework y autorización por roles; eliminar esta forma de evadir el inicio de sesión.

### 3. Inyección SQL en login y reservas

- **Severidad:** Crítica
- **Ubicación:** `LoginCtrl.java`, líneas 12-13; `ReservaCtrl.java`, líneas 34-36.
- **Problema:** parámetros HTTP se concatenan en SQL.
- **Impacto:** evasión del inicio de sesión, lectura, modificación y posible destrucción de datos.
- **Solución futura:** `JdbcTemplate` parametrizado, repositorios/JPA, validación de entrada y pruebas de inyección.

### 4. Contraseñas y credenciales expuestas

- **Severidad:** Crítica
- **Ubicación:** `bd/hotel.sql`, líneas 2-8; `src/main/resources/application.properties`, líneas 1-3.
- **Problema:** claves como `123`, usuario MySQL `root` y contraseña `password` están en archivos versionables; las contraseñas parecen estar en texto plano.
- **Impacto:** compromiso de cuentas y de la base.
- **Solución futura:** Argon2/BCrypt mediante `PasswordEncoder`, secretos por entorno/secret manager y usuario DB restringido.

### 5. Spring Security declarado pero no configurado

- **Severidad:** Alta
- **Ubicación:** `pom.xml`, líneas 8-13.
- **Problema:** existe el starter, pero no se observan `SecurityFilterChain`, `UserDetailsService`, `PasswordEncoder` ni reglas de autorización.
- **Impacto:** autenticación predeterminada o comportamiento incompatible con el login artesanal; los POST pueden quedar bloqueados por CSRF o sin protección explícita.
- **Solución futura:** definir públicamente rutas permitidas, login, logout, CSRF, roles y políticas de sesión; incluir tokens Thymeleaf.

### 6. Operaciones sensibles sin autorización

- **Severidad:** Alta
- **Ubicación:** `CheckinCtrl.java`, líneas 9-14; `ReservaCtrl.java`, líneas 12-40; `FacturaCtrl.java`, líneas 5-6.
- **Problema:** check-in, reservas y facturas no verifican identidad, propiedad de la reserva ni rol.
- **Impacto:** acceso directo, modificación de reservas ajenas y exposición financiera.
- **Solución futura:** autorización declarativa y comprobación de propiedad por endpoint.

### 7. Acceso a reservas ajenas y check-in repetible

- **Severidad:** Alta
- **Ubicación:** `CheckinCtrl.java`, líneas 10-14.
- **Problema:** cualquier reserva puede marcarse como `inhouse` y generar otra llave sin validar existencia, estado previo o huésped.
- **Solución futura:** validar transiciones, bloquear la reserva, exigir propiedad y usar una clave única para la llave.

### 8. Scripts maliciosos guardados y consultas SQL inseguras en facturas

- **Severidad:** Alta
- **Ubicación:** `FacturaSql.java`, líneas 9-16; `facturas.html`, línea 1.
- **Problema:** el nombre se concatena en SQL y el resultado HTML se renderiza con `th:utext`.
- **Impacto:** inyección SQL y JavaScript persistente al abrir facturas.
- **Solución futura:** consultas parametrizadas, DTOs y `th:text`; no construir HTML desde acceso a datos.

### 9. Reservas inconsistentes bajo concurrencia

- **Severidad:** Alta
- **Ubicación:** `ReservaCtrl.java`, líneas 27-38.
- **Problema:** se inserta una reserva y luego se marca una habitación por tipo con `LIMIT 1`, sin comprobar disponibilidad ni filas afectadas.
- **Impacto:** sobreventa, habitación arbitraria y reservas sin habitación real.
- **Solución futura:** servicio transaccional, selección con bloqueo y actualización condicional de una única habitación disponible.

### 10. Pago, DB y correo sin operación consistente

- **Severidad:** Alta
- **Ubicación:** `ReservaCtrl.java`, líneas 28-40.
- **Problema:** pago, varias inserciones y correo se ejecutan en secuencia sin `@Transactional`, compensación ni idempotencia.
- **Impacto:** pago aprobado sin reserva, datos parciales o correo fallido después de persistir.
- **Solución futura:** estados pendiente/confirmado, transacción DB, clave idempotente y patrón outbox para notificaciones.

### 11. Servicios externos sin timeout ni resiliencia

- **Severidad:** Alta
- **Ubicación:** `HomeCtrl.java`, líneas 18-21; `ReservaCtrl.java`, líneas 28-31.
- **Problema:** `RestTemplate` se crea en el controlador, hace llamadas secuenciales a `127.0.0.1` y al banco sin timeout, reintentos o circuit breaker.
- **Impacto:** bloqueos, lentitud y comportamiento no reproducible.
- **Solución futura:** clientes como beans, timeouts, resiliencia, configuración por perfil y mocks de contrato.

### 12. Excepciones usadas para autenticar

- **Severidad:** Media/Alta
- **Ubicación:** `HomeCtrl.java`, líneas 14-16.
- **Problema:** usuario no autenticado produce `RuntimeException("no")`.
- **Impacto:** respuesta 500 en lugar de 302, 401 o 403.
- **Solución futura:** `AuthenticationEntryPoint`, `@ControllerAdvice` y códigos HTTP semánticos.

### 13. Validación de entrada insuficiente

- **Severidad:** Media
- **Ubicación:** `LoginCtrl.java`, líneas 11-13; `ReservaCtrl.java`, líneas 13-15.
- **Problema:** no hay `@Valid`, límites de tamaño, correo válido, enums ni validación server-side de opciones.
- **Impacto:** datos inválidos, abuso de correo y valores no contemplados con precio por defecto.
- **Solución futura:** DTOs con Bean Validation, enums, límites y mensajes de error.

### 14. Modelo SQL sin integridad referencial

- **Severidad:** Alta
- **Ubicación:** `bd/hotel.sql`, líneas 2-8.
- **Problema:** empleados y habitaciones no tienen claves primarias visibles; faltan FK, `NOT NULL`, `UNIQUE`, checks e índices.
- **Impacto:** duplicados, huérfanos y estados imposibles.
- **Solución futura:** migraciones versionadas, PK/FK, restricciones e índices.

### 15. El esquema no representa las reservas

- **Severidad:** Alta
- **Ubicación:** `bd/hotel.sql`, líneas 4-6.
- **Problema:** reservas no contiene habitación concreta, entrada/salida, moneda, pago, correo ni timestamps; SPA relaciona por nombre.
- **Impacto:** no se pueden impedir solapamientos ni distinguir huéspedes con igual nombre.
- **Solución futura:** entidades huésped, reserva, habitación, pago y servicio relacionadas por IDs y fechas.

### 16. Facturación con consultas repetidas y exposición global

- **Severidad:** Media/Alta
- **Ubicación:** `FacturaSql.java`, líneas 9-15.
- **Problema:** se consultan todas las reservas y luego una consulta por fila, sin filtrar adecuadamente por usuario o rol.
- **Impacto:** degradación y exposición de información.
- **Solución futura:** consulta agregada parametrizada, paginación y DTOs por permiso.

### 17. Documentación incompatible con el código

- **Severidad:** Alta
- **Ubicación:** `docs/README_ARQ.txt` y `docs/ER.txt`.
- **Problema:** documenta inventario NASA, SKU, racks y Event Sourcing, mientras el código implementa hotel, huéspedes, reservas y SPA; también afirma que existen transacciones y seguridad no visibles.
- **Solución futura:** definir el dominio real, retirar documentación obsoleta y documentar la arquitectura verificable.

### 18. Interfaz incompleta y poco accesible

- **Severidad:** Media
- **Ubicación:** templates `home.html`, `reservar.html`, `checkin.html` y `spa.html`.
- **Problema:** faltan estructura HTML completa, labels, disponibilidad por fechas, mensajes de éxito/error, logout y navegación por rol; `spa.html` es texto estático.
- **Solución futura:** vistas Thymeleaf completas, validación visible, estados de reserva y navegación coherente.

### 19. Configuración rígida e insegura

- **Severidad:** Media/Alta
- **Ubicación:** `application.properties`, líneas 1-3.
- **Problema:** conexión fija a localhost con `root/password`; faltan perfiles, correo, TLS, cookies seguras y observabilidad.
- **Solución futura:** perfiles dev/test/prod, variables de entorno, usuario DB restringido, mail, HTTPS y health checks.

### 20. Artefactos compilados potencialmente obsoletos

- **Severidad:** Media
- **Ubicación:** `target/classes` y `target/test-classes`.
- **Problema:** `target` contiene copias compiladas, pero no se puede confirmar que correspondan al último fuente y no se observan pruebas compiladas.
- **Solución futura:** excluir `target`, limpiar y recompilar en CI, y ejecutar pruebas desde una compilación limpia.

## Limitaciones

No hay tests, mocks de pago/correo, CI ni configuración de producción visible. Los endpoints `127.0.0.1/mod/*` y `banco-luna.local/pay` no están incluidos, así que sus contratos y seguridad requieren auditoría aparte.
