import pandas as pd
import joblib
from sklearn.model_selection import train_test_split

datos = pd.read_csv('../envios_medios.csv')

X = datos.drop("medio_recomendado", axis=1)
y = datos["medio_recomendado"]
X_entreno, X_prueba, y_entreno, y_prueba = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)


modelo = joblib.load("../modelo_medios.joblib")
y_pred = modelo.predict(X_prueba)

analisis = X_prueba.assign(real=y_prueba, predicho=y_pred)
errores = analisis[analisis["real"] != analisis["predicho"]]

print("--- TOP 5 CONFUSIONES ---")
resumen_errores = errores.groupby(["real", "predicho"]).size().sort_values(ascending=False).head(5)
print(resumen_errores)

print("\n--- MOTOS ENVIADAS A DRON ---")
motos_a_dron = errores[(errores["real"] == "moto") & (errores["predicho"] == "dron")]
print(f"Total: {len(motos_a_dron)}")
print(motos_a_dron[["hora_salida", "peso", "distancia"]].head())