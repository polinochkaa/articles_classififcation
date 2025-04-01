import fitz  # PyMuPDF
import os
import re

def create_safe_filename(filename):
    safe_name = re.sub(r'[<>:"/\\|?*–]', '', filename)
    safe_name = safe_name.replace(" ", "_")
    safe_name = re.sub(r'_+', '_', safe_name)
    return safe_name[:100]

pdf_path = "нннф/Сборник-2024 68.pdf"
output_folder = "nnnf5"
os.makedirs(output_folder, exist_ok=True)

with fitz.open(pdf_path) as doc:
    text = "\n".join(page.get_text("text") for page in doc)


# Разбиваем основной текст по заголовкам
articles = []

start = text.find('м.н.) «Поверхностные волны в гидродинамическом графене»')

while True:
    end = text.find('Библиографический список', start + 1)
    if end != -1:
        articles.append(text[start:end].strip())
        start = end
    else:
        break



# Сохраняем статьи в файлы
for i, article_text in enumerate(articles):
    with open(os.path.join(output_folder, f"Статья {i}.txt"), "w", encoding="utf-8") as f:
        f.write(article_text)

print(f"Готово! Извлечено {len(articles)} статей.")
