# Análisis de `pasofit_flutter`

## Alcance y conclusión

Auditoría estática de `pubspec.yaml`, `lib/`, SQL y documentación. No se modificó el proyecto ni se probó un backend real o un dispositivo.

**Conclusión:** la app tiene autenticación insegura, tráfico HTTP, base local sin inicialización, datos sin aislamiento por usuario, fugas de listeners/timers y varios flujos que no funcionan o no son consistentes.

## Resumen de problemas

Los principales problemas son una autenticación basada en texto y una sesión ficticia, el envío de credenciales por HTTP y el uso de `127.0.0.1`, que no apunta al backend desde un teléfono. La base SQLite se abre sin crear tablas ni migraciones y no relaciona los datos con el usuario. También hay listeners y timers que nunca se liberan, el selector de rutina no cambia el valor guardado, los logros se acumulan incorrectamente y las operaciones asíncronas actualizan widgets destruidos. La app mezcla buses globales con un Cubit no utilizado y carece de manejo de red consistente.

## Patrón de diseño identificado

La interfaz utiliza el enfoque **Widget-based** de Flutter. La documentación propone **BLoC/Observer**, y existe `RelojCubit`, pero el código real usa listas globales (`RelojBus` y `PesoBus`) como una implementación manual y no controlada de **Observer**. No se observa un repositorio o servicio central para red y persistencia. Hay una intención de BLoC/Observer, pero el patrón no está aplicado de forma consistente.

## Hallazgos

### 1. Autenticación completamente falsificable

- **Severidad:** Crítica
- **Ubicación:** `lib/pantallas/login.dart`, líneas 10-15.
- **Problema:** se considera login correcto si la respuesta contiene literalmente `ok` o `id`; se ignora el código HTTP, se fija `uid` en `1` y se crea un valor ficticio de cookie.
- **Impacto:** cualquier respuesta que contenga `id` puede permitir acceso.
- **Solución futura:** respuesta JSON tipada, códigos HTTP, token real con expiración/renovación y almacenamiento seguro; el estado de sesión debe vivir en un repositorio.

### 2. Credenciales por HTTP sin cifrado

- **Severidad:** Crítica
- **Ubicación:** `login.dart`, líneas 12; `inicio.dart`, líneas 20-22; `rutina.dart`, línea 21.
- **Problema:** se usan URLs `http://127.0.0.1/fit/...` y se envía la contraseña en texto plano.
- **Impacto:** captura de credenciales y sesiones.
- **Solución futura:** HTTPS obligatorio, URL por entorno, certificados válidos y headers de autorización con tokens.

### 3. Inyección de código SQL por interpolación

- **Severidad:** Alta
- **Ubicación:** `lib/pantallas/rutina.dart`, líneas 18-20; `logros.dart`, líneas 19-20; `peso.dart`, línea 20.
- **Problema:** `tipo` y otros datos se insertan directamente en sentencias SQL.
- **Impacto:** corrupción o lectura de datos si el valor llega manipulado.
- **Solución futura:** API parametrizada de SQLite/DAO y validación de dominio.

### 4. La base de datos nunca crea sus tablas

- **Severidad:** Crítica
- **Ubicación:** `peso.dart`, línea 16; `logros.dart`, línea 15; `rutina.dart`, línea 18; `bd/fit.sql`.
- **Problema:** se llama a `openDatabase('fit.db')`, pero no hay `onCreate`, `onUpgrade` ni ejecución del SQL.
- **Impacto:** en un dispositivo limpio fallan las consultas por tablas inexistentes.
- **Solución futura:** servicio centralizado con migraciones versionadas, `onCreate`, `onUpgrade`, transacciones y pruebas de migración.

### 5. No existe aislamiento de datos por usuario

- **Severidad:** Alta
- **Ubicación:** `bd/fit.sql`.
- **Problema:** `sesiones`, `logros_pend` y `bitacora_peso` no tienen `user_id`, fechas ni relaciones con cuentas.
- **Impacto:** los datos de varias cuentas se mezclan en el mismo dispositivo.
- **Solución futura:** propietario por registro, FK, timestamps, consultas filtradas y cifrado local si el riesgo lo requiere.

### 6. Cronómetro con temporizadores y avisos que nunca se liberan

- **Severidad:** Alta
- **Ubicación:** `lib/pantallas/cronometro.dart`, líneas 10-16.
- **Problema:** se registra un callback global, no se elimina y no se cancela el `Timer`; puede llamar `setState` después de destruir la pantalla.
- **Impacto:** errores de ciclo de vida y consumo creciente de recursos.
- **Solución futura:** usar `RelojCubit` o un controlador local con `dispose`, cancelar el timer y comprobar `mounted`.

### 7. `PesoBus` conserva avisos de pantallas destruidas

- **Severidad:** Alta
- **Ubicación:** `lib/estado/oyentes.dart`, líneas 4-6; `peso.dart`, líneas 12-14.
- **Problema:** el callback se añade a una lista global y nunca se elimina.
- **Solución futura:** suscripciones cancelables en `dispose` o un gestor BLoC/Riverpod con ciclo de vida claro.

### 8. La arquitectura declarada se incumple

- **Severidad:** Alta
- **Ubicación:** `docs/ARQUITECTURA.md`; `lib/estado/oyentes.dart`; `lib/estado/reloj_cubit.dart`.
- **Problema:** la documentación prohíbe listeners en widgets y define BLoC, pero se usan `RelojBus` y `PesoBus`; `RelojCubit` existe pero no se utiliza. `provider` también está declarado y no se observa uso.
- **Solución futura:** elegir una estrategia de estado, eliminar código/dependencias sin uso y actualizar la documentación.

### 9. El selector de rutina no funciona

- **Severidad:** Alta
- **Ubicación:** `lib/pantallas/rutina.dart`, líneas 25-30; `inicio.dart`, línea 31.
- **Problema:** `onChanged: (_) {}` no guarda la selección y la navegación siempre envía `tipo: cardio`.
- **Impacto:** siempre se registra cardio, aunque el usuario elija otra opción.
- **Solución futura:** estado `tipoSeleccionado`, `value` controlado, actualización en `onChanged` y validación antes de guardar.

### 10. Logros calculados de forma acumulativa incorrecta

- **Severidad:** Alta
- **Ubicación:** `lib/pantallas/logros.dart`, líneas 18-23.
- **Problema:** por cada registro pendiente se vuelve a sumar el total de sesiones; los pendientes nunca se consumen ni se deduplican.
- **Impacto:** el progreso se multiplica artificialmente.
- **Solución futura:** modelo de logros explícito, restricciones únicas, consulta agregada y marca de procesamiento.

### 11. El peso no lo introduce el usuario

- **Severidad:** Media/Alta
- **Ubicación:** `lib/pantallas/peso.dart`, líneas 18-21.
- **Problema:** inicia en 70 kg y resta 0.2 por pulsación; no existe campo, unidad, fecha ni validación.
- **Solución futura:** formulario numérico, rango válido, unidades y registro con timestamp y usuario.

### 12. Argumentos de navegación pueden romper la pantalla

- **Severidad:** Media
- **Ubicación:** `lib/pantallas/rutina.dart`, línea 11.
- **Problema:** se fuerza un mapa no nulo y una clave `tipo`; la ruta puede abrirse sin argumentos.
- **Solución futura:** argumentos tipados, valor por defecto y validación.

### 13. `setState` después de `await` sin comprobar `mounted`

- **Severidad:** Media/Alta
- **Ubicación:** `inicio.dart`, `logros.dart`, `rutina.dart` y `peso.dart`.
- **Problema:** operaciones asíncronas actualizan widgets que pueden haber sido destruidos.
- **Solución futura:** cancelar tareas cuando corresponda y comprobar `mounted` antes de actualizar.

### 14. Rutina parcialmente guardada si falla la red

- **Severidad:** Media/Alta
- **Ubicación:** `lib/pantallas/rutina.dart`, líneas 18-22.
- **Problema:** primero se insertan datos locales y después se llama al backend; si falla el correo/red, queda una rutina local aunque el usuario perciba error.
- **Solución futura:** estados local/sincronizado separados, transacción y cola outbox para reintentos.

### 15. Bases abiertas repetidamente y nunca cerradas

- **Severidad:** Media
- **Ubicación:** `peso.dart`, `logros.dart` y `rutina.dart`.
- **Problema:** cada pantalla abre su propia conexión y no la cierra.
- **Solución futura:** singleton o servicio centralizado, acceso serializado y cierre controlado.

### 16. Esquema SQLite sin restricciones

- **Severidad:** Media
- **Ubicación:** `bd/fit.sql`.
- **Problema:** faltan FK, `user_id`, timestamps, `NOT NULL`, estados controlados, índices, restricciones únicas y migraciones.
- **Impacto:** duplicados, datos inválidos y difícil evolución.
- **Solución futura:** esquema versionado con restricciones y pruebas de migración.

### 17. `127.0.0.1` no apunta al backend desde un teléfono

- **Severidad:** Alta
- **Ubicación:** `login.dart`, `inicio.dart` y `rutina.dart`.
- **Problema:** en un teléfono, localhost es el propio dispositivo; en emuladores también se requieren direcciones especiales.
- **Solución futura:** URL configurable por dev/staging/prod y documentación de red; en Android emulador, configurar el host apropiado.

### 18. Errores de red ocultos o sin tratamiento

- **Severidad:** Media/Alta
- **Ubicación:** `inicio.dart`, `login.dart` y `rutina.dart`.
- **Problema:** algunas excepciones se ignoran; login y rutina no tienen timeout, estado de carga ni mensajes claros.
- **Solución futura:** cliente HTTP central, timeout, errores tipados, reintentos controlados y feedback accesible.

### 19. Las peticiones posteriores no envían autenticación real

- **Severidad:** Alta
- **Ubicación:** `lib/pantallas/inicio.dart`, líneas 20-22.
- **Problema:** la supuesta cookie solo se guarda como argumento de navegación; no se envían headers, cookie HTTP ni token a `/mod` o `/mail`.
- **Impacto:** el backend no puede asociar ni proteger correctamente las peticiones.
- **Solución futura:** interceptor HTTP con token/sesión real, renovación y logout seguro.

## Limitaciones

No se pudo verificar el backend, el dispositivo, la configuración de Android/iOS, logs, pruebas, contratos de `/fit/login`, `/mod/*` y `/mail`, ni el comportamiento con una base creada. Es necesario probar instalación limpia, migraciones, login y sincronización en un entorno controlado.
