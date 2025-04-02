import pymorphy2
import re
from nltk.corpus import stopwords  # Для удаления стоп-слов
import nltk
import spacy
import numpy as np
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess

# Загрузка необходимых ресурсов
nltk.download('stopwords')
stop_words_ru = set(stopwords.words('russian'))
stop_words_en = set(stopwords.words('english'))

# Инициализация лемматизаторов
morph = pymorphy2.MorphAnalyzer()
nlp_en = spacy.load("en_core_web_sm")  # Для лемматизации английского текста

# Загрузка текста из файла
file_path = "статьи/mnb/articles1/ФОТОННЫЕ КРИСТАЛЛЫ И МЕТАМАТЕРИАЛЫ/Статья 1.txt"  # Укажите путь к вашему файлу
with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# Очистка текста: удаление пунктуации, чисел и приведение к нижнему регистру
cleaned_text = re.sub(r"\d+", "", text)  # Удаление чисел
cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)  # Удаление пунктуации
cleaned_text = cleaned_text.lower()  # Приведение к нижнему регистру

# Токенизация текста
words = simple_preprocess(cleaned_text)  # Простая токенизация (gensim)

# Удаление стоп-слов для обоих языков
filtered_words = [word for word in words if word not in stop_words_ru and word not in stop_words_en]

# Лемматизация текста
lemmatized_words = []
for word in filtered_words:
    # Если слово на русском, лемматизируем с помощью pymorphy2
    if re.match('[а-яА-ЯёЁ]', word):
        lemmatized_words.append(morph.parse(word)[0].normal_form)
    # Если слово на английском, лемматизируем с помощью spacy
    elif re.match('[a-zA-Z]', word):
        doc = nlp_en(word)
        lemmatized_words.append(doc[0].lemma_)

# Разделение текста на предложения для обучения Word2Vec
sentences = [lemmatized_words]  # В данном случае весь текст — одна последовательность слов

# Обучение модели Word2Vec
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# Сохранение обученной модели
model.save("word2vec.model")

# Функция для преобразования текста в вектор
def get_text_vector(words, model):
    vectors = [model.wv[word] for word in words if word in model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(model.vector_size)

# Преобразование текста в вектор
text_vector = get_text_vector(lemmatized_words, model)

# Сохранение вектора в файл
np.save("processed_vectors.npy", text_vector)

# Сохранение предобработанного текста в файл
output_path = "processed_text.txt"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(" ".join(lemmatized_words))

print(f"Предобработанный текст сохранён в {output_path}")
print("Модель Word2Vec обучена и сохранена в 'word2vec.model'")
print("Векторное представление текста сохранено в 'processed_vectors.npy'")

import os
from sklearn.model_selection import train_test_split

text_files = []
labels = []

# Загрузка файлов
for label in os.listdir('dataset/'):
    for filename in os.listdir(f'dataset/{label}'):
        with open(f'dataset/{label}/{filename}', 'r', encoding='utf-8') as file:
            text = file.read()
            text_files.append(text)
            labels.append(label)

# Разделение на тренировочные и тестовые данные
X_train, X_test, y_train, y_test = train_test_split(text_files, labels, test_size=0.2, random_state=42)