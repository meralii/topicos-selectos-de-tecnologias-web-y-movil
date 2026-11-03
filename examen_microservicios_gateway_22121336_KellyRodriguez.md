        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
             EXAMEN — MICROSERVICIOS, GATEWAY Y EL MONOLITO
                                CON API
              Tópicos Selectos de Tecnologías Web y Móvil

                            Eduardo Alcaraz
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


Nombre: ___Kelly Merali Rodriguez Reyna___ Calificación :_________


## Indicaciones

  Este ejercicio *no* se aprueba de memoria. Casi todas las preguntas
  tienen una respuesta que «suena bien» y está mal, o dos opciones
  defendibles donde se califica el argumento.

  Reglas:

  • Expliquen el *porqué*. Una conclusión sin razonamiento vale la mitad
    (o menos).
  • Cuando digan «depende», digan *de qué*.
  • No hace falta código que compile; sí hace falta que el diseño cierre
    (quién llama a quién, qué pasa si algo falla, qué ve el cliente).
  • Pueden dibujar. Un dibujo contradictorio con el texto resta.

  Puntaje: *100 puntos* (10 × 10).


## 1 — La frase del compañero (10 puntos)


En el pizarrón quedó:

        La API separa clientes del servidor; los microservicios
        separan servidores entre sí.

  Un compañero dice: «Entonces, si mi monolito Django expone una API y
  además lo meto en Docker, ya cumplí las dos mitades de la frase.»


**a)** Desarmen su argumento. ¿Qué parte de la frase cree cumplir con la API? ¿Qué parte cree cumplir con Docker? ¿En qué se equivoca en cada una?

    a) La API separa la forma en que los clientes se comunican con el servidor: por ejemplo, una página o una aplicación puede pedirle datos a Django. Docker empaqueta y ejecuta la aplicación dentro de un contenedor. Pero Docker no divide automáticamente lo que hace la aplicación. Si Django sigue recibiendo pedidos, recomendando medios y atendiendo usuarios en un mismo programa, sigue siendo un monolito.

**b)** Den un contraejemplo mínimo: mismo código Django, *con* API y *con* Docker, que *sigamos* pudiendo llamar monolito. ¿Qué tendría que añadir (o partir) para que deje de serlo?

    b) Un ejemplo mínimo sería un proyecto Django con rutas `/usuarios/`, `/pedidos/` y `/recomendar/`, que se ejecute dentro de un contenedor y ofrezca una API. Aunque tenga muchas rutas y esté en Docker, puede seguir siendo un monolito si todo forma parte de la misma aplicación. Para dividirlo, se podrían separar Pedidos y Recomendar en aplicaciones independientes, cada una con su propio proceso, responsabilidad y forma de comunicarse.

**c)** ¿La frase del pizarrón habla de *tecnologías* (Docker, REST) o de *límites de proceso / despliegue*? Defiendan su lectura con lo que vieron en clase.

    c) La frase habla principalmente de cómo se separan las responsabilidades y los procesos. REST y Docker pueden ayudar, pero no garantizan que existan microservicios. Lo importante es que los componentes sean independientes y se comuniquen mediante una interfaz acordada. Un contenedor puede contener un monolito.

## 2 — Tres rutas, una trampa (10 puntos)

El equipo muestra este `urls.py' de un solo proyecto Django:

    ┌────
    │ path("usuarios/", ...),
    │ path("pedidos/", ...),
    │ path("recomendar/", ...),
    └────

    y este `docker-compose.yml':

    ┌────
    │ services:
    │   api:
    │     build: .
    │     ports: ["8000:8000"]
    │     deploy:
    │       replicas: 3
    └────

  Afirman: «Tres rutas + tres réplicas = microservicios con alta
  disponibilidad.»

**a)** Separen las dos ideas que mezclaron (rutas vs réplicas). ¿Qué problema resuelve cada una y cuál *no* resuelve?

    a) Las rutas organizan las distintas operaciones que ofrece una aplicación. Tener `/usuarios/`, `/pedidos/` y `/recomendar/` no significa que haya tres servicios: todas pueden ser funciones del mismo Django. Las réplicas ejecutan varias copias de esa aplicación y pueden ayudar a atender más solicitudes o soportar la caída de una copia. No separan las responsabilidades del programa.

**b)** Si una de las tres réplicas se cae a mitad de un `POST /pedidos', ¿el sistema dejó de ser monolito? ¿Por qué sí o por qué no?

    b) No. Si una réplica cae, las demás pueden seguir atendiendo solicitudes, pero la aplicación continúa siendo el mismo monolito replicado. La caída de un proceso no cambia por sí sola el diseño.

**c)** Rediseñen *solo con palabras* el `compose' para que sí ilustre microservicios (nombres de servicios y responsabilidades; no hace falta YAML perfecto)¿Cuántas *imágenes distintas* mínimo y por qué esa cantidad?

    c) Un diseño sencillo tendría tres servicios:

    - **Gateway:** recibe las solicitudes del navegador y las dirige.
    - **Pedidos:** crea y guarda los pedidos.
    - **Recomendar:** elige el medio de entrega.

    Se necesitan al menos **tres imágenes distintas** si cada uno se construye y despliega como aplicación independiente. La razón no es tener tres por obligación numérica, sino que cada pieza tiene un trabajo propio y puede actualizarse por separado.

## 3 — El gateway que «hace de más» (10 puntos)

Les proponen este diseño «para no complicar»:

        Un solo contenedor nginx+Python que: valida el JWT, elige
        el medio con el `.joblib', guarda el pedido en SQLite,
        manda el correo y devuelve el HTML.

  Lo llaman «API Gateway».

**a)** ¿Es un gateway? Si no, ¿qué es? Usen la analogía del recepcionista (o otra) y digan qué oficios mezclaron.

    a) Aunque lo llamen gateway, ese contenedor realiza muchos trabajos de la aplicación. Un gateway se parece a un recepcionista: recibe a las personas, les indica a qué área acudir y puede hacer comprobaciones generales de entrada. En el ejemplo, además de eso, recomienda el medio, guarda pedidos, manda correos y prepara la página. Mezcla recepción, logística, almacenamiento, avisos y presentación.

**b)** Mencionen *tres* consecuencias malas de ese diseño cuando el modelo pesado se reentrena cada semana y el correo empieza a fallar.

    b) Si el modelo se reentrena cada semana, habría que actualizar una pieza que también guarda pedidos y envía correos, lo que aumenta el riesgo de afectar tareas que no cambiaron. Si el correo empieza a fallar, podría retrasar o bloquear operaciones de pedidos y recomendaciones. Además, sería más difícil saber qué parte causó un problema y escalar solo la tarea que lo necesita.

**c)** Partan ese contenedor en piezas. Para cada pieza digan: ¿queda en el borde (gateway) o detrás? No inventen diez servicios: el mínimo que separe borde, logística e (si hace falta) aviso.

    c) Lo dividiría en tres piezas:

    - **Gateway, en el borde:** recibe las solicitudes, valida el acceso y las dirige.
    - **Pedidos, detrás:** guarda el pedido y coordina la operación.
    - **Recomendar, detrás:** usa el modelo `.joblib` para elegir el medio.
    - **Aviso:** si el correo es necesario y tiene suficiente trabajo propio, lo separaría detrás; si solo se manda un correo simple al crear un pedido, inicialmente podría quedar como una tarea de Pedidos.

    Así se separa la puerta de entrada de la logística y del aviso, sin crear servicios para cada detalle pequeño.

## 4 — `localhost', la trampa favorita (10 puntos)

Pedidos corre en un contenedor. Recomendar en otro, misma Compose.
  Alguien «arregla» la conexión así:

  ┌────
  │ RECOMENDAR_URL=http://127.0.0.1:8002
  └────

  En su laptop, *sin* Docker, ese `curl' a `127.0.0.1:8002' sí
  funcionaba.

**a)** Expliquen por qué en Compose ese arreglo suele fallar *aunque* Recomendar esté sano. ¿A qué proceso apunta `127.0.0.1' desde dentro de Pedidos?

    a) Dentro del contenedor Pedidos, `127.0.0.1` señala al propio contenedor de Pedidos. Por eso, `http://127.0.0.1:8002` intenta encontrar Recomendar dentro de Pedidos. Aunque Recomendar esté funcionando, esa dirección no lo señala.

**b)** ¿Por qué `http://recomendar:8002' sí tiene chance de funcionar? ¿Quién «inventa» el nombre `recomendar'?

    b) `http://recomendar:8002` puede funcionar porque Compose conecta los contenedores a una red y permite localizarlos por el nombre de su servicio. Compose proporciona esa resolución de nombres dentro de esa red.

**c)** Ahora Recomendar se muda a la laptop de otro alumno (`192.168.0.57'). Escriban la URL que pondrían *y* dos cosas que tienen que ser verdad en la WiFi para que no sea teatro (puertos, firewall, etc.). Si solo cambian la URL y nada más, ¿qué puede seguir fallando?

    c) La dirección sería:

    ```text
    http://192.168.0.57:8002
    ```

    Para que funcione, Recomendar tendría que aceptar conexiones desde otros equipos, y el puerto 8002 tendría que estar accesible desde la red. Además, el firewall de la laptop de Carla tendría que permitir ese tráfico y ambos equipos deberían poder comunicarse por la WiFi. Solo cambiar la URL no basta si Recomendar escucha únicamente dentro de su propio equipo, si el puerto no está publicado o si la red bloquea la comunicación.

## 5 — Fallo parcial con números (10 puntos)

Escenario medido en laboratorio (inventado pero coherente):

  • 1000 `POST /pedidos' por hora en promedio.
  • Recomendar tarda 200 ms cuando está bien.
  • El 5 % del tiempo Recomendar no responde (timeout 3 s).
  • Pedidos, si hay timeout, usa plan B (moto) y responde 200 en 50 ms.
  • El gateway añade 5 ms.

**a)** En la hora «normal» (Recomendar bien), ¿el cliente espera ~200 ms o ~3 s? ¿Quién pone el tiempo dominante?

    a) Cuando Recomendar responde con normalidad, el cliente espera alrededor de **205 ms**, más el tiempo mínimo de Pedidos y la comunicación. El tiempo dominante es el de Recomendar, que tarda 200 ms. Los 5 ms del Gateway añaden poco en comparación.

**b)** En el 5 % malo, con plan B: ¿el cliente ve error o pedido creado? ¿Qué «mentira útil» están aceptando (medio quizá no óptimo)?

    b) En el caso malo, después de que vence el timeout de 3 segundos, Pedidos usa el plan B y responde con un pedido creado en lugar de mostrar un error. La decisión acepta una “mentira útil”: se da una respuesta rápida y operativa, pero el medio —moto— podría no ser el mejor que habría elegido Recomendar. El sistema debe dejar claro que usó una alternativa.


**c)** Un compañero dice: «Mejor que Pedidos *reintente* 10 veces hasta que Recomendar vuelva; así nunca usamos plan B.» ¿Qué le pasa a la cola de peticiones y al gateway si Recomendar está caído 10 minutos? ¿Plan B siempre es peor que reintentar? Argumenten.

    c) Diez reintentos pueden alargar mucho cada solicitud y mantener ocupados a Pedidos y al Gateway mientras Recomendar sigue caído. Las solicitudes se acumularían y podrían retrasar incluso operaciones que sí podrían atenderse. Durante una caída de diez minutos, reintentar sin límite no hace que Recomendar vuelva antes. El plan B no siempre es mejor: conviene si existe una alternativa segura y el cliente puede aceptar esa elección; si escoger mal implica peligro o un costo alto, es mejor devolver un error claro y pedir que se intente después. También podría usarse un reintento limitado, con espera breve, y luego aplicar el plan B o informar el fallo.

## 6 — Apagan el «edificio equivocado» (10 puntos)

Tres contenedores: gateway, pedidos, recomendar. Hacen tres
  experimentos *por separado*:

  1. `docker compose stop gateway'
  2. `docker compose stop pedidos'
  3. `docker compose stop recomendar'

  Para *cada* experimento digan qué ve el navegador en `http://IP:8080/'
  (página / crear pedido) y qué sigue vivo por dentro. No basta «no
  jala»: digan *qué* no jala y qué sí podría seguir respondiendo si
  alguien hablara por dentro de la red.

  Luego: ¿en cuál de los tres el sistema «parece» más muerto hacia
  afuera aunque más piezas sigan arriba? ¿Qué les enseña eso del borde?

        **1. Se detiene Gateway.** La página en `http://IP:8080/` no carga y el navegador tampoco puede crear pedidos por esa puerta. Pedidos y Recomendar podrían seguir ejecutándose. Si alguien dentro de la red pudiera llamarlos directamente, sus rutas de servicio todavía podrían responder.

        **2. Se detiene Pedidos.** El Gateway podría seguir mostrando el HTML, pero al enviar el formulario fallaría la creación del pedido porque el servicio que recibe esa solicitud está apagado. Recomendar podría seguir vivo, pero no habría Pedidos que le solicitara una recomendación. Una llamada directa desde la red a la salud de Recomendar todavía podría responder.

        **3. Se detiene Recomendar.** El Gateway y Pedidos podrían seguir vivos. La página carga y Pedidos todavía puede informar su salud. Al crear un pedido, Pedidos no logra obtener la recomendación; según el diseño, puede responder con un plan B o con un error claro. El servicio de Recomendar no contesta.

        El sistema parece más muerto desde afuera cuando se detiene **Gateway**, porque es la única puerta del cliente. Esto enseña que el borde concentra el acceso: puede hacer que servicios todavía vivos parezcan inaccesibles desde el navegador.

## 7 — WiFi del salón, conflicto de roles (10 puntos)

Cuatro alumnos:

  • Ana: gateway + HTML
  • Beto: pedidos
  • Carla: recomendar
  • Diana: «yo también levanté un gateway en mi laptop por si Ana falla»

  Todos en la misma WiFi. El cliente (otro equipo) configura a veces la
  IP de Ana y a veces la de Diana.

**a)** ¿Qué problema de *diseño* introdujo Diana aunque «todo responda 200»? (Piensen en una sola puerta vs dos puertas.)

    a) Diana creó una segunda puerta de entrada sin acordar cómo se usa. Aunque ambas puertas respondan, el cliente puede llegar a versiones, configuraciones o rutas distintas. También se vuelve menos claro quién mantiene el punto de entrada y dónde se deben hacer cambios. Para que exista una puerta de respaldo, tendría que planearse cómo se activa y cómo mantiene la misma configuración.

**b)** Beto configuró `RECOMENDAR_URL=http://localhost:8002' porque en su máquina desarrolló Pedidos y Recomendar juntos. En el salón Recomendar está en la laptop de Carla. ¿Qué falla y cómo lo corrigen *sin* juntar otra vez los dos servicios en la laptop de Beto?

    b) Desde Pedidos en la laptop de Beto, `localhost` apunta a la laptop de Beto, no a la de Carla. Beto debe configurar Pedidos para llamar a la IP de Carla, por ejemplo:

    ```text
    RECOMENDAR_URL=http://IP-DE-CARLA:8002
    ```

    Carla debe publicar el puerto y permitir las conexiones en su firewall. Así los servicios siguen en laptops separadas y se comunican por la red.


**c)** La WiFi del campus aísla clientes («AP isolation»). `ping' entre alumnos falla. ¿Pueden hacer la práctica tal cual? Si no, propongan *un* plan B de laboratorio que preserve la lección «procesos separados» (aunque no sea WiFi del salón).

    c) Si la WiFi bloquea las conexiones entre alumnos, no pueden comunicarse entre sí tal como está planteado. Un plan de laboratorio sería levantar los tres contenedores en una sola computadora, dentro de la red de Compose. Seguirían siendo procesos y servicios separados, aunque estén en el mismo equipo.

## 8 — El front que conoce demasiado (10 puntos)

El HTML hace esto al enviar el formulario:

    ┌────
    │ await fetch("http://192.168.1.20:8002/sugerir", { ... }); // Recomendar
    │ await fetch("http://192.168.1.30:8001/pedidos", { ... }); // Pedidos
    └────

  El autor dice: «Más rápido: me salto el gateway.»

**a)** Listen *tres* problemas (seguridad, cambio de IP, orden de llamadas, consistencia del folio, CORS, etc.).

    a) Hay varios problemas:

    1. El navegador conoce direcciones internas e IP que pueden cambiar.
    2. Al llamar directamente a los servicios, se expone más la estructura interna y cada uno tendría que protegerse por separado.
    3. La página tendría que manejar permisos de acceso entre orígenes, conocido como CORS.
    4. El navegador podría pedir primero la recomendación y luego crear el pedido, pero si la segunda llamada falla, la primera ya ocurrió y no hay una operación completa.
    5. Si el navegador o Pedidos crean folios sin coordinación, se pueden duplicar o quedar sin correspondencia.

**b)** Rediseñen la secuencia correcta con gateway: *una* llamada desde el navegador. ¿Quién habla con Recomendar y por qué no el navegador?

b) La secuencia correcta es una sola llamada desde el navegador:

    ```text
    Navegador → Gateway → Pedidos → Recomendar
    ```

    El navegador llama al Gateway. Pedidos habla con Recomendar porque es quien crea y coordina el pedido; así el cliente no tiene que conocer las direcciones internas ni coordinar dos operaciones por separado.

**c)** El selector de modelo (`arbol=|=bosque=|=red') va en el JSON. Si el front llama directo a Recomendar *y* a Pedidos, ¿quién debería crear el folio para no duplicar lógica? ¿Qué invariante rompen si los dos «crean» algo?

    c) Pedidos debería crear el folio, porque es el servicio responsable de crear el pedido. Si Recomendar también creara uno, ambos podrían asignar identificadores distintos o guardar registros diferentes para la misma solicitud. Se rompería la regla de que cada pedido tiene un solo folio y una única creación confirmada.

## 9 — El LLM vendedor (10 puntos)

 Producto: tienda + envíos.

  • Modelo `.joblib': medio de transporte.
  • LLM: texto para convencer al cliente en la ficha del producto.

  Un arquitecto propone *un solo* microservicio `cerebro' que: recibe el
  carrito, elige el medio con el árbol *y* genera el pitch de ventas con
  el LLM, todo en la misma petición `/inteligente'.

**a)** Critiquen el nombre y el corte. ¿Qué dos oficios distintos mezclaron? ¿Qué falla cuando el LLM tarda 8 s y el despacho necesita responder en < 500 ms?

    a) “Cerebro” es un nombre vago: no explica qué hace el servicio. El diseño mezcla dos trabajos distintos: recomendar un transporte para un pedido y generar texto de venta para una ficha de producto. Si el LLM tarda ocho segundos y el envío debe responder en menos de medio segundo, esperar al LLM retrasa una operación que no lo necesita.

**b)** Propongan dos endpoints (o dos servicios) y digan cuál usa el *front de tienda* y cuál el *flujo de pedido/envío*.

b) Separaría las operaciones, por ejemplo:

    - `POST /recomendar-envio`: lo usa el flujo de pedido para elegir el medio y continuar con la entrega.
    - `POST /generar-descripcion`: lo usa el front de tienda para pedir un texto de venta.

    La recomendación del transporte no debe depender de que el texto de venta termine.

**c)** El LLM vive en un server con GPU en otra red. El front de tienda ¿apunta a la GPU o al gateway? Si mañana cambian de proveedor LLM (otro host), ¿qué archivo/config quieren tocar *una sola vez*?

    c) El front debe llamar al Gateway, no directamente a la GPU. El Gateway o un servicio detrás de él se encarga de hablar con el proveedor del LLM. Si mañana cambia el proveedor, se actualiza la dirección y configuración en un solo lugar —la configuración del servicio que llama al LLM— y no en cada navegador.

## 10 — El inversionista y la semana imposible (10 puntos)

Hoy:

  • Panel interno: monolito Django (funciona, poco tráfico).
  • App clientes: gateway + pedidos + recomendar.
  • Idea: LLM de ventas (aún no).
  • Equipo: 5 personas.
  • Inversionista: «Todo a microservicios en 7 días, incluido el panel,
    o no hay dinero.»

**a)** Escriban la respuesta al inversionista (máx. 8 líneas) con postura *y* riesgo concreto si obedecen a ciegas.

    a) Respuesta al inversionista, en máximo ocho líneas**

    > No recomiendo dividir todo el panel en microservicios en siete días.  
    > El panel funciona y tiene poco tráfico, así que el beneficio inmediato sería limitado.  
    > Una migración apresurada puede interrumpir el panel y los pedidos existentes.  
    > También repartiría a cinco personas entre demasiadas piezas y cambios simultáneos.  
    > Esta semana priorizaría proteger la entrada pública y actualizar el modelo sin tumbar Pedidos.  
    > Después mediríamos qué parte del panel causa más demoras o errores.  
    > Dividiríamos esa parte si los datos muestran un problema real.

**b)** Ordenen *estas cuatro* iniciativas de más a menos urgente para *esta* semana y justifiquen el orden (no el catálogo soñado):

  1. Partir el panel Django en 6 microservicios.
  2. Sacar el reentrenamiento del `.joblib' a un pipeline que no tumbe
     Pedidos.
  3. Meter auth + rate limit en el gateway público.
  4. Subir el LLM de ventas a producción sin timeouts ni plan B.

    b) Orden de más a menos urgente esta semana**

    1. **Añadir autenticación y límite de solicitudes al Gateway público.** Está expuesto a clientes y conviene controlar quién lo usa y evitar un exceso de solicitudes.
    2. **Separar el reentrenamiento del `.joblib` para que no tumbe Pedidos.** Cambiar el modelo no debería interrumpir la creación de pedidos.
    3. **Partir el panel Django en seis microservicios.** No hay indicios de que sea urgente: funciona y tiene poco tráfico. Primero mediría dónde está el problema.
    4. **Subir el LLM de ventas sin tiempos límite ni plan B.** Es la opción más riesgosa: una operación lenta podría dejar solicitudes esperando y no hay todavía un mecanismo para manejar la demora. Antes de publicarlo hacen falta límites de espera y una respuesta alternativa.

**c)**  Inventen *una* métrica que les diga «ya toca partir X del monolito» (no «porque está de moda»). Tiene que ser observable (tiempo, errores, despliegues, equipo…).

    c) Una métrica podría ser: **cuántos despliegues de una parte del panel obligan a detener o reiniciar todo Django al mes**. Si ocurre con frecuencia y afecta a usuarios, sería una señal observable de que conviene separar esa parte. También habría que comprobar que el costo de separarla se justifique.

**d)** Cierren con una frase propia (no copien el apunte) que capture: ¿microservicios son el objetivo o la herramienta?

    d) Los microservicios son una herramienta para resolver problemas de independencia y operación; el objetivo es que el sistema sea confiable y fácil de cambiar.
