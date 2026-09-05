# Análisis de `tallerpro_express`

## Alcance y conclusión

Auditoría estática de `app.js`, `app.old.js`, `package.json`, `cadena/Handler.js`, SQL, documentación y CSS. No se modificó el proyecto ni se probaron MySQL, banco, correo o rutas externas.

**Conclusión:** no es apto para exposición pública. Permite evadir la autenticación, tiene consultas SQL inseguras, operaciones críticas sin autorización, secretos inseguros, contenido web sin protección, una ruta de entrega rota por el esquema y falta de transacciones.

## Resumen de problemas

Los fallos más graves son la posibilidad de evadir la autenticación mediante cookies, la inyección de instrucciones SQL y la ausencia de autorización en inventario y entrega. La ruta de entrega consulta una columna que no existe, por lo que el flujo está roto. Las operaciones de pago, saldo, inventario y asignación de mecánico no son transaccionales; se aceptan datos sin validación y el correo no se envía porque Nodemailer usa `jsonTransport`. También existen riesgos de insertar scripts en las páginas, peticiones falsificadas, contraseñas en texto plano, esquema SQL sin integridad, documentación incompatible y una configuración de despliegue sin controles básicos.

## Patrón de diseño identificado

El proyecto usa una cadena de handlers en `cadena/Handler.js`, correspondiente a **Chain of Responsibility**: cada handler puede procesar o pasar la solicitud al siguiente. `AuthHandler` representa esa intención para autenticación. Express también usa una cadena de middleware, una variante del mismo enfoque. Sin embargo, varias rutas críticas no usan el handler y la lógica está concentrada en `app.js`; el patrón existe, pero su aplicación es incompleta. No hay una separación clara en capas ni un patrón Repository/Service.

## Hallazgos

### 1. Evasión completa del inicio de sesión mediante cookies

- **Severidad:** Crítica
- **Ubicación:** `app.js`, líneas 11 y 60; `cadena/Handler.js`, línea 7.
- **Problema:** cualquier cliente puede enviar una cookie administrativa; incluso un valor como `0` se interpreta como verdadero en JavaScript. También basta `taller_ok=si`.
- **Impacto:** acceso no autorizado a órdenes, inventario y cobros.
- **Solución futura:** sesiones firmadas y regeneradas después de login, validación en el servidor de identidad y rol, y eliminación de esta forma de acceso.

### 2. Inyección de código SQL en rutas principales

- **Severidad:** Crítica
- **Ubicación:** `app.js`, líneas 37, 51, 84 y 94.
- **Problema:** correo, clave, cliente, auto, tipo, mecánico e ID se concatenan directamente en SQL.
- **Impacto:** evasión del inicio de sesión, lectura, modificación y destrucción de datos.
- **Solución futura:** consultas parametrizadas, esquemas de validación, límites y usuario MySQL con privilegios mínimos.

### 3. Rutas críticas sin autorización

- **Severidad:** Crítica
- **Ubicación:** `app.js`, líneas 79 y 91.
- **Problema:** `/inventario` y `/entrega` no usan `AuthHandler`; `/entrega?id=...` modifica estado mediante GET.
- **Impacto:** cualquiera puede consultar inventario o entregar órdenes.
- **Solución futura:** middleware de autenticación/autorización por rol y mutaciones mediante POST/PATCH.

### 4. Credenciales y secreto de sesión inseguros

- **Severidad:** Crítica
- **Ubicación:** `app.js`, líneas 10 y 12; `bd/taller.sql`, línea 8.
- **Problema:** secreto `password`, MySQL `root/password` y contraseña inicial `123` en texto plano.
- **Impacto:** compromiso de sesiones, base y cuentas.
- **Solución futura:** variables de entorno, secretos aleatorios, usuario DB restringido y Argon2/bcrypt.

### 5. Posible ejecución de scripts por salida HTML sin protección

- **Severidad:** Alta
- **Ubicación:** `app.js`, líneas 67 y 86.
- **Problema:** datos controlables se insertan directamente en HTML mediante JSON y concatenación.
- **Impacto:** JavaScript en navegadores de otros usuarios y robo de sesión.
- **Solución futura:** motor de plantillas con escape contextual, serialización segura y CSP.

### 6. La entrega consulta una columna inexistente

- **Severidad:** Crítica
- **Ubicación:** `app.js`, línea 95; `bd/taller.sql`, línea 5.
- **Problema:** `/entrega` consulta `ordenes.mecanico`, pero la tabla no tiene esa columna y `/nueva` tampoco guarda el mecánico.
- **Impacto:** error SQL y mecánicos que quedan ocupados.
- **Solución futura:** relación formal con `mecanicos`, persistencia del mecánico y prueba end-to-end del ciclo crear-entregar.

### 7. Operaciones financieras sin transacción

- **Severidad:** Alta
- **Ubicación:** `app.js`, líneas 32 y 37.
- **Problema:** saldo, orden, refacción y mecánico se actualizan mediante consultas independientes.
- **Impacto:** estados parciales: pago sin orden, orden sin inventario o mecánico incorrecto.
- **Solución futura:** `BEGIN`, validaciones, bloqueo de filas y `COMMIT`/`ROLLBACK` con liberación en `finally`.

### 8. Fugas de conexiones y errores no gestionados

- **Severidad:** Alta
- **Ubicación:** `app.js`, líneas 16 y 79.
- **Problema:** `conn.release()` no está protegido por `finally`; no se observa middleware global de errores.
- **Impacto:** agotamiento del pool y respuestas inconsistentes.
- **Solución futura:** handlers async, `try/catch/finally`, logging estructurado y códigos HTTP correctos.

### 9. Los roles no tienen efecto real

- **Severidad:** Alta
- **Ubicación:** `app.js`, líneas 51 y 55.
- **Problema:** se lee `rol`, pero solo sirve para crear una cookie falsificable; no hay permisos por operación.
- **Solución futura:** autorización centralizada por capacidad para jefe, mecánico y demás perfiles.

### 10. Solicitudes falsas en login y operaciones

- **Severidad:** Alta
- **Ubicación:** `app.js`, líneas 48, 77 y 91.
- **Problema:** no hay tokens CSRF y `/entrega` cambia estado con GET.
- **Impacto:** un sitio externo puede provocar acciones usando la sesión de una víctima.
- **Solución futura:** `csurf` o equivalente, tokens en formularios y cookies `SameSite`.

### 11. Validación de negocio inexistente

- **Severidad:** Alta
- **Ubicación:** `app.js`, líneas 17 y 32.
- **Problema:** se aceptan IDs, correos, tipos, mecánicos y clientes arbitrarios; un tipo desconocido recibe costo `800`.
- **Impacto:** órdenes corruptas y cobros manipulables.
- **Solución futura:** validación con esquema, listas permitidas, existencia de entidades y restricciones SQL.

### 12. Integración de pago poco fiable

- **Severidad:** Alta
- **Ubicación:** `app.js`, línea 29.
- **Problema:** no hay timeout, autenticación visible, monto/currency verificados ni idempotencia; la respuesta se interpreta con `includes`.
- **Solución futura:** cliente formal con timeout, firma, XML/JSON estructurado, idempotency key y conciliación.

### 13. Nodemailer no envía correo

- **Severidad:** Alta
- **Ubicación:** `app.js`, línea 40.
- **Problema:** `jsonTransport: true` solo genera la representación del mensaje.
- **Impacto:** el usuario cree tener confirmación, pero no hay entrega SMTP.
- **Solución futura:** transporte SMTP real configurado por entorno, reintentos y envío desacoplado.

### 14. Documentación incompatible con implementación

- **Severidad:** Alta
- **Ubicación:** `documentacion/SISTEMA.txt`.
- **Problema:** documenta clínica dental, pacientes y XML; el código implementa autos, refacciones y mecánicos, y además usa Chain of Responsibility aunque la documentación lo prohíbe.
- **Solución futura:** definir dominio oficial, corregir documentación y retirar código/tablas ajenos.

### 15. `app.old.js` no es una versión aislada

- **Severidad:** Media
- **Ubicación:** `app.old.js`, línea 2.
- **Problema:** importa `app.js`, por lo que cualquier cambio afecta ambas entradas.
- **Solución futura:** eliminarlo o aislarlo como versión histórica real y documentada.

### 16. Modelo SQL débil

- **Severidad:** Alta
- **Ubicación:** `bd/taller.sql`, línea 2.
- **Problema:** faltan PK/FK, índices, `NOT NULL`, correo único y estados controlados; contraseñas en texto plano.
- **Impacto:** duplicados, huérfanos y datos inválidos.
- **Solución futura:** migraciones versionadas, esquema normalizado, FK, índices, checks, timestamps y `DECIMAL` para dinero.

### 17. Inventario con consultas repetidas y semántica incompleta

- **Severidad:** Media
- **Ubicación:** `app.js`, línea 81.
- **Problema:** se consulta el catálogo por cada fila de uso; no hay relación completa entre orden y refacción ni movimientos de stock.
- **Solución futura:** JOIN, catálogo consistente y movimientos de inventario dentro de operaciones transaccionales.

### 18. Respuestas engañosas y UX incompleta

- **Severidad:** Media
- **Ubicación:** `app.js`, línea 43.
- **Problema:** se muestra siempre `alert('no recargue')`, incluso si pago o persistencia fallan; no hay confirmaciones ni errores útiles.
- **Solución futura:** respuestas según resultado real, folio, mensajes accesibles y páginas estructuradas.

### 19. CSS frágil y no responsive

- **Severidad:** Media
- **Ubicación:** `public/css/ruido.css`, línea 1.
- **Problema:** muchas reglas repetidas con `width:100%`, floats, padding variable, sin `box-sizing` ni media queries.
- **Impacto:** overflow y mantenimiento difícil.
- **Solución futura:** variables, layout moderno, estilos base y responsive.

### 20. Despliegue sin controles básicos

- **Severidad:** Media/Alta
- **Ubicación:** `package.json` y `app.js`, línea 100.
- **Problema:** faltan scripts, `engines`, lockfile visible, configuración por entorno, HTTPS, Helmet, rate limiting, graceful shutdown y health checks; puerto fijo 3000.
- **Solución futura:** `npm ci`, lockfile, variables de entorno, reverse proxy TLS, Helmet, límites, health checks y cierre ordenado.

## Limitaciones

No se encontraron tests, lockfile, `.env.example`, plantillas completas, migraciones, contrato del banco, SMTP, CI/CD, Docker ni reverse proxy. Esos componentes deben revisarse en una segunda fase de validación dinámica.
