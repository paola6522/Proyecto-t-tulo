import os
import django
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import joblib
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letrasproject.settings')
django.setup()

from biblioteca.models import LibroLeido, DiarioLector

BASE_DIR = Path(__file__).resolve().parent

# Rutas de datasets externos (Book-Crossing)
BOOKS_CSV = BASE_DIR / 'Books.csv'
BOOKS_ES = BASE_DIR / 'Books_espanol.csv'   # <<--- nuevo dataset en español
RATINGS_CSV = BASE_DIR / 'Ratings.csv'

# ------------------------------
# 1. Cargar datos externos base
# ------------------------------
print("Cargando datasets externos...")

books = pd.read_csv(BOOKS_CSV, sep=';', encoding='latin-1', on_bad_lines='skip', low_memory=False)
ratings_ext = pd.read_csv(RATINGS_CSV, sep=';', encoding='latin-1', on_bad_lines='skip', low_memory=False)

books = books[['ISBN', 'Book-Title', 'Book-Author']].dropna().drop_duplicates('ISBN')
ratings_ext = ratings_ext[['User-ID', 'ISBN', 'Book-Rating']].dropna()
ratings_ext = ratings_ext[ratings_ext['Book-Rating'] > 0]

# ------------------------------
# 2. Añadir libros en español
# ------------------------------
if BOOKS_ES.exists():
    print("🇪🇸 Añadiendo libros en español...")
    books_es = pd.read_csv(BOOKS_ES, sep=';', encoding='utf-8')
    books = pd.concat([books, books_es], ignore_index=True).drop_duplicates('ISBN')
    print(f"Total libros (internacional + español): {len(books)}")
else:
    print("No se encontró Books_espanol.csv, usando solo dataset internacional.")

# ------------------------------
# 3. Ratings desde la app
# ------------------------------
print("Construyendo ratings desde la app...")

rows = []

# Desde DiarioLector (puntuación explícita)
diarios = (DiarioLector.objects
           .select_related('usuario', 'libro_leido')
           .exclude(puntuacion=0))

for d in diarios:
    isbn = (d.libro_leido.isbn or "").strip()
    if not isbn:
        continue

    score_1_10 = max(1, int(d.puntuacion * 2))
    rows.append({
        'User-ID': f"app_{d.usuario_id}",
        'ISBN': isbn,
        'Book-Rating': score_1_10,
    })

# Inferir rating según estado
estado_a_rating = {
    'pendiente': 0,
    'iniciado': 6,
    'en_curso': 7,
    'finalizado': 9,
    'abandonado': 3,
}

libros_app = (LibroLeido.objects
              .select_related('usuario')
              .exclude(isbn__isnull=True)
              .exclude(isbn__exact=''))

for libro in libros_app:
    isbn = (libro.isbn or "").strip()
    if not isbn:
        continue

    user_id = f"app_{libro.usuario_id}"
    ya_tiene = any((r['User-ID'] == user_id and r['ISBN'] == isbn) for r in rows)
    if ya_tiene:
        continue

    r_estado = estado_a_rating.get(libro.estado, 0)
    if r_estado > 0:
        rows.append({'User-ID': user_id, 'ISBN': isbn, 'Book-Rating': r_estado})

ratings_app = pd.DataFrame(rows)
print(f"Ratings desde la app: {len(ratings_app)}")

# ------------------------------
# 4. Unir datasets
# ------------------------------
ratings = pd.concat([ratings_ext, ratings_app], ignore_index=True)
ratings = ratings.dropna(subset=['User-ID', 'ISBN', 'Book-Rating'])

# Solo nos quedamos con ratings de libros que existen en 'books'
df = ratings.merge(books, on='ISBN', how='inner')
df = df.dropna(subset=['ISBN', 'User-ID', 'Book-Rating']).drop_duplicates(['User-ID', 'ISBN'])


# ------------------------------
# 5. Filtrado
# ------------------------------
min_user_r = 20
min_item_r = 10

u_cnt = df['User-ID'].value_counts()
i_cnt = df['ISBN'].value_counts()

df = df[df['User-ID'].isin(u_cnt[u_cnt >= min_user_r].index)]
df = df[df['ISBN'].isin(i_cnt[i_cnt >= min_item_r].index)]

if df.empty:
    raise SystemExit("No hay suficientes datos después del filtrado.")

print(f"Usuarios: {df['User-ID'].nunique()} | Libros: {df['ISBN'].nunique()}")

# ------------------------------
# 6. Matriz centrada por usuario
# ------------------------------
user_mean = df.groupby('User-ID')['Book-Rating'].mean()
df = df.join(user_mean, on='User-ID', rsuffix='_USER_MEAN')
df['adj_rating'] = df['Book-Rating'] - df['Book-Rating_USER_MEAN']

pivot = df.pivot_table(index='ISBN', columns='User-ID', values='adj_rating', aggfunc='mean').fillna(0)
pivot_sparse = csr_matrix(pivot.values)

# ------------------------------
# 7. Entrenar modelo KNN
# ------------------------------
print("Entrenando modelo KNN...")

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=30, n_jobs=-1)
model_knn.fit(pivot_sparse)

# ------------------------------
# 8. Guardar artefactos
# ------------------------------
isbn_index = pd.Series(range(pivot.shape[0]), index=pivot.index)
index_isbn = pd.Series(pivot.index, index=range(pivot.shape[0]))
books_idx = books.set_index('ISBN')
book_meta = books_idx.reindex(pivot.index)[['Book-Title', 'Book-Author']].fillna('Desconocido')


joblib.dump(model_knn, BASE_DIR / 'modelo_recomendador_knn.pkl')
joblib.dump({'isbn_index': isbn_index, 'index_isbn': index_isbn}, BASE_DIR / 'mapeos.pkl')
book_meta.to_pickle(BASE_DIR / 'book_meta.pkl')
pivot.to_pickle(BASE_DIR / 'pivot_centered.pkl')

print("Modelo actualizado con libros en español y datos de usuarios.")

