# Быстрый старт Qwen3-VL Inference Server

## Предварительные требования

1. **Python 3.10 или выше**
2. **CUDA-совместимый GPU** (рекомендуется минимум 24GB VRAM)
3. **Git** для клонирования репозитория

## Шаг 1: Установка зависимостей

```bash
# Перейдите в директорию проекта
cd D:\Projects\Qwen_Vl_inference

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# На Windows:
venv\Scripts\activate
# На Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

## Шаг 2: Настройка конфигурации

```bash
# Скопируйте файл с примером конфигурации
copy .env.example .env  # Windows
# или
cp .env.example .env    # Linux/Mac

# Отредактируйте .env файл
# Установите MODEL_PATH на путь к вашей модели или HuggingFace model ID
```

Пример `.env`:
```env
MODEL_PATH=Qwen/Qwen3-VL-235B-A22B-Instruct
GPU_MEMORY_UTILIZATION=0.70
PORT=8000
```

## Шаг 3: Запуск сервера

```bash
# Простой запуск
python main.py

# Или с явным указанием параметров
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Вы увидите логи инициализации:
```
INFO: Starting Qwen3-VL Inference Server...
INFO: Model path: Qwen/Qwen3-VL-235B-A22B-Instruct
INFO: Initializing Qwen3-VL Inference Engine...
INFO: Inference engine initialized successfully
INFO: Server ready at http://0.0.0.0:8000
```

## Шаг 4: Проверка работоспособности

Откройте браузер и перейдите по адресу:

- **Главная страница**: http://localhost:8000/
- **API документация (Swagger)**: http://localhost:8000/docs
- **Альтернативная документация (ReDoc)**: http://localhost:8000/redoc

Или используйте curl:

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

## Шаг 5: Первый запрос

### Пример с curl:

```bash
curl -X POST "http://localhost:8000/api/v1/image/description" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "detail_level": "detailed",
    "prompt": ""
  }'
```

### Пример с Python:

```python
import requests

url = "http://localhost:8000/api/v1/image/description"
data = {
    "image_url": "https://example.com/image.jpg",
    "detail_level": "detailed",
    "prompt": ""
}

response = requests.post(url, json=data)
print(response.json())
```

### Использование клиента из примеров:

```bash
python examples/example_client.py
```

## Доступные эндпоинты

| Эндпоинт | Описание |
|----------|----------|
| `POST /api/v1/grounding/2d` | 2D обнаружение объектов |
| `POST /api/v1/spatial/understanding` | Пространственное понимание |
| `POST /api/v1/video/understanding` | Анализ видео |
| `POST /api/v1/image/description` | Описание изображений |
| `POST /api/v1/document/parsing` | Парсинг документов |
| `POST /api/v1/ocr/document` | OCR документов |
| `POST /api/v1/ocr/wild` | OCR естественных изображений |

## Примеры запросов

### 1. Обнаружение объектов (2D Grounding)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/grounding/2d",
    json={
        "image_url": "https://example.com/street.jpg",
        "categories": ["person", "car", "bicycle"],
        "include_attributes": True,
        "prompt": ""
    }
)
print(response.json())
```

### 2. Пространственное понимание

```python
response = requests.post(
    "http://localhost:8000/api/v1/spatial/understanding",
    json={
        "image_url": "https://example.com/room.jpg",
        "query": "Which objects are on the table?",
        "prompt": "Which objects are on the table?"
    }
)
print(response.json())
```

### 3. Анализ видео

```python
response = requests.post(
    "http://localhost:8000/api/v1/video/understanding",
    json={
        "video_url": "https://example.com/video.mp4",
        "prompt": "Describe what happens in this video.",
        "max_frames": 128,
        "sample_fps": 1.0
    }
)
print(response.json())
```

### 4. Описание изображения

```python
response = requests.post(
    "http://localhost:8000/api/v1/image/description",
    json={
        "image_url": "https://example.com/image.jpg",
        "detail_level": "comprehensive",  # basic, detailed, или comprehensive
        "prompt": ""
    }
)
print(response.json())
```

### 5. Парсинг документов

```python
response = requests.post(
    "http://localhost:8000/api/v1/document/parsing",
    json={
        "image_url": "https://example.com/document.jpg",
        "output_format": "qwenvl_html",  # html, markdown, qwenvl_html, qwenvl_markdown
        "prompt": ""
    }
)
print(response.json())
```

### 6. OCR документов

```python
response = requests.post(
    "http://localhost:8000/api/v1/ocr/document",
    json={
        "image_url": "https://example.com/document.jpg",
        "granularity": "line",  # word, line, или paragraph
        "include_bbox": True,
        "prompt": ""
    }
)
print(response.json())
```

### 7. OCR естественных изображений

```python
response = requests.post(
    "http://localhost:8000/api/v1/ocr/wild",
    json={
        "image_url": "https://example.com/street_sign.jpg",
        "include_bbox": True,
        "prompt": ""
    }
)
print(response.json())
```

## Работа с base64 изображениями

Вместо `image_url` вы можете использовать `image_base64`:

```python
import base64

# Прочитать изображение
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/api/v1/image/description",
    json={
        "image_base64": image_data,
        "detail_level": "detailed",
        "prompt": ""
    }
)
```

## Настройка параметров инференса

Все эндпоинты поддерживают дополнительные параметры:

```python
response = requests.post(
    "http://localhost:8000/api/v1/image/description",
    json={
        "image_url": "https://example.com/image.jpg",
        "prompt": "",
        "max_tokens": 1024,      # Максимум токенов в ответе
        "temperature": 0.7,      # Температура сэмплирования (0.0 - 2.0)
        "top_p": 0.9,           # Top-p сэмплирование (0.0 - 1.0)
        "seed": 42,             # Seed для воспроизводимости
        "min_pixels": 65536,    # Минимум пикселей для обработки
        "max_pixels": 2097152   # Максимум пикселей для обработки
    }
)
```

## Решение проблем

### Проблема: Out of Memory (OOM)

**Решение**: Уменьшите `GPU_MEMORY_UTILIZATION` в `.env`:
```env
GPU_MEMORY_UTILIZATION=0.5
```

### Проблема: Модель не загружается

**Решение**: Убедитесь, что путь к модели правильный:
```bash
# Если используете HuggingFace Hub
export MODEL_PATH=Qwen/Qwen3-VL-235B-A22B-Instruct

# Если используете локальную модель
export MODEL_PATH=/path/to/your/model
```

### Проблема: Медленная работа

**Решение**:
1. Используйте несколько GPU с tensor parallelism:
```env
TENSOR_PARALLEL_SIZE=2
```

2. Оптимизируйте размеры изображений:
```python
{
    "min_pixels": 32768,   # Меньше пикселей = быстрее
    "max_pixels": 1048576
}
```

## Остановка сервера

Нажмите `Ctrl+C` в терминале, где запущен сервер.

## Дополнительная информация

- Полная документация: [README.md](README.md)
- Примеры использования: [examples/](examples/)
- Swagger UI: http://localhost:8000/docs
