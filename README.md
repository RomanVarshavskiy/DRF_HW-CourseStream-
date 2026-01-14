# CourseStream API

CourseStream — это backend-приложение на Django REST Framework (DRF) для управления онлайн-курсами, уроками и подписками с интеграцией платежной системы Stripe и фоновыми задачами через Celery.

## Основной функционал

- **Управление обучением**: CRUD для курсов и уроков.
- **Подписки**: Возможность пользователей подписываться на обновления курсов.
- **Платежи**: Интеграция со Stripe для оплаты доступа к материалам (поддержка курсов и отдельных уроков).
- **Профили пользователей**: Кастомная модель пользователя (авторизация по email), личный кабинет с историей платежей.
- **Права доступа**: Гибкая система разрешений (Владелец, Модератор, Публичный доступ).
- **Уведомления**: Отправка уведомлений об обновлении контента в Telegram и на Email.
- **Автоматизация**: Фоновые задачи (Celery) для очистки неактивных пользователей и рассылки уведомлений.
- **Документация**: Автоматическая генерация документации API через Swagger/Redoc.

## Технологический стек

- **Python 3.13**
- **Django / DRF**
- **PostgreSQL** (База данных)
- **Redis** (Брокер для Celery)
- **Celery / Celery Beat** (Фоновые и периодические задачи)
- **Stripe API** (Оплата)
- **Poetry** (Управление зависимостями)
- **Docker** (Опционально для развертывания)

## Настройка и запуск проекта локально

### 1. Клонируйте репозиторий
```bash
git clone <URL_вашего_репозитория>
cd DRF_HW
```

### 2. Установите зависимости
```bash
poetry install
```
Если Poetry не установлен, установите его.

### 3. Настройте переменные окружения
Скопируйте шаблон .env_template в .env:

```bash
cp .env_template .env
```
**Откройте .env и заполните все необходимые переменные:**

SECRET_KEY=your_secret_key
POSTGRES_DB=coursestream
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_test_...
EMAIL_HOST=...
EMAIL_PORT=...
EMAIL_USER=...
EMAIL_PASSWORD=...
TELEGRAM_BOT_TOKEN=...

### 4. Поднимите локальную базу данных и Redis
Для локальной разработки удобно использовать Docker Compose, но можно и вручную:

**Через Docker Compose:**

```bash
docker-compose up -d db redis
```

**Вручную:**

PostgreSQL: убедитесь, что сервер PostgreSQL запущен и есть база с именем POSTGRES_DB.

Redis: запустите redis-server локально.

### 5. Примените миграции
```bash
poetry run python manage.py migrate
```

### 6. Создайте суперпользователя
```bash
poetry run python manage.py csu
```

### 7. Запуск сервера Django
```bash
poetry run python manage.py runserver
```
Сервер будет доступен по адресу: http://127.0.0.1:8000/

### 8. Запуск Celery для фоновых задач
В отдельных терминалах запустите:

**Worker:**

```bash
poetry run celery -A config worker -l info
```

**Beat** (периодические задачи):

```bash
poetry run celery -A config beat -l info
```
### 9. Проверка работы
Django API: http://127.0.0.1:8000/swagger/ или /redoc/

**Redis:**

```bash
redis-cli ping
```
# Ответ должен быть PONG

**PostgreSQL:**

```bash
psql -U <POSTGRES_USER> -d <POSTGRES_DB> -h localhost
```
**Celery:** в логах воркера должны появляться задачи.

### 10. Запуск тестов и покрытие кода
```bash
poetry run coverage run --source='.' manage.py test
poetry run coverage report
Запуск через Docker Compose
```
#### Если у вас установлен Docker и Docker Compose, вы можете запустить весь проект (Django, PostgreSQL, Redis, Celery) одной командой.

**Шаги для запуска:**
- **Настройте переменные окружения:**
Убедитесь, что у вас создан файл .env. Для работы в Docker убедитесь, что POSTGRES_HOST установлен как db, а CELERY_BROKER_URL использует redis в качестве хоста.

- **Соберите и запустите контейнеры:**

```bash
docker-compose up --build
```
### Проверка работоспособности сервисов:
Django (web): http://127.0.0.1:8000/

PostgreSQL (db):

```bash
docker-compose logs db
docker-compose exec db pg_isready -U <ваш_postgres_user>
```
Redis:

```bash
docker-compose exec redis redis-cli ping
```
Celery Worker:

```bash
docker-compose logs celery
```
Celery Beat:

```bash
docker-compose logs celery-beat
```
### Документация API
После запуска сервера документация доступна по адресам:

Swagger UI: http://127.0.0.1:8000/swagger/

ReDoc: http://127.0.0.1:8000/redoc/

### Тестирование
```bash
poetry run coverage run --source='.' manage.py test
poetry run coverage report
```
### Права доступа (Permissions)
- **Модераторы:** Могут просматривать и редактировать любые курсы/уроки, но не могут их создавать или удалять.

- **Владельцы:** Полный доступ (CRUD) к своим объектам.

- **Обычные пользователи:** Просмотр доступен только после авторизации. Профиль другого пользователя отображается в сокращенном виде.

### Автоматические задачи
- **deactivate_inactive_users:** Каждый день в 03:00 деактивирует пользователей, которые не заходили в систему более 30 дней.

- **four_hours_notification:** Раз в 30 минут проверяет обновления курсов и рассылает уведомления подписчикам (не чаще чем раз в 4 часа для одного курса).

## Деплой и CI/CD
В проекте настроена автоматизация через GitHub Actions. При каждом пуше в ветку main запускается процесс проверки кода, тестирования и автоматического деплоя на удаленный сервер.

### Настройка удаленного сервера (Ubuntu/Debian)
**Установите Docker и Docker Compose:**

```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable --now docker
```
### Подготовьте директорию проекта:
Создайте папку, указанную в **DEPLOY_DIR** (например, /home/username/coursestream), и разместите там файлы docker-compose.yml и конфигурацию nginx/nginx.conf.

### Настройте .env на сервере:
Создайте файл **.env** в директории проекта и заполните его боевыми значениями.

### Настройка GitHub Secrets

Для корректной работы GitHub Actions (workflow) необходимо добавить следующие секреты в настройках вашего репозитория (**Settings -> Secrets and variables -> Actions**):

| Секрет | Описание |
| :--- | :--- |
| `SECRET_KEY` | Секретный ключ Django |
| `DOCKER_HUB_USERNAME` | Ваш логин на Docker Hub |
| `DOCKER_HUB_ACCESS_TOKEN` | Access Token от Docker Hub |
| `SSH_KEY` | Приватный SSH-ключ для доступа к серверу |
| `SSH_USER` | Имя пользователя на сервере (например, `root`) |
| `SERVER_IP` | IP-адрес вашего сервера |
| `DEPLOY_DIR` | Путь к папке проекта на сервере (например, `/home/app/coursestream`) |

### Workflow шаги

1.  **Lint**: Проверка кода на соответствие стандартам (flake8).
2.  **Test**: Запуск тестов внутри временного контейнера с PostgreSQL.
3.  **Build**: Сборка Docker-образа и отправка его на Docker Hub с тегами `latest` и SHA коммита.
4.  **Deploy**: Подключение к серверу по SSH, загрузка новых образов (`docker compose pull`) и перезапуск контейнеров.

### Ручной деплой
Если вам нужно обновить приложение вручную на сервере:
```bash
docker compose pull
docker compose up -d --remove-orphans
```
