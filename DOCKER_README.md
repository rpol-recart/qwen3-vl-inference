# Docker Quick Reference для Qwen3-VL Inference Server

Быстрая справка по Docker командам и использованию.

## 📋 Содержание

- [Makefile команды](#makefile-команды)
- [Docker Compose команды](#docker-compose-команды)
- [Скрипты](#скрипты)
- [Конфигурационные файлы](#конфигурационные-файлы)

## Makefile команды

Makefile предоставляет удобные команды для управления проектом:

### Общие команды

```bash
make help           # Показать все доступные команды
make version        # Показать версии Docker, Docker Compose, Python
```

### Setup и Build

```bash
make setup          # Создать .env файл из шаблона
make install        # Установить Python зависимости локально
make build          # Собрать Docker образ
make build-no-cache # Собрать Docker образ без кэша
```

### Запуск и остановка

```bash
make up             # Запустить сервисы (detached mode)
make up-build       # Собрать и запустить
make down           # Остановить сервисы
make down-volumes   # Остановить и удалить volumes
make restart        # Перезапустить сервисы
```

### Development

```bash
make dev            # Запустить в dev режиме (с hot reload)
make dev-build      # Собрать и запустить в dev режиме
make dev-down       # Остановить dev сервисы
```

### Production

```bash
make prod           # Запустить в production режиме
make prod-build     # Собрать и запустить в production
make prod-down      # Остановить production сервисы
```

### Deployment

```bash
make deploy-dev     # Полный deployment для dev
make deploy-prod    # Полный deployment для production
```

### Мониторинг

```bash
make logs           # Показать логи (follow mode)
make logs-tail      # Последние 100 строк логов
make health         # Проверить health endpoint
make ps             # Показать запущенные контейнеры
make stats          # Показать использование ресурсов
make gpu            # Показать использование GPU
```

### Утилиты

```bash
make shell          # Открыть shell в контейнере
make backup         # Создать backup
make restore BACKUP_DIR=path  # Восстановить из backup
make docs           # Открыть API документацию в браузере
```

### Тестирование

```bash
make test           # Запустить тесты
make test-api       # Тестировать API endpoints
```

### Очистка

```bash
make clean          # Удалить контейнеры, образы, volumes
make clean-cache    # Очистить Docker build cache
make clean-all      # Полная очистка
```

## Docker Compose команды

### Базовые команды

```bash
# Запуск
docker-compose up                 # Запустить (foreground)
docker-compose up -d              # Запустить (background)
docker-compose up --build         # Собрать и запустить

# Остановка
docker-compose down               # Остановить и удалить контейнеры
docker-compose down -v            # + удалить volumes
docker-compose stop               # Только остановить (не удалять)

# Перезапуск
docker-compose restart            # Перезапустить сервисы
docker-compose restart qwen3-vl-server  # Перезапустить конкретный сервис
```

### Development режим

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

### Production режим

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Логи

```bash
docker-compose logs                    # Все логи
docker-compose logs -f                 # Follow mode
docker-compose logs -f qwen3-vl-server # Конкретный сервис
docker-compose logs --tail=100         # Последние 100 строк
docker-compose logs --since 30m        # За последние 30 минут
```

### Информация

```bash
docker-compose ps                      # Статус сервисов
docker-compose top                     # Запущенные процессы
docker-compose config                  # Валидация и вывод конфигурации
docker-compose images                  # Используемые образы
```

### Выполнение команд

```bash
docker-compose exec qwen3-vl-server bash           # Открыть shell
docker-compose exec qwen3-vl-server nvidia-smi     # Запустить команду
docker-compose exec qwen3-vl-server python --version
```

### Build

```bash
docker-compose build                   # Собрать все сервисы
docker-compose build --no-cache        # Без кэша
docker-compose build qwen3-vl-server   # Конкретный сервис
```

## Скрипты

Все скрипты находятся в директории `scripts/`:

### deploy.sh

Автоматический deployment:

```bash
./scripts/deploy.sh dev   # Development deployment
./scripts/deploy.sh prod  # Production deployment
```

Что делает:
- Проверяет prerequisites (Docker, nvidia-docker)
- Собирает образ
- Останавливает старые контейнеры
- Запускает новые контейнеры
- Проверяет health check

### backup.sh

Создание backup:

```bash
./scripts/backup.sh                    # Default: ./backups
./scripts/backup.sh /custom/path       # Custom path
```

Создает backup:
- .env и docker-compose файлов
- Model cache volume
- HuggingFace cache volume
- Transformers cache volume

### restore.sh

Восстановление из backup:

```bash
./scripts/restore.sh ./backups/qwen-backup-YYYYMMDD-HHMMSS
```

### logs.sh

Просмотр логов:

```bash
./scripts/logs.sh                      # Все логи
./scripts/logs.sh -f                   # Follow mode
./scripts/logs.sh -n 100               # Последние 100 строк
./scripts/logs.sh --prod               # Production logs
./scripts/logs.sh -f --dev             # Dev logs с follow
```

### health-check.sh

Проверка здоровья сервиса:

```bash
./scripts/health-check.sh                          # Default URL
./scripts/health-check.sh http://custom:8000/api/health
```

Проверяет:
- HTTP статус код
- JSON response
- GPU статус

## Конфигурационные файлы

### Docker файлы

| Файл | Описание |
|------|----------|
| `Dockerfile` | Multi-stage Dockerfile с CUDA support |
| `.dockerignore` | Исключения для Docker build |

### Docker Compose файлы

| Файл | Описание |
|------|----------|
| `docker-compose.yml` | Базовая конфигурация |
| `docker-compose.dev.yml` | Development override (hot reload, debug) |
| `docker-compose.prod.yml` | Production override (security, limits) |
| `docker-compose.override.yml.example` | Пример кастомных настроек |

### Environment файлы

| Файл | Описание |
|------|----------|
| `.env.docker` | Шаблон для Docker окружения |
| `.env` | Ваша конфигурация (создайте из .env.docker) |

### Другие файлы

| Файл | Описание |
|------|----------|
| `Makefile` | Makefile с удобными командами |
| `DOCKER_DEPLOYMENT.md` | Полная документация по Docker |
| `DOCKER_README.md` | Этот файл - краткая справка |

## Примеры использования

### Первый запуск (Development)

```bash
# 1. Setup
make setup
# Отредактируйте .env

# 2. Deploy
make deploy-dev

# 3. Check
make health
make logs
```

### Первый запуск (Production)

```bash
# 1. Setup
make setup
# Отредактируйте .env для production

# 2. Build and deploy
make deploy-prod

# 3. Monitor
make health
make logs-tail
make gpu
```

### Обновление сервиса

```bash
# Pull новый код
git pull

# Rebuild и restart
make build-no-cache
make restart

# Check
make health
```

### Создание backup перед обновлением

```bash
# Backup
make backup

# Update
git pull
make build-no-cache
make restart

# If something goes wrong:
# make restore BACKUP_DIR=./backups/qwen-backup-XXXXXXXX
```

### Development workflow

```bash
# Запустить в dev режиме с hot reload
make dev

# В другом терминале - смотреть логи
make logs

# Изменить код в app/
# Сервер автоматически перезагрузится

# Тестировать через curl или browser
curl http://localhost:8000/api/health
```

### Production deployment

```bash
# Build production image
make prod-build

# Check health
make health

# Monitor
make stats
make gpu

# View logs if issues
make logs-tail
```

### Troubleshooting

```bash
# Проверить статус
make ps

# Проверить health
make health

# Посмотреть логи
make logs-tail

# Проверить GPU
make gpu

# Войти в контейнер
make shell

# Перезапустить
make restart

# Если не помогает - rebuild
make down
make build-no-cache
make up
```

## Быстрые команды для типичных задач

### "Просто запусти"

```bash
make deploy-dev
```

### "Покажи логи"

```bash
make logs
```

### "Все ли работает?"

```bash
make health && make gpu
```

### "Перезапусти сервис"

```bash
make restart
```

### "Полная переустановка"

```bash
make down-volumes
make build-no-cache
make up
```

### "Создай backup"

```bash
make backup
```

### "Открой shell"

```bash
make shell
```

### "Очисти все"

```bash
make clean
```

## Полезные алиасы для .bashrc или .zshrc

```bash
# Добавьте в ~/.bashrc или ~/.zshrc

alias qwen-up='make up'
alias qwen-down='make down'
alias qwen-logs='make logs'
alias qwen-health='make health'
alias qwen-shell='make shell'
alias qwen-gpu='make gpu'
alias qwen-restart='make restart'
```

## Для Windows пользователей

Если вы на Windows без WSL:

### PowerShell команды

```powershell
# Вместо make используйте docker-compose напрямую
docker-compose up -d
docker-compose logs -f
docker-compose ps
docker-compose down

# Или используйте WSL для make
wsl make up
wsl make logs
```

### Используйте Git Bash

Make работает в Git Bash на Windows:

```bash
# В Git Bash
make deploy-dev
make logs
make health
```

## Дополнительная информация

- Полная документация: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- Основная документация: [README.md](README.md)
- Быстрый старт: [QUICKSTART.md](QUICKSTART.md)
- Архитектура: [ARCHITECTURE.md](ARCHITECTURE.md)
