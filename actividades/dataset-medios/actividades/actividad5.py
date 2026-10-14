import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

datos = pd.read_csv('../envios_medios.csv')

X = datos.drop("medio_recomendado", axis=1)
y = datos["medio_recomendado"]


X_entreno, X_prueba, y_entreno, y_prueba = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)


NUMERICAS = ["distancia", "peso", "volumen", "hora_salida"]
CATEGORICAS = ["clima", "zona_destino"]

preparacion = ColumnTransformer([
    ("num", StandardScaler(), NUMERICAS),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS)
])


pipeline_normal = Pipeline([
    ("preparacion", preparacion),
    ("arbol", DecisionTreeClassifier(random_state=42))
])
pipeline_normal.fit(X_entreno, y_entreno)
pred_normal = pipeline_normal.predict(X_prueba)

print("--- SIN BALANCEAR ---")
print(f"Exactitud: {accuracy_score(y_prueba, pred_normal):.4f}")
print(classification_report(y_prueba, pred_normal))


pipeline_pesado = Pipeline([
    ("preparacion", preparacion),
    ("arbol", DecisionTreeClassifier(class_weight="balanced", random_state=42))
])
pipeline_pesado.fit(X_entreno, y_entreno)
pred_pesado = pipeline_pesado.predict(X_prueba)

print("\n--- CON BALANCEO (CLASS WEIGHT) ---")
print(f"Exactitud: {accuracy_score(y_prueba, pred_pesado):.4f}")
print(classification_report(y_prueba, pred_pesado))