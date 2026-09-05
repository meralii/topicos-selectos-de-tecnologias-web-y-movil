# Análisis de `sabores_laravel`

## Alcance y conclusión

Auditoría estática de controladores, middleware, rutas, vistas Blade, SQL, documentación y configuración disponible. No se modificó el proyecto. Faltan partes esenciales de un proyecto Laravel completo, por lo que el arranque real no pudo confirmarse.

**Conclusión:** la aplicación tiene autenticación falsificable, rutas sin filtros de acceso, inyección de código SQL generalizada, exposición insegura de tarjetas, protección incompleta contra solicitudes falsas, acceso a datos ajenos, riesgo de scripts maliciosos y operaciones de pedido sin transacciones.

## Resumen de problemas

Los riesgos prioritarios son la autenticación falsificable, las rutas privadas sin middleware, SQL injection en controladores y vistas, y el envío del número completo de tarjeta. También faltan CSRF, autorización por propietario, hash de contraseñas y transacciones para pedidos; esto permite suplantaciones, puntos negativos, pedidos inconsistentes y cierres de reparto repetidos. Las vistas mezclan HTML, conexiones `mysqli` y SQL, mientras la configuración de base está duplicada. Se añaden XSS, reportes financieros públicos, una ruta antigua vulnerable y documentación de otro dominio.

## Patrón de diseño identificado

El proyecto intenta seguir **MVC** mediante rutas, controladores y vistas Blade. También declara middleware, que corresponde al patrón **Chain of Responsibility**, porque cada middleware decide si procesa o delega la petición; sin embargo, las rutas no aplican realmente esos middleware. No se observa una capa de servicios o repositorios bien integrada, y las vistas ejecutan SQL directamente. MVC y Middleware están presentes solo de forma parcial.

## Hallazgos

### 1. Autenticación evadible por cookies

- **Severidad:** Crítica
- **Ubicación:** `HomeController.php`, línea 5; `LoginController.php`, línea 13; `RepartoController.php`, línea 7.
- **Problema:** se acepta cualquier cookie `logueado=si` y cualquier cookie administrativa, asignando `uid=1`; se crean cookies manualmente.
- **Impacto:** suplantación de usuario y administrador.
- **Solución futura:** usar sesiones Laravel, regenerar sesión después de login, eliminar esta forma de evadir el inicio de sesión y aplicar `auth`, roles, policies y gates.

### 2. Rutas privadas sin middleware

- **Severidad:** Crítica
- **Ubicación:** `routes/web.php`, línea 5; `app/Http/Kernel.php`, línea 6.
- **Problema:** aunque existen aliases `auth` y `repartidor`, las rutas no usan `->middleware(...)`.
- **Impacto:** `/pedir`, `/reporte`, `/resenas` y reparto son accesibles directamente.
- **Solución futura:** grupos de middleware para autenticación, administración y reparto, con autorización por recurso.

### 3. Inyección de código SQL generalizada

- **Severidad:** Crítica
- **Ubicación:** `LoginController.php`, línea 9; `MenuController.php`, línea 10; `PedidoController.php`, línea 14; `ResenaController.php`, línea 10; `menu.blade.php`, línea 5.
- **Problema:** correo, clave, IDs y estrellas se concatenan en SQL; las vistas también ejecutan consultas `mysqli` con GET.
- **Impacto:** evasión del inicio de sesión, lectura, modificación y destrucción de datos.
- **Solución futura:** Eloquent/Query Builder o consultas preparadas, Form Requests y autorización de cada recurso.

### 4. Credenciales y contraseñas inseguras

- **Severidad:** Crítica
- **Ubicación:** `.env`, línea 1; `bd/sabores.sql`, línea 3.
- **Problema:** usuario DB `root`, contraseña `password` y contraseña inicial `123`; la columna `pass` parece almacenar texto plano.
- **Impacto:** compromiso de cuentas y base de datos.
- **Solución futura:** secretos fuera del repositorio, usuario DB mínimo, `Hash::make`/`Hash::check`, rotación y datos de ejemplo no reales.

### 5. Datos completos de tarjeta enviados a una pasarela

- **Severidad:** Crítica
- **Ubicación:** `PedidoController.php`, línea 27; `menu.blade.php`, línea 14.
- **Problema:** se recibe el PAN completo y se inserta en XML sin tokenización, validación, timeout o manejo seguro.
- **Impacto:** riesgo PCI y filtración financiera.
- **Solución futura:** pasarela oficial con tokenización; nunca recibir ni almacenar PAN; usar TLS, timeout y estados de pago verificables.

### 6. Protección incompleta contra solicitudes falsas

- **Severidad:** Alta
- **Ubicación:** `app/Http/Kernel.php`, línea 6; `routes/web.php`, línea 6.
- **Problema:** el grupo `web` solo muestra `StartSession`, no `VerifyCsrfToken`; login y pedido no incluyen `@csrf`.
- **Impacto:** peticiones forzadas desde sitios externos.
- **Solución futura:** restaurar el middleware estándar y proteger todos los POST.

### 7. Aumento indebido de permisos y acceso a datos ajenos

- **Severidad:** Crítica
- **Ubicación:** `menu.blade.php`, línea 7; `PedidoController.php`, línea 7; `RepartoController.php`, línea 12.
- **Problema:** `id_cliente`, correo y pedido llegan desde campos controlables; cierre usa solo `pedido_id` y no comprueba asignación.
- **Impacto:** pedidos a nombre de otros, descuento de puntos ajenos y cierre arbitrario.
- **Solución futura:** obtener identidad desde sesión, resolver modelos autorizados y comprobar rol, propiedad y estado en una transacción.

### 8. Scripts maliciosos guardados y reflejados

- **Severidad:** Alta
- **Ubicación:** `home.blade.php`, línea 3; `resenas.blade.php`, línea 5; `reporte.blade.php`, línea 8; `MenuController.php`, línea 12.
- **Problema:** `{!! $html !!}` y `echo` muestran contenido de BD o parámetros sin escape.
- **Impacto:** JavaScript persistente, robo de sesión y manipulación de páginas.
- **Solución futura:** escape Blade por defecto, sanitización con allowlist y eliminación de HTML construido en controladores.

### 9. Reseñas suplantables

- **Severidad:** Alta
- **Ubicación:** `resenas.blade.php`, línea 7; `ResenaController.php`, línea 10.
- **Problema:** el formulario permite enviar `uid`, `rid`, texto y estrellas sin que el servidor derive identidad ni valide pertenencia.
- **Solución futura:** tomar `uid` de sesión, validar restaurante, limitar estrellas y usar consultas preparadas.

### 10. Pedido sin integridad transaccional

- **Severidad:** Alta
- **Ubicación:** `PedidoController.php`, línea 35.
- **Problema:** vale, puntos, pedido, detalles y reparto se escriben por separado sin `DB::transaction`.
- **Impacto:** cobro sin pedido, pedido sin reparto o puntos descontados sin compra.
- **Solución futura:** transacción, validación previa, rollback y estados de pago explícitos.

### 11. `SELECT MAX(id)` causa carreras

- **Severidad:** Alta
- **Ubicación:** `PedidoController.php`, línea 45.
- **Problema:** después del INSERT se obtiene el pedido con `SELECT MAX(id)`.
- **Impacto:** dos pedidos simultáneos pueden asociar detalles al pedido equivocado.
- **Solución futura:** usar `insertGetId()` dentro de una transacción.

### 12. Puntos y vales manipulables

- **Severidad:** Alta
- **Ubicación:** `PedidoController.php`, línea 37; `RepartoController.php`, línea 16.
- **Problema:** se descuentan puntos sin comprobar saldo; el vale no tiene saldo, validación ni relación consistente.
- **Solución futura:** actualización condicionada por saldo, ledger de movimientos, restricciones y transacción.

### 13. Cierre de reparto repetible

- **Severidad:** Alta
- **Ubicación:** `RepartoController.php`, línea 12.
- **Problema:** el UPDATE no exige estado anterior `espera`; cada llamada suma cinco puntos de nuevo.
- **Impacto:** puntos duplicados y estados falsos.
- **Solución futura:** `WHERE pedido_id = ? AND estatus = 'espera'`, comprobar filas afectadas y actualizar una sola vez.

### 14. Correo vacío en el flujo de pedido

- **Severidad:** Media
- **Ubicación:** `home.blade.php`, línea 4; `menu.blade.php`, línea 8; `PedidoController.php`, línea 48.
- **Problema:** home envía `u` pero no `m`; el pedido depende de un correo enviado por el formulario.
- **Impacto:** confirmaciones a dirección vacía o fallo silencioso.
- **Solución futura:** obtener correo de la sesión y usar notificaciones Laravel con errores observables.

### 15. Errores no controlados

- **Severidad:** Media
- **Ubicación:** `PedidoController.php`, línea 15; `RepartoController.php`, línea 15; `menu.blade.php`, línea 5.
- **Problema:** se usa `$p[0]` sin comprobar resultados y no se comprueba `mysqli_query`.
- **Solución futura:** Form Requests, excepciones controladas, logging y respuestas HTTP apropiadas.

### 16. Reporte financiero sin protección ni fecha

- **Severidad:** Alta
- **Ubicación:** `routes/web.php`, línea 14; `ReporteController.php`, línea 4; `reporte.blade.php`, línea 4.
- **Problema:** `/reporte` no usa middleware y consulta ventas globales aunque la pantalla dice “del día”.
- **Impacto:** exposición de ventas y reporte incorrecto.
- **Solución futura:** autorización administrativa, filtro por timestamps, agregación y paginación.

### 17. SQL y conexiones dentro de vistas

- **Severidad:** Alta
- **Ubicación:** `menu.blade.php`, línea 2; `resenas.blade.php`, línea 1; `reporte.blade.php`, línea 2.
- **Problema:** las vistas abren `mysqli`, consultan y construyen HTML.
- **Impacto:** testing difícil, configuración duplicada y errores mezclados con presentación.
- **Solución futura:** controladores delgados, datos preparados y consultas centralizadas.

### 18. Configuración DB duplicada

- **Severidad:** Alta
- **Ubicación:** `.env`, línea 1; `menu.blade.php`, línea 3.
- **Problema:** Laravel y las vistas tienen hosts, usuario y contraseña distintos o duplicados.
- **Impacto:** entornos inconsistentes y secretos expuestos.
- **Solución futura:** una única conexión Laravel mediante entorno y eliminar `mysqli` de las vistas.

### 19. Código muerto y documentación contradictoria

- **Severidad:** Alta
- **Ubicación:** `FrontController.php`; `documentacion/LEAME_ARQUITECTO.txt`.
- **Problema:** `FrontController` no está en rutas y la documentación describe nómina ganadera, mientras el código es un restaurante.
- **Solución futura:** definir dominio oficial, retirar documentación ajena y eliminar código muerto.

### 20. Modelo SQL sin integridad

- **Severidad:** Alta
- **Ubicación:** `bd/sabores.sql`, línea 3.
- **Problema:** faltan PK/FK, índices, correo único y restricciones de estados/rangos.
- **Impacto:** duplicados, huérfanos, reseñas inválidas y consultas lentas.
- **Solución futura:** migraciones versionadas, claves, índices, checks y timestamps.

### 21. Respuesta de pedido engañosa

- **Severidad:** Media
- **Ubicación:** `PedidoController.php`, línea 50.
- **Problema:** siempre se muestra `listo`, incluso con fallos de pago o persistencia; se pide no recargar.
- **Impacto:** pedidos duplicados y falta de confirmación real.
- **Solución futura:** redirect después de POST, folio, mensaje flash y estado verificable.

### 22. Ruta antigua publicada

- **Severidad:** Media/Alta
- **Ubicación:** `routes/web.php`, línea 15; `MenuController.php`, línea 9.
- **Problema:** `menu_old` sigue público y usa SQL directo y salida sin escape.
- **Solución futura:** eliminarla o protegerla durante una migración.

## Limitaciones

No se encontraron `artisan`, `config/`, `bootstrap/`, `public/index.php`, modelos, migraciones, tests, `composer.lock` ni configuración completa de sesión, correo y pasarela. Por eso no se pudo confirmar arranque, versiones efectivas ni comportamiento end-to-end.
