Семантический анализ
Семантический анализ – это процесс, направленный на определение значения слов, фраз, предложений и текстов в целом. В NLP семантический анализ помогает моделям не просто читать слова, а понимать их смысл и взаимосвязи между ними. Этот анализ включает в себя несколько подходов:

Лексическая семантика – изучение смысла отдельных слов и их значений.
Синтаксическая семантика – анализ структуры предложений, чтобы понять, как слова в них связаны и как они влияют на смысл.
Контекстная семантика – интерпретация значения слов и фраз с учетом контекста (например, полисемия, когда одно и то же слово может иметь разные значения).
Семантическая близость
Семантическая близость – это мера схожести между двумя текстами (словами, фразами или целыми предложениями) на основе их смысла, а не только лексической похожести. Например, слова "автомобиль" и "машина" имеют высокую семантическую близость, потому что обозначают примерно одно и то же, в отличие от слов, таких как "автомобиль" и "яблоко".

Для вычисления семантической близости используются следующие методы:

Векторные представления (эмбеддинги) – слова и предложения представляются в виде векторов, где близость определяется по косинусной схожести или евклидовому расстоянию между ними. Популярные модели, такие как Word2Vec, GloVe, BERT, создают такие векторы на основе большого объема текстовых данных.
Модели глубокого обучения – более сложные архитектуры, такие как трансформеры (BERT, GPT), которые могут учитывать контекст и более тонкие семантические зависимости между текстами.
Семантические сети и графы – методы, основанные на иерархических и сетевых связях между словами и концепциями.

# Пример

from datasets import Dataset

# Три пары предложений
sentence1_list = [
    "I love programming", 
    "Python is great", 
    "The weather is nice today"
]
sentence2_list = [
    "Coding is my passion", 
    "I enjoy working with Python", 
    "It’s a sunny day"
]

# Метки для каждой пары предложений, указывающие степень их семантической близости
# 1.0 - полное совпадение, 0.0 - полное отсутствие схожести
labels_list = [0.9, 0.8, 0.4]

# Создание датасета
train_dataset = Dataset.from_dict({
    "sentence1": sentence1_list,
    "sentence2": sentence2_list,
    "label": labels_list,
})

# Печать первых строк датасета
print(train_dataset[0])  # {'sentence1': 'I love programming', 'sentence2': 'Coding is my passion', 'label': 0.9}
print(train_dataset[1])  # {'sentence1': 'Python is great', 'sentence2': 'I enjoy working with Python', 'label': 0.8}
print(train_dataset[2])  # {'sentence1': 'The weather is nice today', 'sentence2': 'It’s a sunny day', 'label': 0.4}


 Sentence Transformers (GitHub https://github.com/UKPLab/sentence-transformers)
Описание: Инструмент на базе BERT и других трансформеров для создания векторных представлений текста. Поддерживает генерацию векторов предложений и документов для вычисления семантической близости.
Применение: Используется для создания векторных представлений загруженных документов и типовых форм. Позволяет вычислять косинусную близость между векторами для нахождения различий по смыслу.

Spacy (GitHub https://github.com/explosion/spaCy)
Описание: Библиотека NLP для обработки текста, которая поддерживает трансформеры и векторные представления.
Применение: Использование встроенных эмбеддингов и моделей для создания векторов для сравнения документа с типовой формой на основе семантической близости.