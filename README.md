# Qwen3-VL Inference Server

Полнофункциональный inference сервер для модели Qwen3-VL на базе FastAPI и vLLM.

## Возможности

Сервер поддерживает следующие задачи:

1. **2D Grounding** - Обнаружение и локализация объектов на изображениях
2. **Spatial Understanding** - Пространственное понимание и рассуждение
3. **Video Understanding** - Анализ видео и понимание временных событий
4. **Image Description** - Детальное описание изображений
5. **Document Parsing** - Парсинг документов в различные форматы (HTML, Markdown, JSON)
6. **Document OCR** - Распознавание текста в документах
7. **Wild Image OCR** - Распознавание текста на естественных изображениях
8. **Image Comparison** - Сравнение нескольких изображений (2-4) для поиска различий, изменений или сходств

## Архитектура

Проект следует принципам SOLID и DRY, организован по модульной архитектуре:

```
app/
├── __init__.py
├── main.py                 # Главное приложение FastAPI
├── config.py              # Конфигурация через Pydantic Settings
├── schemas.py             # Pydantic модели для запросов/ответов
├── api/
│   ├── __init__.py
│   └── routes.py          # API endpoints
├── core/
│   ├── __init__.py
│   ├── inference_engine.py  # vLLM wrapper
│   └── utils.py           # Утилиты для обработки
└── services/
    ├── __init__.py
    ├── grounding_service.py
    ├── spatial_service.py
    ├── video_service.py
    ├── description_service.py
    ├── document_service.py
    └── ocr_service.py
```

## Установка

### Требования

- Python 3.10+
- CUDA-совместимый GPU (для vLLM)
- Минимум 24GB GPU памяти (зависит от модели)

### Шаги установки

1. Клонируйте репозиторий:
```bash
cd D:\Projects\Qwen_Vl_inference
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

## Запуск

### Docker (Рекомендуется для Production)

Docker обеспечивает изолированное окружение и упрощает deployment.

#### Быстрый старт с Docker

```bash
# 1. Создайте .env файл
cp .env.docker .env
# Отредактируйте .env с вашими настройками

# 2. Запустите с помощью Make
make deploy-dev  # Для разработки
# или
make deploy-prod  # Для production

# 3. Проверьте статус
make health
```

#### Используя Docker Compose напрямую

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Подробнее см. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

### Локальный запуск (без Docker)

#### Базовый запуск

```bash
python main.py
```

Или используя uvicorn напрямую:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### С параметрами

```bash
# Указать путь к модели
export MODEL_PATH=/path/to/qwen3-vl-model
python main.py

# Настроить GPU использование
export GPU_MEMORY_UTILIZATION=0.8
export TENSOR_PARALLEL_SIZE=2
python main.py
```

## API Документация

После запуска сервера, документация доступна по адресу:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Примеры использования

### 1. 2D Grounding

```python
import requests

url = "http://localhost:8000/api/v1/grounding/2d"
data = {
    "image_url": "https://example.com/image.jpg",
    "categories": ["person", "car", "bicycle"],
    "output_format": "json",
    "include_attributes": True
}

response = requests.post(url, json=data)
print(response.json())
```

### 2. Spatial Understanding

```python
url = "http://localhost:8000/api/v1/spatial/understanding"
data = {
    "image_url": "https://example.com/room.jpg",
    "query": "What objects are on the table?",
    "output_format": "json"
}

response = requests.post(url, json=data)
print(response.json())
```

### 3. Video Understanding

```python
url = "http://localhost:8000/api/v1/video/understanding"
data = {
    "video_url": "https://example.com/video.mp4",
    "prompt": "Describe the main events in this video.",
    "max_frames": 128,
    "sample_fps": 1.0
}

response = requests.post(url, json=data)
print(response.json())
```

### 4. Image Description

```python
url = "http://localhost:8000/api/v1/image/description"
data = {
    "image_url": "https://example.com/image.jpg",
    "detail_level": "comprehensive"  # basic, detailed, comprehensive
}

response = requests.post(url, json=data)
print(response.json())
```

### 5. Document Parsing

```python
url = "http://localhost:8000/api/v1/document/parsing"
data = {
    "image_url": "https://example.com/document.jpg",
    "output_format": "qwenvl_html"  # html, markdown, qwenvl_html, qwenvl_markdown
}

response = requests.post(url, json=data)
print(response.json())
```

### 6. Document OCR

```python
url = "http://localhost:8000/api/v1/ocr/document"
data = {
    "image_url": "https://example.com/document.jpg",
    "granularity": "line",  # word, line, paragraph
    "include_bbox": True,
    "output_format": "json"
}

response = requests.post(url, json=data)
print(response.json())
```

### 7. Wild Image OCR

```python
url = "http://localhost:8000/api/v1/ocr/wild"
data = {
    "image_url": "https://example.com/street_sign.jpg",
    "include_bbox": True
}

response = requests.post(url, json=data)
print(response.json())
```

### 8. Image Comparison

```python
url = "http://localhost:8000/api/v1/image/comparison"
data = {
    "image_urls": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
    ],
    "comparison_type": "differences",  # differences, changes, similarities
    "output_format": "json",
    "prompt": ""
}

response = requests.post(url, json=data)
print(response.json())
```

## Health Check

```bash
curl http://localhost:8000/api/health
```

Ответ:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

## Конфигурация

Все настройки можно конфигурировать через переменные окружения или `.env` файл:

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `MODEL_PATH` | Путь к модели или HuggingFace model ID | `Qwen/Qwen3-VL-235B-A22B-Instruct` |
| `HOST` | Хост для запуска сервера | `0.0.0.0` |
| `PORT` | Порт для запуска сервера | `8000` |
| `GPU_MEMORY_UTILIZATION` | Использование GPU памяти | `0.70` |
| `TENSOR_PARALLEL_SIZE` | Количество GPU для параллелизма | auto |
| `DEFAULT_MAX_TOKENS` | Максимум токенов по умолчанию | `2048` |

## Производительность

- vLLM обеспечивает высокую пропускную способность и низкую латентность
- Поддержка Tensor Parallelism для распределения модели на несколько GPU
- Оптимизированное управление памятью через PagedAttention

## Разработка

### Линтинг и форматирование

```bash
# Форматирование кода
black app/
isort app/

# Проверка стиля
flake8 app/
```

### Тестирование

```bash
pytest tests/
```

## Лицензия

Проект использует лицензию, совместимую с Qwen3-VL.

## Поддержка

Для вопросов и проблем создайте issue в репозитории.

## Благодарности

- Alibaba Cloud за модель Qwen3-VL
- vLLM team за inference engine
- FastAPI за веб-фреймворк
