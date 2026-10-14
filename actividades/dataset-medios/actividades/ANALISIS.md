# Análisis del Dataset de Envíos y Modelos Predictivos

## Actividad 1 — El retrato del dataset

* **1. Mis suposiciones iniciales (Predicción):**
  * Ante condiciones de lluvia, anticipé que predominarían los vehículos pesados y cerrados como la camioneta.
  * Para los traslados dentro del centro urbano, supuse que la bicicleta y la moto acapararían las rutas.
  * Calculé que la distancia máxima abarcada por una bicicleta rondaría un tope de 5 a 7 km.
  * Consideré seguro hallar anomalías o excepciones debido al ruido inherente de cualquier entorno operativo real.

* **2. Verificación empírica (Comprobación):**
  * **Clima frente al medio:** Al llover, la camioneta acapara el 70.83% de los trayectos y la moto el 29.17%, anulando totalmente el uso de drones y bicicletas ($0\%$).
  * **Zona céntrica frente al medio:** En el núcleo urbano, la bicicleta lidera con el 74.07%, seguida de la moto con el 21.01% y la camioneta con el 4.90%, sin presencia de drones.
  * **Métrica límite:** El registro máximo de distancia verificado para la bicicleta se sitúa exactamente en los 7.00 km.
  * **Evaluación:** Las restricciones físicas estimadas coincidieron con la realidad de los datos; el clima desfavorable frena por completo a los transportes descubiertos.

* **3. Criterio analítico y respuestas (Decisión):**
  1. *Zonas y climas excluyentes para el dron:* El dron jamás interviene en el centro ni bajo precipitaciones. Esto obedece directamente al filtro de seguridad y normativa del espacio aéreo (`paquete["clima"] != "despejado" o paquete["zona_destino"] == "centro"`).
  2. *Restricción en la periferia para bicicletas:* La variable determinante es la distancia (`distancia_km`). Al mantenerse el tope de la bicicleta en 7.00 km, resulta físicamente incompatible con las longitudes de la periferia.
  3. *Límites discernibles:* Es viable deducir los topes de distancia, peso y volumen inspeccionando los valores máximos tabulados. No obstante, las restricciones compuestas (como la inhabilitación nocturna o climática del dron) escapan a una simple lectura aislada por requerir un cruce multivariable.
  4. *Camionetas en trayectos breves ($< 2\text{ km}$):* Se detectaron 174 casos de camionetas en distancias cortas. Aquellas que rebasan los máximos operativos de una moto (25 kg o 90 L) están plenamente justificadas; las restantes obedecen a contingencias climáticas (lluvia) que neutralizan alternativas ligeras.
  * *Reflexión crítica:* Partir exclusivamente de un archivo histórico permite extraer únicamente contornos absolutos. Delegar toda la directriz operativa en un modelo predictivo conlleva el riesgo latente de que este reproduzca sesgos o correlaciones espurias en lugar de blindar la operación con reglas estrictas de seguridad.

---

## Actividad 2 — La hora y el dron

* **1. Mis suposiciones iniciales (Predicción):**
  * A las 03:00 horas la actividad de drones será nula a causa de la restricción de visibilidad nocturna.
  * La proporción global de envíos nocturnos se mantendrá en una franja reducida, estimada entre el 10% y el 15%.

* **2. Verificación empírica (Comprobación):**
  * **Cruce horario:** A las 03:00 horas el registro de envíos mediante dron arroja un valor absoluto de cero.
  * **Volumen nocturno (antes de las 06:00 o desde las 21:00):** Representa el 10.96% del total.
  * **Evaluación:** La estimación inicial sobre la baja incidencia operativa durante la noche demostró ser sumamente acertada.

* **3. Criterio analítico y respuestas (Decisión):**
  1. *Ausencia nocturna de drones:* La restricción opera rigurosamente entre las 21:00 y las 05:59 horas, alineándose con la condición lógica programada en el sistema.
  2. *Proporción diurna frente a nocturna:* Al representar cerca del 11%, el volumen nocturno otorga una señal débil al algoritmo de aprendizaje, restando robustez predictiva frente al flujo diurno masivo.
  3. *Comportamiento de la bicicleta a las 20:00:* Su descenso drástico previo a las 21:00 responde a la política de mitigación de riesgos laborales ante escenarios de baja visibilidad.
  4. *Limitación temporal del árbol de decisión:* Al basarse en divisiones escalares simples de tipo menor o mayor igual, una condición cíclica o de intervalo nocturno fragmentado exige al menos dos particiones lógicas independientes.
  5. *Reflexión crítica:* Una solución óptima consistiría en incorporar una variable booleana explícita (`es_de_noche`). Su eficacia se comprobaría evaluando su peso directo dentro de las métricas de importancia de atributos del modelo y la reducción consecuente de falsos positivos.

---

## Actividad 3 — Anatomía de los errores

* **1. Mis suposiciones iniciales (Predicción):**
  * Las confusiones más recurrentes se concentrarán en las fronteras operativas de capacidad entre vehículos de características contiguas, específicamente entre la motocicleta y la bicicleta.

* **2. Verificación empírica (Comprobación):**
  * **Principales discrepancias del clasificador:** Motocicletas catalogadas erróneamente como bicicletas (23 casos), camionetas etiquetadas como motocicletas (16 casos) y bicicletas tratadas como motocicletas (16 casos).
  * **Evaluación:** El pronóstico se confirmó; las mayores imprecisiones ocurren en los umbrales limítrofes de operación.

* **3. Criterio analítico y respuestas (Decisión):**
  1. *Naturaleza de los fallos:* La concentración de errores en rangos adyacentes evidencia que las zonas grises (como trayectos cercanos a los 7 km) exigen mayor precisión en los metadatos del paquete.
  2. *Desviaciones hacia el dron:* De los 29 equívocos donde el modelo sugirió un dron para un servicio de moto, 26 correspondieron a horarios nocturnos. Si bien la capa de validación comercial neutraliza estos casos mediante filtros estrictos, los 3 restantes obedecen a envíos situados exactamente en el umbral de los 2.5 kg.
  3. *Desviaciones hacia la bicicleta:* Derivan del solapamiento metadatos-distancia alrededor de los 7 km, donde el factor diferenciador suele radicar en volúmenes o pesos específicos incompatibles con la capacidad ciclista.
  4. *Reflexión crítica:* Enfocaría los esfuerzos en corregir los falsos positivos de los drones. Añadir variables contextuales específicas (como la franja nocturna) previene que el algoritmo generalice erróneamente, salvaguardando los recursos operativos de la empresa sin recargar excesivamente la capa de validación dura.

---

## Actividad 4 — Qué columnas usa de verdad el modelo

* **1. Mis suposiciones iniciales (Predicción):**
  * *Variables de mayor relevancia:* Distancia, peso y volumen del paquete.
  * *Variable de menor relevancia:* Zona de destino.

* **2. Verificación empírica (Comprobación):**
  * **Jerarquía de importancia según scikit-learn:** `distancia_km` (0.322), `volumen_l` (0.193), `refrigerado` (0.131) y `peso_kg` (0.126).
  * **Evaluación:** Acerté al priorizar las magnitudes físicas, aunque resultó llamativo el peso crítico otorgado al requerimiento de refrigeración en las ramificaciones superiores.

* **3. Criterio analítico y respuestas (Decisión):**
  1. *Consistencia del Top 4:* Distancia, volumen, refrigeración y peso coinciden plenamente con las restricciones primordiales del negocio y los planteamientos iniciales.
  2. *Sensibilidad ante la supresión de atributos:* Retirar la distancia degradaría drásticamente la tasa de acierto global al ser el eje estructurante de la red logística, a diferencia de metadatos geográficos secundarios que aportan un impacto marginal.
  3. *El caso de la zona de destino:* Su aparente irrelevancia numérica en los coeficientes se debe a que el modelo infiere implícitamente la ubicación mediante fuertes correlaciones cruzadas (por ejemplo, trayectos breves asociados al centro urbano).
  4. *Reflexión crítica:* Cuestionar la recolección de la zona geográfica por su aparente baja jerarquía en el árbol sería un error. Los sistemas periféricos de posicionamiento global, la emisión fiscal y los tableros gerenciales de control requieren indefectiblemente este parámetro independientemente de la lógica predictiva del clasificador.

---

## Actividad 5 — El dron es minoría: ¿hay que balancear el dataset?

### Parte A — Consideraciones conceptuales previas
1. Un esquema predictivo que omitiera por completo la clase minoritaria del dron alcanzaría de forma artificial una exactitud del 90.5%. Esto demuestra que el indicador de *accuracy* disimula la inutilidad operativa ante clases minoritarias, haciendo indispensable el uso de métricas específicas como *Precision*, *Recall* y *F1-Score*.
2. La escasez de registros de drones responde fielmente a la realidad estructural y normativa de la flota actual, reflejando un entorno operativo fidedigno y no un sesgo de captura.
3. Cualquier técnica de balanceo debe aplicarse de forma estricta única y exclusivamente sobre el conjunto de entrenamiento posterior a la partición; el segmento de evaluación intocable (*test set*) jamás debe alterarse para conservar una muestra imparcial de la realidad productiva.

### Parte B — Comparativa de estrategias de balanceo
*Evaluación ejecutada sobre un conjunto estándar invariable de 2,000 muestras de prueba:*

| Estrategia aplicada | Exactitud global | Precisión (Dron) | Exhaustividad (Dron) | Predicciones de dron (Real: 190) | Sugerencias no viables |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Sin balancear** | 0.92 | 0.84 | 0.91 | 205 | 31 |
| **Con ponderación (`class_weight`)** | 0.90 | 0.77 | 1.00 | 248 | 35 |

### Parte C — Interpretación de resultados
1. *Precisión frente a Exhaustividad:* Al penalizar los errores sobre la clase minoritaria, el índice de recuperación (*Recall*) se eleva al máximo posible ($1.00$), detectando la totalidad de escenarios óptimos para drones; sin embargo, la precisión desciende a 0.77 debido al incremento de falsos positivos por sobreestimación.
2. *Riesgo del submuestreo (*undersampling*):* Descartar masivamente datos de las clases mayoritarias para equiparar volúmenes destruye patrones de comportamiento valiosos acumulados por el modelo.
3. *Equivalencia metodológica:* Las técnicas de sobremuestreo y la ponderación de clases operan bajo un principio matemático idéntico: incrementar el coste del error ante la omisión de la clase minoritaria.
4. *Distorsión de la confianza:* Tras aplicar esquemas de equilibrado artificial, el porcentaje de confianza reportado deja de representar una probabilidad estadística real al haber alterado las proporciones originales del entorno.

### Parte D — Recomendación final para la plataforma
Se aconseja **preservar el esquema sin balancear**, evitando inflar artificialmente la tasa de sugerencias no viables. 

Desde una perspectiva de gestión de riesgos e infraestructura, un falso positivo en la asignación de drones conlleva implicaciones severas de costos, riesgos normativos y vulnerabilidad de equipos ante contingencias meteorológicas. La precisión elevada (0.84) del esquema original salvaguarda de manera más eficiente los intereses de la empresa. 

Elevar de forma forzada la sensibilidad incrementa la emisión de sugerencias erróneas (llevando las predicciones de dron de 205 a 248 y elevando las recomendaciones inviables de 31 a 35), las cuales exigen un filtrado secundario de cómputo en el servidor backend. Si la flota de drones se expande a futuro, el flujo orgánico de transiciones comerciales reequilibrará de forma natural los datos históricos sin falsear las proporciones operativas.