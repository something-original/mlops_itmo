# Сравнение методов хранения файлов


| Метод хранения | Суть подхода | Преимущества | Недостатки | Рекомендуемый объем файла | Применение в проекте |
|----------------|-------------|--------------|------------|---------------------------|----------------------|
| **СУБД (SQL Database)** | Хранение файлов в базе данных как BLOB (Binary Large Object) | - Централизованное управление данными<br>- Возможность транзакционного контроля<br>- Удобный поиск и фильтрация данных | - Увеличение размера базы данных<br>- Потенциальное снижение производительности<br>- Сложность резервного копирования больших данных | Рекомендуется для файлов до **1–5 MB**. Более крупные файлы могут значительно увеличить размер базы и снизить её производительность. | Подходит для хранения метаданных документов и небольших файлов. Например, документов с основными данными, такими как имена и даты, но не для больших сканов. |
| **Файловая система (Disk File System)** | Хранение файлов на диске с путями, сохраненными в базе данных | - Высокая производительность для больших файлов<br>- Простота резервного копирования<br>- Легкость масштабирования | - Необходимость управления ссылками на файлы<br>- Сложность обеспечения целостности данных | Рекомендуется для файлов свыше **5 MB** и особенно для больших сканов и изображений (например, 10 MB и более). | Рекомендуется для хранения больших файлов, таких как сканированные документы и фотографии, для быстрой загрузки и доступа. Пути к файлам могут быть сохранены в базе данных для облегчения поиска и управления. |

## Вопросы безопасности
**Базы данных SQL** имеют встроенные меры безопасности, такие как аутентификация пользователей и контроль доступа, что делает их более безопасным вариантом для хранения конфиденциальных изображений. 
Однако **файловые системы на дисках** также можно защитить с помощью контроля доступа и шифрования, что делает их подходящим вариантом для компаний, работающих с конфиденциальными изображениями.

На мой взгляд, хранение в базе данных в виде больших двоичных объектов — более эффективное и масштабируемое решение в сценарии с несколькими серверами, особенно с учётом отказоустойчивости и доступности.

# Файловые БД
# Сравнение файловых баз данных для хранения файлов в Spring Boot проекте

| Метод хранения           | Суть подхода                                                                                       | Преимущества                                                                                   | Недостатки                                                                                   | Рекомендуемый объем файла | Применение в проекте                                                                                       |
|--------------------------|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|---------------------------|------------------------------------------------------------------------------------------------------------|
| **MongoDB (GridFS)**     | Хранение файлов в MongoDB с использованием GridFS, где файлы разбиваются на части и хранятся в отдельных документах | - Высокая масштабируемость<br>- Поддержка бинарных данных<br>- Удобная интеграция с Spring Data MongoDB | - Увеличение объема базы данных<br>- Требуется MongoDB для развертывания                     | Файлы от 5 MB и более      | Подходит для хранения крупных файлов (сканы, изображения). Можно хранить метаданные, пути к файлам и результаты OCR. |
| **MinIO**                | Объектное хранилище с API, совместимым с Amazon S3, где файлы хранятся в виде объектов             | - Легко развертывается локально<br>- Поддерживает шифрование и управление версиями<br>- Совместимость с Amazon S3 API | - Требует дополнительных настроек для локального развертывания                              | Файлы среднего и большого размера (например, 5 MB и более) | Подходит для хранения больших файлов и использования объектного хранилища для документов и изображений.     |
| **PostgreSQL (BYTEA)**   | Хранение файлов в PostgreSQL в виде бинарных данных (тип данных BYTEA)                             | - Удобная поддержка транзакций<br>- Полная интеграция с SQL-запросами<br>- Удобная работа с метаданными | - Ограничения производительности для больших файлов<br>- Рекомендуется для файлов до 5 MB    | Файлы до 1-5 MB            | Подходит для хранения небольших файлов и метаданных, таких как информация о документах, которые требуют SQL-запросов. |
| **Spring Data JPA (BLOB)** | Хранение файлов в реляционных базах данных с использованием BLOB для бинарных данных             | - Централизованное управление данными<br>- Транзакционная поддержка и интеграция с JPA/Hibernate | - Замедление производительности с увеличением размера файлов<br>- Рекомендуется для файлов до 5 MB | Файлы до 1-5 MB            | Подходит для хранения метаданных и небольших файлов, таких как изображения и PDF-документы. Не рекомендуется для больших файлов. |


## Рекомендации для проекта

Для проекта, направленного на автоматическое выявление расхождений в юридических документах, рекомендуется следующая архитектура хранения:

- **Файловая система**: использовать для хранения больших файлов, таких как сканы и фотографии документов. Это обеспечит быструю загрузку и обработку изображений.

- **База данных**: хранить метаданные документов, пути к файлам и результаты OCR-распознавания. Это позволит эффективно управлять данными, выполнять поиск и анализ.

Такой подход сочетает преимущества обоих методов, обеспечивая производительность и удобство управления данными.


## Пример данных хранимых в БД MongoDB
```json
{
    "documentId": "abc123",
    "metadata": {
        "title": "Contract Agreement",
        "createdAt": "2024-11-01",
        "author": "John Doe",
        "type": "Legal Document"
    },
    "ocrResults": [
        {
            "page": 1,
            "text": "This is the extracted text from page 1 of the document.",
            "fields": {
                "contractNumber": "123456",
                "date": "2024-10-20"
            }
        },
        {
            "page": 2,
            "text": "Extracted text from page 2..."
        }
    ]
}

```