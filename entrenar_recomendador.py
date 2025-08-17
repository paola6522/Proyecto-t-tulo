import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import joblib

# 1. Cargar datasets
books = pd.read_csv('Books.csv', sep=';', encoding='latin-1', on_bad_lines='skip')
ratings = pd.read_csv('Ratings.csv', sep=';', encoding='latin-1', on_bad_lines='skip')

# 2. Limpiar datos
# Extrae solo lo necesario del dataset
books = books[['ISBN', 'Book-Title', 'Book-Author']]
ratings = ratings[['User-ID', 'ISBN', 'Book-Rating']]
ratings = ratings[ratings['Book-Rating'] > 0]

# 2.1 Filtrar usuarios con al menos 50 valoraciones y libros con al menos 50 votos
usuario_counts = ratings['User-ID'].value_counts()
libros_counts = ratings['ISBN'].value_counts()

ratings_filtrados = ratings[
    ratings['User-ID'].isin(usuario_counts[usuario_counts >= 50].index) &
    ratings['ISBN'].isin(libros_counts[libros_counts >= 50].index)
]

# 3. Merge
df = ratings_filtrados.merge(books, on='ISBN')
df = df.dropna()

# 4. Crear matriz
pivot = df.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating').fillna(0)

# 5. Modelo KNN
from sklearn.neighbors import NearestNeighbors
model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
model_knn.fit(pivot.values)

# 6. Guardar modelo
import joblib
joblib.dump(model_knn, 'modelo_recomendador.pkl')
pivot.to_pickle('pivot_matrix.pkl')

# Guardar diccionario de títulos y autores
libros_info = dict(zip(books['Book-Title'], books['Book-Author']))
joblib.dump(libros_info, 'info_libros.pkl')

print("Modelo entrenado y guardado correctamente.")


