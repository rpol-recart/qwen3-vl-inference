# Video Understanding API - Руководство

Полное руководство по использованию API для анализа видео в Qwen3-VL Inference Server.

## Содержание

- [Обзор](#обзор)
- [Endpoints](#endpoints)
- [Форматы входных данных](#форматы-входных-данных)
- [Примеры использования](#примеры-использования)
- [Оптимизация параметров](#оптимизация-параметров)

## Обзор

API для video understanding поддерживает **4 формата входных данных**:

1. **video_url** - URL к видеофайлу
2. **video_base64** - Base64 encoded видео
3. **frame_urls** - Список URL кадров
4. **frame_base64_list** - Список base64 encoded кадров

Плюс дополнительный endpoint для **прямой загрузки файлов**.

## Endpoints

### 1. POST /api/v1/video/understanding

Основной endpoint для анализа видео через JSON запрос.

**Поддерживаемые форматы:**
- video_url
- video_base64
- frame_urls
- frame_base64_list

### 2. POST /api/v1/video/understanding/upload

Endpoint для загрузки видеофайла напрямую через multipart/form-data.

**Преимущества:**
- Удобно для загрузки локальных файлов
- Не нужно конвертировать в base64 вручную
- Поддержка больших файлов через streaming

## Форматы входных данных

### 1. Video URL

Самый простой способ - указать URL к видеофайлу.

```python
import requests

url = "http://localhost:8000/api/v1/video/understanding"
data = {
    "video_url": "https://example.com/video.mp4",
    "prompt": "Describe what happens in this video.",
    "max_frames": 128,
    "sample_fps": 1.0
}

response = requests.post(url, json=data)
print(response.json())
```

**Плюсы:**
- Простота использования
- Не нужно передавать большие данные
- Быстрый запрос

**Минусы:**
- Видео должно быть доступно по URL
- Зависит от скорости скачивания

### 2. Video Base64

Передача видео в виде base64 строки.

```python
import requests
import base64

# Читаем видеофайл
with open("video.mp4", "rb") as f:
    video_data = base64.b64encode(f.read()).decode()

url = "http://localhost:8000/api/v1/video/understanding"
data = {
    "video_base64": video_data,
    "prompt": "What activities are shown in this video?",
    "max_frames": 64,
    "sample_fps": 2.0
}

response = requests.post(url, json=data)
print(response.json())
```

**Плюсы:**
- Не требует хостинга видео
- Работает с локальными файлами

**Минусы:**
- Большой размер payload
- Медленнее для больших видео

### 3. Frame URLs

Список URL кадров, извлеченных из видео.

```python
import requests

# Предварительно извлеченные кадры
frame_urls = [
    "https://example.com/frames/frame_0001.jpg",
    "https://example.com/frames/frame_0002.jpg",
    "https://example.com/frames/frame_0003.jpg",
    # ... до 2048 кадров
]

url = "http://localhost:8000/api/v1/video/understanding"
data = {
    "frame_urls": frame_urls,
    "prompt": "Summarize the main events.",
    "sample_fps": 0.5  # FPS оригинального видео при извлечении
}

response = requests.post(url, json=data)
print(response.json())
```

**Плюсы:**
- Контроль над выбором кадров
- Можно предобработать кадры
- Гибкость в сэмплировании

**Минусы:**
- Требует предварительного извлечения кадров
- Нужно хостить кадры

### 4. Frame Base64 List

Список кадров в base64 формате.

```python
import requests
import base64
from PIL import Image
import io

# Извлекаем кадры из видео (пример с использованием PIL)
def extract_frames_to_base64(video_path, num_frames=10):
    """Псевдокод - в реальности используйте OpenCV или ffmpeg"""
    frames = []
    # ... извлечение кадров
    for frame_img in extracted_frames:
        buffered = io.BytesIO()
        frame_img.save(buffered, format="JPEG")
        frame_base64 = base64.b64encode(buffered.getvalue()).decode()
        frames.append(frame_base64)
    return frames

frames_base64 = extract_frames_to_base64("video.mp4", num_frames=50)

url = "http://localhost:8000/api/v1/video/understanding"
data = {
    "frame_base64_list": frames_base64,
    "prompt": "Describe the sequence of events.",
    "sample_fps": 2.0
}

response = requests.post(url, json=data)
print(response.json())
```

**Плюсы:**
- Полный контроль над кадрами
- Не требует хостинга

**Минусы:**
- Очень большой payload
- Требует предварительной обработки

### 5. File Upload (Рекомендуется!)

Прямая загрузка файла через multipart/form-data.

```python
import requests

url = "http://localhost:8000/api/v1/video/understanding/upload"

with open("video.mp4", "rb") as video_file:
    files = {"file": ("video.mp4", video_file, "video/mp4")}
    data = {
        "prompt": "What is happening in this video?",
        "max_frames": 128,
        "sample_fps": 1.0,
        "max_tokens": 2048
    }

    response = requests.post(url, files=files, data=data)
    print(response.json())
```

**Или с помощью curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/video/understanding/upload" \
  -F "file=@video.mp4" \
  -F "prompt=Describe what happens in this video" \
  -F "max_frames=128" \
  -F "sample_fps=1.0"
```

**Плюсы:**
- Самый простой для локальных файлов
- Не нужна конвертация в base64
- Эффективное использование памяти

**Минусы:**
- Требует multipart/form-data (не JSON)

## Примеры использования

### Пример 1: Базовый анализ видео

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/video/understanding",
    json={
        "video_url": "https://example.com/cooking.mp4",
        "prompt": "Describe the cooking process step by step.",
        "max_frames": 64,
        "sample_fps": 1.0
    }
)

result = response.json()
if result["success"]:
    print(result["result"])
else:
    print(f"Error: {result['error']}")
```

### Пример 2: Временная локализация событий

```python
response = requests.post(
    "http://localhost:8000/api/v1/video/understanding",
    json={
        "video_url": "https://example.com/soccer.mp4",
        "prompt": """Localize activity events in the video.
        Output start and end timestamps for each event in JSON format:
        [{"time": "mm:ss-mm:ss", "description": "event description"}]""",
        "max_frames": 128,
        "sample_fps": 2.0
    }
)

print(response.json()["result"])
```

### Пример 3: Детальное описание с высоким разрешением

```python
response = requests.post(
    "http://localhost:8000/api/v1/video/understanding",
    json={
        "video_url": "https://example.com/nature.mp4",
        "prompt": "Provide a detailed description of the scenery and wildlife.",
        "max_frames": 256,  # Больше кадров
        "sample_fps": 4.0,  # Выше FPS
        "total_pixels": 256 * 1024 * 32 * 32,  # Больше пикселей
        "max_tokens": 4096  # Длиннее ответ
    }
)
```

### Пример 4: Загрузка локального видео

```python
def analyze_local_video(video_path, question):
    """Анализ локального видеофайла"""
    with open(video_path, "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/v1/video/understanding/upload",
            files={"file": f},
            data={"prompt": question}
        )
    return response.json()

# Использование
result = analyze_local_video(
    "my_video.mp4",
    "What are the main activities shown?"
)
print(result["result"])
```

### Пример 5: Пакетная обработка видео

```python
import os
from pathlib import Path

def process_video_directory(directory, question):
    """Обработка всех видео в директории"""
    results = {}

    for video_file in Path(directory).glob("*.mp4"):
        print(f"Processing {video_file.name}...")

        with open(video_file, "rb") as f:
            response = requests.post(
                "http://localhost:8000/api/v1/video/understanding/upload",
                files={"file": (video_file.name, f, "video/mp4")},
                data={
                    "prompt": question,
                    "max_frames": 64,
                    "sample_fps": 1.0
                }
            )

        result = response.json()
        results[video_file.name] = result["result"] if result["success"] else result["error"]

    return results

# Использование
results = process_video_directory("./videos", "Summarize this video in one sentence.")
for filename, description in results.items():
    print(f"\n{filename}:")
    print(description)
```

### Пример 6: Анализ с предобработанными кадрами

```python
import cv2
import base64
import io
from PIL import Image

def extract_key_frames(video_path, num_frames=30):
    """Извлечение ключевых кадров"""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Равномерное сэмплирование
    indices = [int(i * total_frames / num_frames) for i in range(num_frames)]

    frames_base64 = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Конвертация в PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)

            # Конвертация в base64
            buffered = io.BytesIO()
            pil_img.save(buffered, format="JPEG", quality=90)
            frame_base64 = base64.b64encode(buffered.getvalue()).decode()
            frames_base64.append(frame_base64)

    cap.release()
    return frames_base64

# Извлечение кадров
frames = extract_key_frames("video.mp4", num_frames=50)

# Анализ
response = requests.post(
    "http://localhost:8000/api/v1/video/understanding",
    json={
        "frame_base64_list": frames,
        "prompt": "Analyze the visual content across these frames.",
        "sample_fps": 2.0
    }
)

print(response.json()["result"])
```

## Оптимизация параметров

### Параметры сэмплирования

| Параметр | Описание | Рекомендации |
|----------|----------|--------------|
| `max_frames` | Максимум кадров для обработки | 64-128 для базового анализа<br>256+ для детального |
| `sample_fps` | FPS сэмплирования | 1-2 для большинства задач<br>4+ для быстрых событий |
| `total_pixels` | Бюджет пикселей | 20480×32×32 по умолчанию<br>Увеличьте для HD качества |
| `min_pixels` | Минимум пикселей на кадр | 64×32×32 обычно достаточно |

### Оптимизация по задачам

#### Быстрый анализ (низкая латентность)
```python
{
    "max_frames": 32,
    "sample_fps": 0.5,
    "total_pixels": 10240 * 32 * 32,
    "max_tokens": 512
}
```

#### Детальный анализ (высокое качество)
```python
{
    "max_frames": 256,
    "sample_fps": 4.0,
    "total_pixels": 256 * 1024 * 32 * 32,
    "max_tokens": 4096
}
```

#### Событийный анализ (временная локализация)
```python
{
    "max_frames": 128,
    "sample_fps": 2.0,
    "total_pixels": 40960 * 32 * 32,
    "max_tokens": 2048
}
```

## Обработка ошибок

```python
def safe_video_analysis(video_input, prompt, **kwargs):
    """Безопасный анализ с обработкой ошибок"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/video/understanding",
            json={
                **video_input,
                "prompt": prompt,
                **kwargs
            },
            timeout=300  # 5 минут timeout
        )
        response.raise_for_status()

        result = response.json()
        if not result["success"]:
            raise Exception(f"Analysis failed: {result.get('error', 'Unknown error')}")

        return result["result"]

    except requests.Timeout:
        return "Error: Request timed out. Try reducing max_frames or total_pixels."
    except requests.RequestException as e:
        return f"Error: Network issue - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# Использование
result = safe_video_analysis(
    {"video_url": "https://example.com/video.mp4"},
    "Describe this video",
    max_frames=64
)
print(result)
```

## Ограничения

- **Максимальный размер файла**: Зависит от настроек сервера (по умолчанию ~1GB для upload)
- **Максимум кадров**: 2048 (можно настроить)
- **Максимум токенов**: Настраиваемо (по умолчанию 2048)
- **Timeout**: Установите достаточный timeout для больших видео

## Советы по производительности

1. **Используйте video_url когда возможно** - быстрее чем base64
2. **Оптимизируйте max_frames** - больше не всегда лучше
3. **Правильный sample_fps** - соответствует динамике видео
4. **Batch processing** - обрабатывайте видео параллельно
5. **Кэширование** - кэшируйте результаты для повторных запросов

## Дополнительная информация

- Основная документация: [README.md](README.md)
- Примеры клиента: [examples/example_client.py](examples/example_client.py)
- API документация: http://localhost:8000/docs

## Поддержка

Для вопросов и проблем создайте issue в репозитории проекта.
