# Docker Deployment Guide для Qwen3-VL Inference Server

Этот гайд покрывает все аспекты развертывания сервера с использованием Docker и Docker Compose.

## Содержание

- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Управление контейнерами](#управление-контейнерами)
- [Мониторинг и логи](#мониторинг-и-логи)
- [Troubleshooting](#troubleshooting)

## Требования

### Обязательные требования

1. **Docker** (версия 20.10+)
   ```bash
   docker --version
   ```

2. **Docker Compose** (версия 2.0+)
   ```bash
   docker-compose --version
   ```

3. **NVIDIA Docker Runtime** (для GPU support)
   ```bash
   # Установка nvidia-docker2
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list

   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker

   # Проверка
   docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
   ```

4. **GPU с минимум 24GB VRAM** (для модели Qwen3-VL-235B)

### Рекомендуемые характеристики сервера

- **CPU**: 16+ cores
- **RAM**: 64GB+
- **GPU**: NVIDIA A100, H100 или аналогичные с 40GB+ VRAM
- **Storage**: 200GB+ SSD для моделей и кэша

## Быстрый старт

### 1. Подготовка

```bash
# Клонируйте или перейдите в директорию проекта
cd D:\Projects\Qwen_Vl_inference

# Создайте .env файл из шаблона
cp .env.docker .env

# Отредактируйте .env файл
nano .env  # или vim, или любой редактор
```

### 2. Настройка .env

Минимальная конфигурация:

```env
MODEL_PATH=Qwen/Qwen3-VL-235B-A22B-Instruct
GPU_MEMORY_UTILIZATION=0.70
HOST_PORT=8000
```

Для gated models добавьте HuggingFace token:

```env
HF_TOKEN=hf_your_token_here
```

### 3. Запуск

```bash
# Сборка образа
docker-compose build

# Запуск в detached mode
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### 4. Проверка

```bash
# Проверка health status
curl http://localhost:8000/api/health

# Просмотр Swagger UI
open http://localhost:8000/docs  # или в браузере
```

## Конфигурация

### Структура файлов

```
.
├── Dockerfile                  # Основной Dockerfile
├── docker-compose.yml          # Базовая конфигурация
├── docker-compose.dev.yml      # Development override
├── docker-compose.prod.yml     # Production override
├── .dockerignore              # Исключения для Docker build
└── .env                       # Переменные окружения (создайте из .env.docker)
```

### Переменные окружения

#### Основные переменные

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `MODEL_PATH` | Путь к модели или HF model ID | `Qwen/Qwen3-VL-235B-A22B-Instruct` |
| `HF_TOKEN` | HuggingFace access token | - |
| `HOST_PORT` | Порт на хосте | `8000` |
| `GPU_MEMORY_UTILIZATION` | Использование GPU памяти (0.0-1.0) | `0.70` |
| `TENSOR_PARALLEL_SIZE` | Количество GPU | auto |

#### Дополнительные переменные

См. полный список в [.env.docker](.env.docker)

### GPU Configuration

#### Использование всех GPU

```yaml
# docker-compose.yml (по умолчанию)
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

#### Использование конкретных GPU

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0', '1']  # GPU 0 и 1
          capabilities: [gpu]
```

#### Tensor Parallelism

В `.env`:
```env
TENSOR_PARALLEL_SIZE=2  # Использовать 2 GPU
```

## Development Deployment

Для разработки используйте `docker-compose.dev.yml`:

```bash
# Запуск в dev режиме
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Особенности dev режима:
# - Hot reload при изменении кода
# - Debug логи
# - Монтирование исходников
# - Interactive mode
```

### Dev конфигурация

```yaml
# docker-compose.dev.yml
services:
  qwen3-vl-server:
    environment:
      - DEBUG=True
      - LOG_LEVEL=DEBUG
    volumes:
      - ./app:/app/app:rw  # Hot reload
    command: uvicorn app.main:app --reload --log-level debug
```

## Production Deployment

### 1. Подготовка production конфигурации

```bash
# Создайте production .env
cp .env.docker .env.prod

# Настройте production параметры
nano .env.prod
```

Production `.env.prod`:
```env
MODEL_PATH=Qwen/Qwen3-VL-235B-A22B-Instruct
GPU_MEMORY_UTILIZATION=0.80
HOST_PORT=8000
DEBUG=False
ALLOW_ORIGINS=https://yourdomain.com
```

### 2. Запуск в production

```bash
# Сборка production образа
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Запуск
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

### 3. Production best practices

#### Использование внешних volumes

Отредактируйте `docker-compose.prod.yml`:

```yaml
volumes:
  model-cache:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/qwen-models  # Ваш путь
```

#### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '16'
      memory: 64G
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

#### Security

```yaml
security_opt:
  - no-new-privileges:true
read_only: true  # Если поддерживается
tmpfs:
  - /tmp
  - /app/tmp
```

### 4. Reverse Proxy с Nginx

Создайте `nginx.conf`:

```nginx
upstream qwen_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://qwen_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Для больших payload (images/videos)
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

Docker Compose с Nginx:

```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - qwen3-vl-server
    networks:
      - qwen-network
```

## Управление контейнерами

### Основные команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Пересборка и перезапуск
docker-compose up -d --build

# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f qwen3-vl-server

# Выполнение команды в контейнере
docker-compose exec qwen3-vl-server bash

# Просмотр использования ресурсов
docker stats qwen3-vl-server
```

### Обновление контейнера

```bash
# Pull новый код
git pull

# Пересборка
docker-compose build --no-cache

# Restart с новым образом
docker-compose up -d
```

### Очистка

```bash
# Удалить контейнеры и volumes
docker-compose down -v

# Удалить неиспользуемые образы
docker image prune -a

# Полная очистка Docker
docker system prune -a --volumes
```

## Мониторинг и логи

### Health Check

```bash
# Через Docker
docker-compose ps

# Через API
curl http://localhost:8000/api/health

# Автоматический health check (в docker-compose.yml)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 120s
```

### Логирование

#### Просмотр логов

```bash
# Все логи
docker-compose logs

# С follow (real-time)
docker-compose logs -f

# Последние N строк
docker-compose logs --tail=100

# С timestamp
docker-compose logs -t
```

#### Конфигурация логов

```yaml
# docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### Экспорт логов

```bash
# В файл
docker-compose logs > logs.txt

# Только ошибки
docker-compose logs 2>&1 | grep ERROR
```

### Мониторинг ресурсов

```bash
# GPU usage
nvidia-smi

# Внутри контейнера
docker-compose exec qwen3-vl-server nvidia-smi

# Container stats
docker stats qwen3-vl-server

# Disk usage
docker-compose exec qwen3-vl-server df -h
```

### Интеграция с Prometheus + Grafana

Добавьте в `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  prometheus-data:
  grafana-data:
```

## Troubleshooting

### Проблема: Container не запускается

**Решение 1**: Проверьте логи
```bash
docker-compose logs qwen3-vl-server
```

**Решение 2**: Проверьте GPU доступность
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

**Решение 3**: Увеличьте start_period в health check
```yaml
healthcheck:
  start_period: 300s  # Увеличьте для больших моделей
```

### Проблема: Out of Memory (OOM)

**Решение**: Уменьшите GPU_MEMORY_UTILIZATION

```env
GPU_MEMORY_UTILIZATION=0.5
```

Или добавьте memory limits:

```yaml
deploy:
  resources:
    limits:
      memory: 32G
```

### Проблема: Модель не загружается

**Решение 1**: Проверьте HF_TOKEN для gated models
```env
HF_TOKEN=hf_your_token_here
```

**Решение 2**: Используйте локальную модель
```yaml
volumes:
  - /path/to/local/model:/models:ro
```

```env
MODEL_PATH=/models/Qwen3-VL-235B-A22B-Instruct
```

### Проблема: Медленный inference

**Решение 1**: Используйте tensor parallelism
```env
TENSOR_PARALLEL_SIZE=2
```

**Решение 2**: Увеличьте GPU memory utilization
```env
GPU_MEMORY_UTILIZATION=0.85
```

**Решение 3**: Оптимизируйте image sizes
```python
{
    "min_pixels": 32768,
    "max_pixels": 1048576
}
```

### Проблема: Permission denied

**Решение**: Проверьте permissions для volumes

```bash
# Создайте директории с правильными правами
sudo mkdir -p /data/qwen-models
sudo chown -R 1000:1000 /data/qwen-models
```

### Проблема: Network connectivity

**Решение**: Проверьте Docker network

```bash
# Inspect network
docker network inspect qwen_qwen-network

# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

## Полезные скрипты

### Скрипт для автоматического деплоя

Создайте `deploy.sh`:

```bash
#!/bin/bash

# Deploy script for Qwen3-VL Inference Server

set -e

echo "🚀 Starting deployment..."

# Pull latest code
echo "📦 Pulling latest code..."
git pull

# Build image
echo "🏗️  Building Docker image..."
docker-compose build --no-cache

# Stop old container
echo "🛑 Stopping old container..."
docker-compose down

# Start new container
echo "▶️  Starting new container..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for health check..."
sleep 30

# Check health
echo "🏥 Checking health..."
curl -f http://localhost:8000/api/health || exit 1

echo "✅ Deployment successful!"
docker-compose ps
```

Сделайте исполняемым:
```bash
chmod +x deploy.sh
./deploy.sh
```

### Backup script

Создайте `backup.sh`:

```bash
#!/bin/bash

# Backup script

BACKUP_DIR="/backup/qwen-$(date +%Y%m%d-%H%M%S)"

echo "📦 Creating backup at $BACKUP_DIR"

mkdir -p $BACKUP_DIR

# Backup volumes
docker run --rm \
  -v qwen_model-cache:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/model-cache.tar.gz -C /data .

echo "✅ Backup completed!"
```

## Заключение

Теперь у вас есть полная конфигурация для Docker deployment:

- ✅ Multi-stage Dockerfile для оптимизации размера
- ✅ Docker Compose для оркестрации
- ✅ Development и Production конфигурации
- ✅ GPU support через nvidia-docker
- ✅ Health checks и мониторинг
- ✅ Логирование и troubleshooting
- ✅ Best practices для production

Для дополнительной информации см.:
- [README.md](README.md) - основная документация
- [QUICKSTART.md](QUICKSTART.md) - быстрый старт
- [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура
