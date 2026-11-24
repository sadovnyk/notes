# notes-api

Невеликий REST API для нотаток (FastAPI + SQLite). Це полігон для практики **GitHub Actions, Docker і деплою**: код навмисно простий, головна робота відбувається в `.github/` і `Dockerfile`.

<!-- Сюди додаси бейджі CI, коли напишеш workflow -->

## Можливості

| Метод | Шлях | Опис |
|---|---|---|
| GET | `/` | Назва та версія сервісу |
| GET | `/health` | Healthcheck: 200 якщо все ок, 503 якщо БД недоступна |
| GET | `/metrics` | Uptime і кількість запитів |
| GET | `/notes?search=&limit=&offset=` | Список нотаток з пошуком і пагінацією |
| GET | `/notes/{id}` | Одна нотатка |
| POST | `/notes` | Створити (🔒 якщо задано `API_KEY`) |
| PUT | `/notes/{id}` | Оновити (🔒) |
| DELETE | `/notes/{id}` | Видалити (🔒) |

Swagger UI: `http://localhost:8000/docs`

## Конфігурація (змінні середовища)

| Змінна | За замовчуванням | Навіщо |
|---|---|---|
| `APP_NAME` | `notes-api` | Назва сервісу |
| `APP_ENV` | `development` | `staging` / `production`: зручно для GitHub Environments |
| `APP_VERSION` | `0.0.0-dev` | Підставляй з CI (тег або git SHA) і перевіряй через `/health` після деплою |
| `DATABASE_PATH` | `notes.db` | Шлях до SQLite-файлу; у Docker винось у volume |
| `API_KEY` | порожньо | Якщо задано, запити на запис вимагають заголовок `X-API-Key`. Тримай у GitHub Secrets |

## Локальний запуск

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

make run                          # або: uvicorn app.main:app --reload
```

Перевірка:

```bash
curl localhost:8000/health
curl -X POST localhost:8000/notes -H "Content-Type: application/json" -d '{"title":"Перша нотатка"}'
```

## Перевірки якості

```bash
make lint     # ruff check + ruff format --check
make format   # автовиправлення
make test     # pytest
make cov      # pytest з покриттям, створює coverage.xml
```

Ці ж команди запускатиме твій CI.

## Структура

```
app/
  main.py      # FastAPI-застосунок, ендпоінти, middleware логування
  config.py    # налаштування з env
  models.py    # Pydantic-схеми
  storage.py   # робота з SQLite
tests/         # pytest (TestClient, тимчасова БД на кожен тест)
requirements.txt       # залежності для продакшну (для Docker-образу)
requirements-dev.txt   # + тести й лінтер (для CI)
pyproject.toml         # налаштування ruff, pytest, coverage
```

---

## 🗺️ DevOps-роадмап (твоя частина)

Відмічай пункти, коли закінчуєш. Кожен етап краще робити окремим PR.

### Етап 1: CI
- [ ] `ci.yml`: lint + test на `push` і `pull_request`
- [ ] Matrix: Python 3.11 / 3.12 / 3.13, ubuntu + windows
- [ ] Кеш pip
- [ ] `coverage.xml` як artifact
- [ ] Бейдж статусу в README
- [ ] Branch protection на `main` з обов'язковою перевіркою CI

### Етап 2: Docker
- [ ] `Dockerfile` (підказка: multi-stage, непривілейований користувач, `HEALTHCHECK` на `/health`)
- [ ] `.dockerignore`
- [ ] Workflow: збірка та push у `ghcr.io` з `GITHUB_TOKEN` і мінімальними `permissions`
- [ ] Теги образу: `latest`, short SHA, semver
- [ ] Передай `APP_VERSION` в образ через `build-args`

### Етап 3: Релізи
- [ ] Workflow на тег `v*` → GitHub Release з changelog
- [ ] `needs` + `outputs` між jobs

### Етап 4: Деплой
- [ ] Environments `staging` і `production` (для prod — required reviewers)
- [ ] `API_KEY` в environment secrets, `APP_ENV` в environment variables
- [ ] Деплой на безкоштовний хостинг
- [ ] Smoke-тест після деплою: `curl /health` і перевірка, що `version` збігається
- [ ] `concurrency` для деплою

### Етап 5: Автоматизація
- [ ] `schedule`: нічний прогін тестів
- [ ] `workflow_dispatch` з `inputs` (вибір environment)
- [ ] Reusable workflow (`workflow_call`) для тестів
- [ ] Власний composite action (`.github/actions/setup-app`)

### Етап 6: Безпека
- [ ] Dependabot (pip, github-actions, docker)
- [ ] CodeQL
- [ ] Сканування Docker-образу (наприклад, Trivy)
- [ ] ⭐ Бонус: OIDC до хмарного провайдера замість статичних ключів
