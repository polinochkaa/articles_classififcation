import pymorphy2
import re
from nltk.corpus import stopwords  # Для удаления стоп-слов
import nltk
import spacy

# Загрузка необходимых ресурсов
nltk.download('stopwords')
stop_words_ru = set(stopwords.words('russian'))
stop_words_en = set(stopwords.words('english'))

# Инициализация лемматизаторов
morph = pymorphy2.MorphAnalyzer()
nlp_en = spacy.load("en_core_web_sm")  # Для лемматизации английского текста

# Загрузка текста из файла
file_path = "Статья 1.txt"  # Укажите путь к вашему файлу

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# Очистка текста: удаление пунктуации, чисел и приведение к нижнему регистру
cleaned_text = re.sub(r"\d+", "", text)  # Удаление чисел
cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)  # Удаление пунктуации
cleaned_text = cleaned_text.lower()  # Приведение к нижнему регистру

# Разделение текста на слова
words = cleaned_text.split()

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

# Результат после лемматизации
lemmatized_text = " ".join(lemmatized_words)

# Сохранение результата в файл
output_path = "processed_text.txt"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(lemmatized_text)

print(f"Предобработанный текст сохранён в {output_path}")
