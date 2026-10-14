import pandas as pd
import matplotlib.pyplot as plt

datos = pd.read_csv('../envios_medios.csv')

tabla_hora = pd.crosstab(datos["hora_salida"], datos["medio_recomendado"])
print("--- DISTRIBUCION POR HORA ---")
print(tabla_hora)


tabla_hora.plot(kind="bar", stacked=True, figsize=(10,6)).figure.savefig("hora_vs_medio.png")
print("\nGráfica guardada como hora_vs_medio.png")

nocturnos = datos[(datos["hora_salida"] < 6) | (datos["hora_salida"] >= 21)]
porcentaje_noche = (len(nocturnos) / len(datos)) * 100
print(f"\nPorcentaje de envíos de noche: {porcentaje_noche:.2f}%")