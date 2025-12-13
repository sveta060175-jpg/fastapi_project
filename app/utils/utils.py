import os

def read_readme():
    """Чтение README.md файла"""
    try:
        readme_path = "../README.md"
        
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                return f.read()
        current_dir = os.path.dirname(__file__)
        readme_path = os.path.join(current_dir, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Описание проекта не найдено. Проверьте наличие файла README.md"
        
    except Exception as e:
        return f"Ошибка при чтении README.md: {str(e)}"
