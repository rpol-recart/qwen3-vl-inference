# Руководство по сравнению изображений (Image Comparison)

Этот документ описывает использование нового API endpoint `/api/v1/image/comparison` для сравнения 2-4 изображений.

## Обзор

Endpoint позволяет:
- Сравнивать от 2 до 4 изображений одновременно
- Находить различия между изображениями
- Отслеживать изменения в последовательности изображений
- Определять общие элементы и сходства

## Endpoint

```
POST /api/v1/image/comparison
```

## Параметры запроса

### Обязательные параметры

Один из следующих параметров должен быть указан:

- `image_urls` (list[str]): Список URL изображений (2-4 изображения)
- `image_base64_list` (list[str]): Список base64-кодированных изображений (2-4 изображения)

### Опциональные параметры

- `comparison_type` (str): Тип сравнения
  - `"differences"` (по умолчанию): Поиск различий между изображениями
  - `"changes"`: Анализ изменений в последовательности изображений
  - `"similarities"`: Поиск общих элементов и сходств

- `output_format` (str): Формат вывода
  - `"json"` (по умолчанию): Структурированный JSON ответ
  - `"text"`: Текстовое описание

- `prompt` (str): Пользовательский промпт для более специфичного сравнения

- `max_tokens` (int): Максимальное количество токенов в ответе (по умолчанию: 2048)

- `temperature` (float): Температура генерации (0.0-2.0, по умолчанию: 0.0)

- `top_p` (float): Top-p sampling (0.0-1.0, по умолчанию: 1.0)

- `seed` (int): Seed для воспроизводимости результатов

- `min_pixels` (int): Минимальное количество пикселей для обработки (по умолчанию: 65536)

- `max_pixels` (int): Максимальное количество пикселей для обработки (по умолчанию: 4194304)

## Примеры использования

### 1. Базовое сравнение двух изображений

```python
import requests

url = "http://localhost:8000/api/v1/image/comparison"
data = {
    "image_urls": [
        "https://example.com/before.jpg",
        "https://example.com/after.jpg"
    ],
    "comparison_type": "differences",
    "output_format": "json"
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### 2. Анализ изменений в последовательности из 3 изображений

```python
data = {
    "image_urls": [
        "https://example.com/frame1.jpg",
        "https://example.com/frame2.jpg",
        "https://example.com/frame3.jpg"
    ],
    "comparison_type": "changes",
    "output_format": "json"
}

response = requests.post(url, json=data)
result = response.json()
```

### 3. Поиск сходств между 4 изображениями

```python
data = {
    "image_urls": [
        "https://example.com/product1.jpg",
        "https://example.com/product2.jpg",
        "https://example.com/product3.jpg",
        "https://example.com/product4.jpg"
    ],
    "comparison_type": "similarities",
    "output_format": "json"
}

response = requests.post(url, json=data)
result = response.json()
```

### 4. Использование base64 изображений

```python
import base64

# Чтение и кодирование изображений
image_paths = ["image1.jpg", "image2.jpg"]
image_base64_list = []

for path in image_paths:
    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
        image_base64_list.append(image_data)

# Запрос
data = {
    "image_base64_list": image_base64_list,
    "comparison_type": "differences",
    "output_format": "json"
}

response = requests.post(url, json=data)
result = response.json()
```

### 5. Пользовательский промпт для специфичного сравнения

```python
data = {
    "image_urls": [
        "https://example.com/room_before.jpg",
        "https://example.com/room_after.jpg"
    ],
    "comparison_type": "differences",
    "output_format": "json",
    "prompt": "Compare these two images of the same room and identify all furniture and decoration changes. Pay special attention to color changes, new or removed items, and repositioned objects."
}

response = requests.post(url, json=data)
result = response.json()
```

### 6. С дополнительными параметрами

```python
data = {
    "image_urls": [
        "https://example.com/scene1.jpg",
        "https://example.com/scene2.jpg"
    ],
    "comparison_type": "differences",
    "output_format": "json",
    "max_tokens": 3072,
    "temperature": 0.1,
    "min_pixels": 32768,
    "max_pixels": 1048576
}

response = requests.post(url, json=data)
result = response.json()
```

## Формат ответа

### Успешный ответ

```json
{
  "success": true,
  "result": {
    "summary": "Краткое описание сравнения",
    "differences": [
      {
        "description": "Описание различия",
        "location": "Расположение в изображении",
        "images_affected": [1, 2]
      }
    ],
    "common_elements": [
      "Элемент 1",
      "Элемент 2"
    ]
  },
  "error": null,
  "metadata": {
    "task": "image_comparison",
    "num_images": 2,
    "comparison_type": "differences",
    "output_format": "json"
  }
}
```

### Ответ с ошибкой

```json
{
  "success": false,
  "result": null,
  "error": "Number of images must be between 2 and 4",
  "metadata": null
}
```

## Использование через Python клиент

```python
from examples.example_client import Qwen3VLClient

client = Qwen3VLClient("http://localhost:8000")

# Сравнение изображений
result = client.image_comparison(
    image_urls=[
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
    ],
    comparison_type="differences",
    output_format="json"
)

print(result)
```

## Примеры использования через curl

```bash
# Сравнение двух изображений
curl -X POST "http://localhost:8000/api/v1/image/comparison" \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": [
      "https://example.com/image1.jpg",
      "https://example.com/image2.jpg"
    ],
    "comparison_type": "differences",
    "output_format": "json"
  }'
```

## Типичные кейсы использования

### 1. Quality Control (Контроль качества)
Сравнение изображений продукции для выявления дефектов:
```python
data = {
    "image_urls": ["reference.jpg", "sample.jpg"],
    "comparison_type": "differences",
    "prompt": "Identify any defects or deviations from the reference image"
}
```

### 2. Change Detection (Обнаружение изменений)
Отслеживание изменений на участке:
```python
data = {
    "image_urls": ["site_day1.jpg", "site_day7.jpg", "site_day14.jpg"],
    "comparison_type": "changes",
    "prompt": "Track the construction progress and identify new structures"
}
```

### 3. Visual Search (Визуальный поиск)
Поиск похожих элементов между изображениями:
```python
data = {
    "image_urls": ["design1.jpg", "design2.jpg", "design3.jpg"],
    "comparison_type": "similarities",
    "prompt": "Find common design patterns and visual themes"
}
```

### 4. Before/After Analysis (Анализ до/после)
Сравнение состояния объекта до и после обработки:
```python
data = {
    "image_urls": ["before_editing.jpg", "after_editing.jpg"],
    "comparison_type": "differences",
    "prompt": "List all edits and modifications made to the image"
}
```

## Ограничения

- Минимум: 2 изображения
- Максимум: 4 изображения
- Все изображения должны быть предоставлены через один метод (либо URLs, либо base64)
- Рекомендуется использовать изображения схожего размера для лучших результатов

## Оптимизация производительности

1. **Размер изображений**: Используйте параметры `min_pixels` и `max_pixels` для контроля размера:
   ```python
   data = {
       "image_urls": [...],
       "min_pixels": 32768,    # Меньше = быстрее, но менее детально
       "max_pixels": 1048576   # Больше = медленнее, но более детально
   }
   ```

2. **Temperature**: Для детерминированных результатов используйте `temperature=0.0`:
   ```python
   data = {
       "image_urls": [...],
       "temperature": 0.0,
       "seed": 42  # Для воспроизводимости
   }
   ```

3. **Токены**: Ограничьте количество токенов для более быстрых ответов:
   ```python
   data = {
       "image_urls": [...],
       "max_tokens": 1024  # Меньше = быстрее
   }
   ```

## Проверка работоспособности

Убедитесь, что сервер запущен и доступен:

```bash
curl http://localhost:8000/api/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

## Дополнительные ресурсы

- [README.md](README.md) - Общая документация сервера
- [CLAUDE.md](CLAUDE.md) - Руководство для разработчиков
- [examples/comparison_example.py](examples/comparison_example.py) - Расширенные примеры
- [examples/example_client.py](examples/example_client.py) - Python клиент с методом `image_comparison()`

## Техническая информация

### Архитектура

- **Service**: `ImageComparisonService` ([app/services/comparison_service.py](app/services/comparison_service.py))
- **Schema**: `ImageComparisonRequest` ([app/schemas.py](app/schemas.py))
- **Route**: `/api/v1/image/comparison` ([app/api/routes.py](app/api/routes.py))

### Формат сообщений для модели

Внутри сервис создает сообщение следующего формата:

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": "url1", "min_pixels": ..., "max_pixels": ...},
            {"type": "image", "image": "url2", "min_pixels": ..., "max_pixels": ...},
            {"type": "image", "image": "url3", "min_pixels": ..., "max_pixels": ...},
            {"type": "text", "text": "Compare these images..."}
        ]
    }
]
```

Этот формат соответствует официальной документации Qwen3-VL для multi-image инференса.
