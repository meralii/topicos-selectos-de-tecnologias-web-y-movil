# Actividad — Microservicios con Docker

Nombre: kelly merali rodriguez reyna 
Matrícula: 22121336 


## 1. Predicción (hora 3) vs resultado

### Predicción antes de ejecutar

Para el paquete de `paquete.json`, predigo que el resultado final será **moto**. La hora de salida es 3, que corresponde al horario nocturno; según las reglas del proyecto, el dron no es viable durante la noche. La bicicleta tampoco parece viable para una distancia de 12.64 km. Moto y camioneta podrían cumplir las restricciones restantes, así que la elección final depende del ranking del modelo.

El paquete de prueba tiene estos valores:

| Campo | Valor |
|---|---:|
| Distancia | 12.64 km |
| Peso | 0.31 kg |
| Largo × ancho × alto | 11.7 × 7.6 × 10.6 cm |
| Volumen | 0.94 L |
| Frágil / refrigerado | No / No |
| Valor declarado | $4,603 MXN |
| Prioridad | mismo_dia |
| Zona de destino | periferia |
| Clima | despejado |
| Hora de salida | 3 |
| Tráfico | medio |




## 2. `docker compose ps`: qué hay en cada contenedor

El archivo `docker-compose.yml` define tres servicios separados:

| Servicio | Función según el código | Puerto |
|---|---|---:|
| `gateway` | Nginx sirve `gateway/index.html` y enruta las solicitudes. Es el único servicio publicado en la computadora. | 8080 → 80 |
| `pedidos` | Flask recibe `POST /pedidos`, llama a Recomendar por HTTP, genera el folio y conserva el pedido en una lista en memoria. | 8001, interno |
| `recomendar` | Flask valida el paquete, usa el recomendador y las reglas, y devuelve el medio y el motivo. | 8002, interno |

La URL entre Pedidos y Recomendar se configura como `http://recomendar:8002` mediante `RECOMENDAR_URL`. En Docker Compose, `recomendar` es el nombre de host del servicio dentro de la red del proyecto.



## 3. Fallo al apagar Recomendar

El código de Pedidos captura fallos de conexión o respuestas inválidas de Recomendar y devuelve HTTP 503 con un mensaje claro. Incluye un medio por defecto (`camioneta`) marcado como pendiente de validación y `pedido_creado: false`; por lo tanto, ese plan B no debe tomarse como un pedido confirmado ni como autorización para despachar.

**Prueba propia pendiente.** No pude detener Recomendar ni observar la respuesta real porque los contenedores no estaban disponibles en esta computadora. Para realizarla:

```powershell
docker compose stop recomendar
curl.exe -i -X POST http://127.0.0.1:8080/pedidos `
  -H "Content-Type: application/json" `
  --data-binary "@paquete.json"
curl.exe -i http://127.0.0.1:8080/salud/pedidos
docker compose start recomendar
```


## 4. Réplicas de la etapa 5 vs. esta práctica

Las réplicas del monolito son instancias de la misma aplicación y mantienen las mismas responsabilidades y dependencias. En esta práctica se separaron responsabilidades en servicios distintos: Pedidos crea pedidos y Recomendar calcula la recomendación; Gateway ofrece el punto de entrada al navegador. Pedidos y Recomendar se comunican por HTTP y pueden construirse por separado. Tener varios contenedores por sí solo no convierte una aplicación en microservicios: aquí importa que cada servicio tenga una responsabilidad separada y una interfaz de comunicación.

## 5. Camino: navegador → … → modelo (red vs. import)

El recorrido esperado de un pedido es:

```text
Navegador
  └─ HTTP POST /pedidos → Gateway (Nginx, puerto 8080)
       └─ HTTP → Pedidos (puerto interno 8001)
            └─ HTTP POST /sugerir → Recomendar (puerto interno 8002)
                 └─ llamadas locales de Python → recomendador, modelo y reglas
```

El navegador solo envía la ruta relativa `/pedidos` al Gateway. Pedidos llama a `http://recomendar:8002/sugerir` usando la red de Compose. Dentro del contenedor Recomendar, `app.py` importa el código del recomendador y las reglas; el recomendador carga el archivo `.joblib` y calcula la predicción. Esa parte ocurre dentro del proceso del servicio, no mediante otra solicitud HTTP.

## 6. Si solo cambia el `.joblib`, ¿qué reconstruyen?

El Dockerfile de Recomendar copia el directorio `entregas`, que contiene el modelo. Al cambiar el archivo del modelo, se debe reconstruir y recrear Recomendar:

```powershell
docker compose up -d --build recomendar
```

No hace falta reconstruir Pedidos ni Gateway si su código y la API no cambian. El modelo nuevo debe ser compatible con el preprocesamiento y las dependencias de Recomendar. En el monolito, si el Dockerfile incluye el modelo en la imagen de Django, se reconstruye la imagen del monolito que lo contiene.

## 7. Dos límites de esta práctica antes de producción

1. **Pedidos se guarda en memoria.** La lista de Python se pierde al reiniciar el proceso y no se comparte entre réplicas. Haría falta almacenamiento persistente compartido.
2. **Flask corre con el servidor de desarrollo.** Para producción se necesitaría un servidor WSGI apropiado y configuración operativa para procesos, tiempos de espera y supervisión.

## 8. ¿En qué se parece y en qué no el HTML al del monolito Django?

El HTML conserva el formulario de los 14 campos del paquete y ejemplos para distintos horarios. En el monolito, Django procesa la aplicación y atiende sus rutas. En esta versión, Nginx sirve `gateway/index.html` como archivo estático y el navegador manda el pedido a `POST /pedidos` del Gateway; el navegador no llama directamente a Pedidos ni a Recomendar.

En el código actual, el selector de modelo está deshabilitado y solo ofrece árbol de decisión. Por eso el formulario todavía no permite elegir bosque o red, aunque las instrucciones del profesor piden esa selección y mostrar qué modelo se utilizó.

## 9. Misma hora 3 con árbol, bosque y red: ¿coincidieron?

No se puede concluir si los tres modelos coinciden con la versión actual: Recomendar inicializa únicamente `obtener_recomendador("arbol")`, y el formulario solo ofrece árbol. No se probaron bosque ni red en esta implementación. Para comparar los tres, primero habría que incorporar sus modelos y permitir seleccionarlos; luego ejecutar exactamente el mismo paquete con hora 3 en cada uno y registrar el medio y motivo obtenidos.
