import pandas as pd


def dummy_model(input):
    return [558168099, 558171104, 612787165]


def prepare_data(sex, age, status, hobby, reason):
    return pd.Series({
        "man":                      1 if sex == "M" else 0,
        "woman":                    1 if sex == "F" else 0,
        "age":                      age,
        "Туризм":                   1 if "туризм" in hobby else 0,
        "Футбол":                   1 if "футбол" in hobby else 0,
        "Бокс":                     1 if "бокс" in hobby else 0,
        "Спорт":                    1 if "спорт" in hobby else 0,
        "Рукоделие":                1 if "рукоделие" in hobby else 0,
        "Чтение":                   1 if "чтение" in hobby else 0,
        "Фотография":               1 if "фотография" in hobby else 0,
        "Кулинария":                1 if "кулинария" in hobby else 0,
        "Настольные игры":          1 if "настольные игры" in hobby else 0,
        "Кино":                     1 if "кино" in hobby else 0,
        "Музыка":                   1 if "музыка" in hobby else 0,
        "Видеоигры":                1 if "видеоигры" in hobby else 0,
        "IT":                       1 if "IT" in hobby else 0,
        "Цветоводство":             1 if "садоводство" in hobby else 0,
        "Видеомонтаж":              1 if "видеомонтаж" in hobby else 0,
        "Рисование":                0,
        "Новый год":                1 if reason == "new_year" else 0,
        "День рождения":            1 if reason == "birthday" else 0,
        "23 февраля":               1 if (reason == "gender" and sex == "M") else 0,
        "8 марта":                  1 if (reason == "gender" and sex == "F") else 0,
        "Годовщина отношений":      1 if reason == "anniversary" else 0,
        "День Святого Валентина":   1 if reason == "valentine" else 0,
        "Вне праздника":            1 if reason == "other" else 0,
    }).to_frame().T
