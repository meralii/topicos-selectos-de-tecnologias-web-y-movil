Actividad individual: lo que hay detras de la implementacion

Nombre: Kelly Merali Rodriguez Reyna
Matricula: 22121336


# A
## A1
Ana piensa que con Docker el venv sobra, y Luis cree que el venv aguanta todo el trafico. Los dos estan mal. El venv nada mas sirve en local para que las librerias no choquen en la compu. El contenedor aisla todo el sistema operativo para que la app jale igual en donde sea que la subas.

## A2
**a)** No se perdio su codigo, la carpeta venv solo guarda las librerias que descargamos de internet, no nuestros scripts.
**b)** Nomas ocupa volver a crear el entorno y correr pip install -r requirements.txt para descargar todo de nuevo.
**c)** Activar el entorno solo le cambia las variables a esa terminal para usar el Python aislado. Si cierras la terminal se borra esa configuracion, por eso hay que activarlo cada que abres una nueva.

## A3
**a)** La carpeta app solo existe adentro del contenedor. El COPY  lo que hace es clonar los archivos de nuestra compu al contenedor.
**b)** Ignorar venv es para no meter al contenedor librerias de mi compu que igual y no jalan en Linux. Ignorar db.sqlite3 evita que mis datos de prueba sobreescriban la base de datos real.

# B
## B1
**a)** Si dejamos la regla en el JS y luego sacamos app movil, vamos a tener codigo repetido. Si hay un cambio, hay que cambiar la web y obligar a todos a actualizar la app de su cel.
**b)** El front se cambia facil porque el backend es la unica fuente de verdad. El backend nomas avienta datos crudos (en JSON) y el front ya ve como acomodarlos visualmente.

## B2
La app movil va a tronar porque va a buscar un dato que ya no existe. El contrato es el acuerdo estricto de como se mandan los datos entre front y back. La version sirve para seguirle mandando la respuesta vieja a las apps que no se han actualizado, mientras sacamos lo nuevo para la web.

## B3
No estoy de acuerdo. Las validaciones del front son nomas visuales para ayudar al usuario. Las del backend son a fuerza para cuidar la base de datos, porque no podemos confiar en lo que manda el cliente, cualquiera podria saltarse el front.

# C
## C1
**a)** Escalar vertical es meterle mas RAM o mejor procesador a la misma compu. Horizontal es poner mas compus o contenedores a trabajar al mismo tiempo.
**b)** El limite vertical es el presupuesto y lo que aguante el hardware fisicamente.
**c)** Nginx jala como un semaforo, repartiendo el trafico parejo entre las 3 copias para que no se sature una sola.

## C2
**a)** Como la RAM de cada contenedor esta separada, el diccionario nomas se guardo en la memoria de la copia que recibio el registro.
**b)** Porque Gunicorn abre varios procesos (workers), y si la peticion le cae a otro worker distinto, su memoria esta en blanco.
**c)** No tiene razon, Docker no rompio nada. El error es de nosotros por guardar datos en RAM cuando tenemos varias copias corriendo.

## C3
Falla por lo mismo, los contenedores no comparten variables. La sesion si jala porque Django la guarda directo en la base de datos, asi cualquier copia puede ir a buscar la info.

## C4
**a)** Se mandarian 5 correos repetidos al cliente. Esa tarea deberia estar en un proceso aparte que solo se ejecute una vez.
**c)** Se abririan 80 conexiones. Si metemos copias a lo loco, saturamos PostgreSQL y tumbamos todo. SQLite no sirve con varias copias porque bloquea todo el archivo cuando alguien escribe, y no deja hacer nada en paralelo.

# D
## D1
**a)** Ese 99% es engañoso porque el modelo se evaluo con los datos que ya memorizo, no esta prediciendo nada nuevo.
**b)** El train_test_split sirve para apartar datos y ver como reacciona el modelo con info que nunca ha visto en su vida.
**c)** Stratify cuida que se mantenga la proporcion. Como hay bien poquitos drones, sin stratify el set de prueba podria quedarse sin ningun caso de dron.

## D2
Usar 0, 1 y 2 le haria creer al modelo que el viento (2) vale mas que la lluvia (1) como si fuera una jerarquia. El one-hot arregla esto haciendo columnas separadas de falso/verdadero. Se usa el Pipeline para asegurar que cualquier paquete nuevo pase exactamente por las mismas conversiones antes de predecir.

## D3
**a)** El arbol sin limite acierta menos porque hace overfitting (se sobreajusta), memoriza ruido en vez de aprender las reglas.
**b)** Nos quedamos con el de 8 porque es muchisimo mas ligero (47 hojas vs 92) y ese extra de exactitud que da el de 10 no vale la pena para lo pesado que se vuelve.

## D4
**a)** Precision es que, de todas las veces que dijo dron, le atino el 84%. Recall es que de todos los envios que si eran dron en la realidad, logro detectar el 90.5%.
**b)** Mandar un dron cuando no tocaba sale mas caro (error de Precision). No mandar uno que si podia irse en dron es error de Recall.
**c)** No llega al 100% porque estaria sobreajustado; la vida real tiene anomalias y forzar la perfeccion echa a perder al modelo.

## D5
El Random Forest esta bien pesado (60 MB) y nos acabaria la memoria de las copias. Aparte es una caja negra, en el arbol si podemos revisar la logica. En Django no cambia gran cosa, solo importas el archivo nuevo y mandas a llamar la misma funcion para predecir.

# E
## E1
**a)** Seguro el modelo no vio casos de viajes de dron en la madrugada cuando lo entrenaron y no sabe que hacer.
**b)** La IA solo da probabilidades, pero las reglas del negocio son restricciones duras que se tienen que cumplir si o si.
**c)** Las reglas se ponen aparte para poder forzar decisiones por encima del modelo sin ensuciar sus matematicas.

## E2
No es contradiccion. Un pedido son datos en tiempo real, el modelo ya es un archivo fijo que solo se lee. Si no lo dejamos en cache, cada peticion tendria que estar leyendo el disco duro y el servidor se haria lentisimo.

## E3
Como en el txt no le pusieron la version exacta, Docker bajo la version mas nueva y rompio compatibilidad con el archivo viejo. Se evita anclando la version ej. scikit-learn==1.9.0. Esto va de la mano con la seccion A: el contenedor solo funciona perfecto si le das las instrucciones exactas.

# F
## F1
**a)** Ocupamos hacer el patron Adaptador para que reciba la respuesta de la IA y la traduzca a lo que entiende la plataforma. Todo lo demas se queda igual.
**b)** La IA nada mas decide el vehiculo. Todo el resto del viaje como hacer el plan, calcular el costo y crear los objetos aun ocupa nuestro diseño.
**c)** 1. Si la api de la IA se cae, le metemos un adaptador de emergencia y la app sigue jalando. 2. Si despues cambiamos de proveedor de IA, nomas cambiamos ese archivo adaptador y el resto del codigo ni se entera. Por eso los patrones siguen sirviendo.