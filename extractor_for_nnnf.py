import fitz  # PyMuPDF
import os
import re

def create_safe_filename(filename):
    safe_name = re.sub(r'[<>:"/\\|?*–]', '', filename)
    safe_name = safe_name.replace(" ", "_")
    safe_name = re.sub(r'_+', '_', safe_name)
    return safe_name[:100]

pdf_path = "нннф/Сборник-2016 135.pdf"
output_folder = "articles_extracted"
os.makedirs(output_folder, exist_ok=True)

with fitz.open(pdf_path) as doc:
    text = "\n".join(page.get_text("text") for page in doc)

# Очистка текста от лишних пробелов и переносов строк
#text = re.sub(r'\s+', ' ', text)

# Ищем раздел "СОДЕРЖАНИЕ" (в конце документа)
content_start = text.rfind("СОДЕРЖАНИЕ")
content_end = text.rfind('Научное издание')
content_section = text[content_start+11:content_end]


# Извлекаем названия статей, убирая авторов
article_titles = []
for line in content_section.split("---"):
    line = line.strip('-')
    line = line.strip()
    line = line.lstrip('0123456789')
    last_dot = line.rfind(".")  # Ищем последнюю точку как границу авторов
    if last_dot != -1:
        if len(line[last_dot:]) < 10:
            last_dot = line.rfind('.', 0, last_dot)
        title_only = line[last_dot + 1:].strip()  # Берем только название статьи
        title_only = title_only.replace("\n", '')
        title_only = title_only.strip()
        title_only = title_only.strip('.')
        article_titles.append(title_only)


# Создаем словарь заголовков
article_dict = {title: f"Статья {i + 1}" for i, title in enumerate(article_titles)}

print('\n'.join(article_titles))

# Разбиваем основной текст по заголовкам
articles = []
article_positions = []

for i, title in enumerate(article_titles):
    keywords = title.split()[:3]
    pattern = re.compile(r'\s+'.join(map(re.escape, keywords)), re.IGNORECASE | re.DOTALL)
    match = pattern.search(text)
    if match:
        start = match.start()
    else:
        start = -1
    if i + 1 < len(article_titles):
        end = text.find('Библиографический список', start + 1)
    else:
        end = content_start-1

    if start != -1:  # Добавляем только найденные статьи
        articles.append((article_dict[title], text[start:end].strip()))



# Сохраняем статьи в файлы
for filename, article_text in articles:
    safe_filename = create_safe_filename(filename)
    with open(os.path.join(output_folder, f"{safe_filename}.txt"), "w", encoding="utf-8") as f:
        f.write(article_text)

print(f"Готово! Извлечено {len(articles)} статей.")
