import pandas as pd


datos = pd.read_csv('../envios_medios.csv')

print("--- CLIMA VS MEDIO ---")
print(pd.crosstab(datos["clima"], datos["medio_recomendado"], normalize="index") * 100)

print("\n--- ZONA VS MEDIO ---")
print(pd.crosstab(datos["zona_destino"], datos["medio_recomendado"], normalize="index") * 100)

print("\n--- LIMITES FISICOS (MIN, MEDIAN, MAX) ---")
print(datos.groupby("medio_recomendado")[["distancia", "peso", "volumen"]].agg(["min", "median", "max"]))


camionetas_cortas = datos[(datos["medio_recomendado"] == "camioneta") & (datos["distancia"] < 2)]
print(f"\nCamionetas en < 2km: {len(camionetas_cortas)}")