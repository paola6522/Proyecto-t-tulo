import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / 'modelo_recomendador_knn.pkl'
MAPEOS_PATH = BASE_DIR / 'mapeos.pkl'
BOOK_META_PATH = BASE_DIR / 'book_meta.pkl'
PIVOT_PATH = BASE_DIR / 'pivot_centered.pkl'

# Carga modelo y artefactos
model_knn = joblib.load(MODEL_PATH)

mapeos = joblib.load(MAPEOS_PATH)
isbn_index = mapeos['isbn_index']
index_isbn = mapeos['index_isbn']

book_meta = pd.read_pickle(BOOK_META_PATH)

# 👇 CLAVE: rellenar NaN acá
pivot = pd.read_pickle(PIVOT_PATH).fillna(0)


def recomendar_para_usuario(isbns_usuario, top_n=12, vecinos=30):
    # Quitar duplicados
    isbns_usuario = list(dict.fromkeys(isbns_usuario))

    # Quedarnos solo con ISBN que existan en el modelo
    base = [i for i in isbns_usuario if i in isbn_index.index]
    if not base:
        return []

    scores = {}

    for isbn in base:
        fila = int(isbn_index[isbn])

        # Fila segura sin NaN
        vector = pivot.iloc[fila, :].values.reshape(1, -1)

        n_vecinos = min(vecinos + 1, pivot.shape[0])
        distances, indices = model_knn.kneighbors(vector, n_neighbors=n_vecinos)

        for dist, idx_vecino in zip(distances[0], indices[0]):
            vecino_isbn = index_isbn[int(idx_vecino)]

            # Saltar mismo libro y libros ya leídos
            if vecino_isbn == isbn or vecino_isbn in isbns_usuario:
                continue

            sim = 1.0 - float(dist)
            if sim <= 0:
                continue

            scores[vecino_isbn] = scores.get(vecino_isbn, 0.0) + sim

    if not scores:
        return []

    ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    recomendaciones = []
    for isbn, score in ordenados:
        if isbn in book_meta.index:
            meta = book_meta.loc[isbn]
            recomendaciones.append({
                "isbn": isbn,
                "title": str(meta.get("Book-Title", "")),
                "author": str(meta.get("Book-Author", "")),
                "score": round(float(score), 3),
            })

    return recomendaciones

