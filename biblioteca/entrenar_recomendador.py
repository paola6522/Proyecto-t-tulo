import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import joblib

# 1. Carga de datos
books = pd.read_csv('Books.csv', sep=';', encoding='latin-1', on_bad_lines='skip')
ratings = pd.read_csv('Ratings.csv', sep=';', encoding='latin-1', on_bad_lines='skip')

# 2. Limpieza
books = books[['ISBN', 'Book-Title', 'Book-Author']].dropna().drop_duplicates('ISBN')
ratings = ratings[['User-ID', 'ISBN', 'Book-Rating']].dropna()
ratings = ratings[ratings['Book-Rating'] > 0]

# 3. Filtrado
min_user_r = 30
min_item_r = 30
u_cnt = ratings['User-ID'].value_counts()
i_cnt = ratings['ISBN'].value_counts()

ratings = ratings[ratings['User-ID'].isin(u_cnt[u_cnt >= min_user_r].index)]
ratings = ratings[ratings['ISBN'].isin(i_cnt[i_cnt >= min_item_r].index)]

# 4. Merge y matriz pivot
df = ratings.merge(books, on='ISBN', how='inner')
user_mean = df.groupby('User-ID')['Book-Rating'].mean()
df = df.join(user_mean, on='User-ID', rsuffix='_USER_MEAN')
df['adj_rating'] = df['Book-Rating'] - df['Book-Rating_USER_MEAN']

pivot = df.pivot_table(index='ISBN', columns='User-ID', values='adj_rating', aggfunc='mean')
pivot_sparse = csr_matrix(pivot.fillna(0).values)

# 5. Modelo KNN
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=30, n_jobs=-1)
model_knn.fit(pivot_sparse)

# 6. Guardar artefactos
isbn_index = pd.Series(range(pivot.shape[0]), index=pivot.index)
index_isbn = pd.Series(pivot.index, index=range(pivot.shape[0]))
book_meta = books.set_index('ISBN').loc[pivot.index][['Book-Title', 'Book-Author']]

joblib.dump(model_knn, 'modelo_recomendador_knn.pkl')
joblib.dump({'isbn_index': isbn_index, 'index_isbn': index_isbn}, 'mapeos.pkl')
book_meta.to_pickle('book_meta.pkl')
pd.to_pickle(pivot, 'pivot_centered.pkl')

print("Modelo entrenado y archivos guardados correctamente.")
