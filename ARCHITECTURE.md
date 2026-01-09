# Архитектура Qwen3-VL Inference Server

## Обзор

Проект реализован с соблюдением принципов **SOLID**, **DRY** и других best practices для создания масштабируемого, поддерживаемого и тестируемого кода.

## Структура проекта

```
D:\Projects\Qwen_Vl_inference\
├── app/                          # Основной пакет приложения
│   ├── __init__.py
│   ├── main.py                   # FastAPI приложение и lifespan management
│   ├── config.py                 # Конфигурация через Pydantic Settings
│   ├── schemas.py                # Pydantic модели (Request/Response DTOs)
│   │
│   ├── api/                      # API слой (Controllers)
│   │   ├── __init__.py
│   │   └── routes.py             # FastAPI роутеры и endpoints
│   │
│   ├── core/                     # Ядро системы
│   │   ├── __init__.py
│   │   ├── inference_engine.py   # vLLM wrapper (Engine)
│   │   └── utils.py              # Утилиты для обработки данных
│   │
│   └── services/                 # Бизнес-логика (Services)
│       ├── __init__.py
│       ├── grounding_service.py  # 2D Grounding сервис
│       ├── spatial_service.py    # Spatial Understanding сервис
│       ├── video_service.py      # Video Understanding сервис
│       ├── description_service.py # Image Description сервис
│       ├── document_service.py   # Document Parsing сервис
│       └── ocr_service.py        # OCR сервис
│
├── examples/                     # Примеры использования
│   └── example_client.py         # Python клиент
│
├── main.py                       # Точка входа
├── requirements.txt              # Зависимости Python
├── .env.example                  # Пример конфигурации
├── .gitignore                    # Git ignore rules
├── README.md                     # Основная документация
├── QUICKSTART.md                 # Быстрый старт
└── ARCHITECTURE.md               # Этот файл
```

## Архитектурные слои

### 1. API Layer (Controllers)

**Файлы**: `app/api/routes.py`

**Ответственность**:
- Определение HTTP endpoints
- Валидация входящих запросов (через Pydantic)
- Маршрутизация запросов к соответствующим сервисам
- Формирование HTTP ответов

**Принципы**:
- **Single Responsibility**: Только HTTP обработка, никакой бизнес-логики
- **Dependency Injection**: Получение engine через FastAPI Depends

```python
@router.post("/v1/grounding/2d", response_model=InferenceResponse)
async def grounding_2d(
    request: Grounding2DRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    service = GroundingService(engine)
    return await service.perform_grounding(request)
```

### 2. Service Layer (Business Logic)

**Файлы**: `app/services/*.py`

**Ответственность**:
- Реализация бизнес-логики для каждой задачи
- Построение промптов
- Вызов inference engine
- Обработка и форматирование результатов

**Принципы**:
- **Single Responsibility**: Каждый сервис отвечает за одну задачу
- **Dependency Inversion**: Зависимость от абстракции (engine interface)
- **Open/Closed**: Легко добавить новый сервис без изменения существующих

**Пример**:
```python
class GroundingService:
    def __init__(self, engine: Qwen3VLInferenceEngine):
        self.engine = engine

    async def perform_grounding(self, request: Grounding2DRequest):
        # Бизнес-логика для grounding
        ...
```

### 3. Core Layer (Infrastructure)

#### Inference Engine (`app/core/inference_engine.py`)

**Ответственность**:
- Инициализация vLLM модели
- Подготовка входных данных для модели
- Выполнение инференса
- Streaming generation (опционально)

**Принципы**:
- **Encapsulation**: Скрывает детали работы с vLLM
- **Interface Segregation**: Предоставляет чистый API для сервисов

```python
class Qwen3VLInferenceEngine:
    def __init__(self, model_path, ...):
        # Инициализация vLLM

    def generate(self, messages, ...):
        # Инференс

    def prepare_image_inputs(self, messages):
        # Подготовка данных
```

#### Utils (`app/core/utils.py`)

**Ответственность**:
- Обработка изображений (base64, URL)
- Обработка видео
- Построение message формата
- Парсинг JSON ответов

**Принципы**:
- **DRY**: Общая функциональность в одном месте
- **Pure Functions**: Без побочных эффектов

### 4. Data Layer (Schemas)

**Файлы**: `app/schemas.py`

**Ответственность**:
- Определение структур данных (DTOs)
- Валидация входных данных
- Документация API (через Pydantic)

**Принципы**:
- **Type Safety**: Строгая типизация через Pydantic
- **Validation**: Автоматическая валидация на уровне схем

```python
class Grounding2DRequest(ImageInferenceRequest):
    categories: Optional[List[str]] = None
    output_format: OutputFormat = OutputFormat.JSON
    include_attributes: bool = False
```

### 5. Configuration Layer

**Файлы**: `app/config.py`

**Ответственность**:
- Централизованная конфигурация
- Загрузка из переменных окружения
- Валидация конфигурации

**Принципы**:
- **Separation of Concerns**: Конфигурация отделена от кода
- **12-Factor App**: Конфигурация через environment variables

## Применение SOLID принципов

### Single Responsibility Principle (SRP)

Каждый класс/модуль имеет одну ответственность:

- **Routes**: Только HTTP обработка
- **Services**: Только бизнес-логика для конкретной задачи
- **Engine**: Только работа с моделью
- **Utils**: Только вспомогательные функции

### Open/Closed Principle (OCP)

Система открыта для расширения, закрыта для модификации:

- Легко добавить новый сервис без изменения существующего кода
- Легко добавить новый endpoint
- Легко добавить новый output format

### Liskov Substitution Principle (LSP)

Наследование используется правильно:

```python
class ImageInferenceRequest(InferenceRequest):
    # Расширяет базовый класс, не нарушая контракт
```

### Interface Segregation Principle (ISP)

Интерфейсы разделены по функциональности:

- Разные request схемы для разных задач
- Каждый сервис использует только нужные методы engine

### Dependency Inversion Principle (DIP)

Зависимости направлены от конкретного к абстрактному:

- Services зависят от Engine (абстракция), а не от vLLM напрямую
- API зависит от Services, а не от деталей реализации

## Применение DRY принципа

### Переиспользование кода

1. **Общие утилиты** в `utils.py`:
   - `get_image_from_request()` - используется всеми image-based сервисами
   - `build_image_message()` - единое построение message формата
   - `parse_json_response()` - единый парсинг JSON

2. **Базовые схемы**:
   - `InferenceRequest` - базовый класс для всех запросов
   - `ImageInferenceRequest` - для image-based задач
   - `VideoInferenceRequest` - для video-based задач

3. **Общий engine**:
   - Все сервисы используют один экземпляр engine
   - Переиспользование кода подготовки данных

## Паттерны проектирования

### 1. Dependency Injection

FastAPI's Depends для инъекции зависимостей:

```python
def get_engine() -> Qwen3VLInferenceEngine:
    return _engine

@router.post("/endpoint")
async def endpoint(engine: Engine = Depends(get_engine)):
    ...
```

### 2. Factory Pattern

Сервисы создаются в endpoints по требованию:

```python
service = GroundingService(engine)
return await service.perform_grounding(request)
```

### 3. Strategy Pattern

Разные стратегии обработки через разные сервисы:
- GroundingService
- SpatialUnderstandingService
- VideoUnderstandingService
- etc.

### 4. Builder Pattern

Построение сложных message структур:

```python
def build_image_message(image_input, prompt, ...):
    messages = [...]
    return messages
```

## Data Flow

```
HTTP Request
    ↓
FastAPI Route (API Layer)
    ↓
Pydantic Validation (Schema Layer)
    ↓
Service (Business Logic Layer)
    ↓
Utils (Helper Functions)
    ↓
Inference Engine (Core Layer)
    ↓
vLLM Model
    ↓
Response Processing
    ↓
HTTP Response
```

## Управление жизненным циклом

### Lifespan Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    engine = Qwen3VLInferenceEngine(...)
    set_engine(engine)

    yield

    # Shutdown
    # Cleanup code here
```

### Singleton Pattern для Engine

Один экземпляр engine на весь сервер:

```python
_engine: Qwen3VLInferenceEngine = None

def set_engine(engine: Qwen3VLInferenceEngine):
    global _engine
    _engine = engine
```

## Обработка ошибок

### Try-Catch в сервисах

```python
try:
    result = self.engine.generate(...)
    return InferenceResponse(success=True, result=result)
except Exception as e:
    logger.error(f"Task failed: {e}")
    return InferenceResponse(success=False, error=str(e))
```

### HTTP Exceptions в API Layer

```python
if _engine is None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Engine not initialized"
    )
```

## Логирование

Структурированное логирование на всех уровнях:

```python
logger = logging.getLogger(__name__)
logger.info("Starting inference...")
logger.error(f"Failed: {e}")
```

## Тестируемость

### Легко тестируемая архитектура

- **Unit Tests**: Тестирование сервисов с mock engine
- **Integration Tests**: Тестирование endpoints с test client
- **Mocking**: Легко подменить engine или utils

Пример:
```python
def test_grounding_service():
    mock_engine = Mock(spec=Qwen3VLInferenceEngine)
    service = GroundingService(mock_engine)
    # Test service logic
```

## Масштабируемость

### Horizontal Scaling

- Stateless сервер - легко масштабируется горизонтально
- Load balancer перед несколькими инстансами

### Vertical Scaling

- Tensor parallelism для распределения модели
- GPU memory utilization control

## Безопасность

### Input Validation

- Pydantic схемы валидируют все входные данные
- Type safety предотвращает ошибки типов

### CORS Configuration

- Настраиваемый CORS через конфигурацию
- Контроль origins, methods, headers

## Производительность

### Оптимизации

1. **vLLM**: Высокопроизводительный inference engine
2. **Async/Await**: Асинхронная обработка запросов
3. **Batch Processing**: vLLM поддерживает батчинг
4. **GPU Optimization**: PagedAttention, tensor parallelism

## Расширяемость

### Добавление нового сервиса

1. Создать файл `app/services/new_service.py`
2. Реализовать класс сервиса
3. Создать Pydantic схему в `schemas.py`
4. Добавить endpoint в `routes.py`

### Добавление нового output формата

1. Добавить в `OutputFormat` enum
2. Обновить prompt building в сервисе
3. Готово!

## Заключение

Архитектура проекта обеспечивает:

✅ **Модульность** - чёткое разделение ответственности
✅ **Поддерживаемость** - легко понять и изменить код
✅ **Тестируемость** - легко покрыть тестами
✅ **Масштабируемость** - легко расширить функциональность
✅ **Производительность** - оптимизированный inference
✅ **Читаемость** - чистый, организованный код

Следование принципам SOLID и DRY делает код профессиональным, надёжным и готовым к production использованию.
