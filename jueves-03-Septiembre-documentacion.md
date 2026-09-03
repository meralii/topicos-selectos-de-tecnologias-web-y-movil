# Revisión del proyecto

Equipo:
1. Kelly Merali Rodriguez Reyna
2. Daniel Adrian Roque Cortés
3. Armando Casanova Lemus

Esta documentación es una revisión general de todo el proyecto, con el proposito de analizar su estructura, archivos, patrones de código e identificar todas las problematicas presentes.

---

## 1. Duplicación de directorios y archivos
El proyecto presenta una estructura desorganizada con duplicaciones usando el sufijo `1` o nombres derivados, lo que genera ambigüedad sobre cuáles archivos están en uso en entornos de desarrollo o producción:

| Elemento Original | Elemento Duplicado / Incoherente | Tipo de Problema |
| --- | --- | --- |
| Directorio `/config` | Directorio `/config1` | Duplicación completa de directorio de configuración |
| `config/db_connect.php` | `config1/db_connect1.php` | Copia idéntica de código con renombrado innecesario. |
| `config/db_connect_produccion.php` | `config1/db_connect_produccion1.php` | Copia idéntica de credenciales de producción |
| `index.php` | `index1.php` | Dos versiones funcionalmente distintas del panel principal. |
| `kardex.php` | `kardex1.php` | Dos implementaciones paralelas de kárdex con esquemas DB diferentes |
| `pagar.php` | `pagar1.php` | Dos flujos de pago donde `pagar1.php` envía datos por POST a `pagar.php` |
| - | `login1.php` | Existe `login1.php`, pero el sistema redirige a `login.php` el cual no existe |
| - | `js1/utilerias1.js` | utilidades inconsistentes |

---

## 2. Patrones presentes
- No existe separación de capas entre Presentación como HTML/CSS/JS, la lógica de negocio PHP y el acceso a datos.
- No hay un enrutador o Front Controller por lo que cada script plano en la raíz actúa como vista, controlador y manejador de base de datos por separado y al mismo tiempo.

---

## 3. Problemas por archvio

| Archivo | Tipo | Categoría | Descripción Sintética del Hallazgo |
| --- | --- | --- | --- |
| `api.php` | CRÍTICA | Seguridad | uso de archivo inexistente, RCE con `eval()`, LFI con `file_get_contents()`. |
| `config/db_connect_produccion.php` | ALTA | Seguridad | Exposición de credenciales de producción e IP privada |
| `login1.php` | CRÍTICA | Seguridad / Diseño | SQLi, autenticación por cookies de cliente, falta de hashing de contraseñas |
| `kardex.php` | ALTA | Rendimiento / Código | Inclusión inválida, 10 niveles de `if`, N+1 queries |
| `kardex1.php` | ALTA | Arquitectura | SQLi, violaciones de idempotencia GET (`INSERT`/`mail`), desalineación con DB |
| `pagar.php` | ALTA | Arquitectura | 500 variables dummy, `UPDATE` masivo sin `WHERE`, `switch` repetitivo de 30 casos |
| `pagar1.php` | CRÍTICA | Seguridad | No asegura correctamente la informacion de pago, por manejo directo de CVV, XSS reflejado |
| `index.php` | CRÍTICA | Seguridad | 1,000 clases CSS basura, 20 llamadas SSRF internas |
| `index1.php` | ALTA | Rendimiento | Peticiones XHR síncronas, polling de 1s, riesgo de bucle de recarga infinito |
| `global/funciones.php` | MEDIA | Calidad de Código | 2,000 funciones sintéticas innecesarias que contaminan el namespace global |
| `js1/utilerias1.js` | MEDIA | Calidad de Código | 500 funciones JS vacías |
| `bd/script_produccion_real_no_tocar.sql` | ALTA | Arquitectura DB | 50 tablas abandonadas y falta de alineación con el código PHP y la documentación |
