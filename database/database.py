# Создаем шаблон заполнения словаря с пользователями
user_dict_template = {
    'current_page': 1,
    'total_pages': 1,
    'residue': 1,
    'step': 5,
    'query': 'abs:"primordial black holes" doctype:("article" OR "eprint" OR "inproceedings") ',
    'favorite': set(),
}

# Инициализируем "базу данных"
users_db = {}
