import fitz  # PyMuPDF
import os
import re

# Функция для создания безопасного имени файла
def create_safe_filename(filename):
    # Удаляем недопустимые символы
    safe_name = re.sub(r'[<>:"/\\|?*–]', '', filename)
    # Заменяем пробелы на подчеркивания
    safe_name = safe_name.replace(" ", "_")
    # Убираем лишние подчеркивания
    safe_name = re.sub(r'_+', '_', safe_name)
    # Ограничиваем длину имени файла
    return safe_name[:100]  # Максимальная длина имени файла

# Путь к файлу PDF
pdf_path = "mnb_2024 76.pdf"
output_folder = "articles11"
os.makedirs(output_folder, exist_ok=True)

# Открываем PDF и извлекаем текст
with fitz.open(pdf_path) as doc:
    text = "\n".join(page.get_text("text") for page in doc)

# Ищем раздел "СОДЕРЖАНИЕ" и извлекаем его текст
content_start = text.find("СОДЕРЖАНИЕ")
content_end = text.find("Посвящается 110")  # конец содержания
content_section = text[content_start:content_end]

# Ищем заголовки статей (пропуская названия секций)
article_titles = []
for line in re.split(r'\d+', content_section):
    line = line.strip().strip('.')
    new_line = ''
    if line and not line.isupper() and re.search(r'\w', line):  # Пропускаем заголовки секций
        for word in line.split():
            if not any(letter.islower() or letter == '.' for letter in word):
                new_line += word + ' '
        article_titles.append(new_line.strip().strip('.').strip(',').strip())

# Создаем список заголовков с нумерацией
article_dict = {title: f"Статья {i + 1}" for i, title in enumerate(article_titles)}

# Заменяем невидимые символы
text = re.sub(r'[\xa0\t]', ' ', text)

# Разделяем основной текст по заголовкам
articles = []
end = content_end+1
for i, title in enumerate(article_titles):
    # Используем первые три слова для поиска
    keywords = title.split()[:3]
    pattern = re.compile(r'\s+'.join(map(re.escape, keywords)), re.IGNORECASE | re.DOTALL)
    match = pattern.search(text, pos=max(end, content_end+1))
    if match:
        start = match.start()
    else:
        start = -1

    # Ищем конец статьи (начало следующего заголовка)
    if i + 1 < len(article_titles):
        next_keywords = article_titles[i + 1].split()[:3]
        next_pattern = re.compile(r'\s*'.join(map(re.escape, next_keywords)), re.IGNORECASE | re.DOTALL)
        end_match = next_pattern.search(text, pos=start + 1)
        end = end_match.start() if end_match else len(text)
    else:
        end = len(text)  # Для последней статьи

    if start != -1:  # Добавляем только найденные статьи
        articles.append((article_dict[title], text[start:end].strip()))

# Сохраняем статьи
for filename, article_text in articles:
    safe_filename = create_safe_filename(filename)  # Создаем безопасное имя файла
    with open(os.path.join(output_folder, f"{filename}.txt"), "w", encoding="utf-8") as f:
        f.write(article_text)

print(f"Готово! Извлечено {len(articles)} статей.")