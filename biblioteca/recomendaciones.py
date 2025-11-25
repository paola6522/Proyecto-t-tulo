# biblioteca/recomendaciones.py
import joblib
from pathlib import Path
from django.conf import settings

# ---------------------------
# RUTAS ABSOLUTAS (Render-safe)
# ---------------------------
ML_DIR = Path(settings.BASE_DIR) / "biblioteca" / "ml"

MODEL_PATH = ML_DIR / "modelo_recomendador_knn.pkl"
MAPEOS_PATH = ML_DIR / "mapeos.pkl"
BOOK_META_PATH = ML_DIR / "book_meta.pkl"
PIVOT_PATH = ML_DIR / "pivot_centered.pkl"

# ---------------------------
# CARGA PEREZOSA (lazy load)
# ---------------------------
_model_knn = None
_isbn_index = None
_index_isbn = None
_book_meta = None
_pivot = None


def _load_artifacts():
    """
    Carga modelo y artefactos solo cuando se necesiten.
    Evita que migrate/collectstatic revienten en Render.
    """
    global _model_knn, _isbn_index, _index_isbn, _book_meta, _pivot

    if _model_knn is None:
        _model_knn = joblib.load(MODEL_PATH)

    if _isbn_index is None or _index_isbn is None:
        mapeos = joblib.load(MAPEOS_PATH)
        _isbn_index = mapeos["isbn_index"]   # ej: Series isbn -> fila
        _index_isbn = mapeos["index_isbn"]   # ej: dict fila -> isbn

    if _book_meta is None:
        _book_meta = joblib.load(BOOK_META_PATH)  # DataFrame index=ISBN

    if _pivot is None:
        _pivot = joblib.load(PIVOT_PATH)          # DataFrame/array ya centrado
        # si es DF, aseguramos NaN fuera
        try:
            _pivot = _pivot.fillna(0)
        except AttributeError:
            pass


def recomendar_para_usuario(isbns_usuario, top_n=12, vecinos=30):
    _load_artifacts()

    model_knn = _model_knn
    isbn_index = _isbn_index
    index_isbn = _index_isbn
    book_meta = _book_meta
    pivot = _pivot

    # quitar duplicados manteniendo orden
    isbns_usuario = list(dict.fromkeys(isbns_usuario))

    # quedarnos solo con ISBN presentes en el modelo
    # (si isbn_index es Series, su index son los ISBN válidos)
    base = [i for i in isbns_usuario if i in isbn_index.index]
    if not base:
        return []

    scores = {}

    for isbn in base:
        fila = int(isbn_index[isbn])

        # vector sin NaN
        vector = pivot.iloc[fila, :].values.reshape(1, -1)

        n_vecinos = min(vecinos + 1, pivot.shape[0])
        distances, indices = model_knn.kneighbors(vector, n_neighbors=n_vecinos)

        for dist, idx_vecino in zip(distances[0], indices[0]):
            vecino_isbn = index_isbn[int(idx_vecino)]

            # saltar mismo libro y libros ya del usuario
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


