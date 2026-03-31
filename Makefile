# ===============================
# Настройки проекта
# ===============================
# Каталоги с кодом/тестами
PY_SRCS=src/
include .env
export
# Порог для Radon:
# - запрещаем функции со сложностью CC уровней E/F
# - минимальный Maintainability Index (MI)
RADON_MIN_MI=50
# ===============================
# Служебные цели
# ===============================

.PHONY: help install lint fmt type security cc mi hal raw check

help:
	@echo "Доступные цели:"
	@echo " lint - ruff check (с автофиксом)"
	@echo " fmt - ruff format"
	@echo " type - mypy (проверка типов)"
	@echo " security - bandit (скан безопасности)"
	@echo " cc - radon cc (цикломатическая сложность) + quality gate"
	@echo " mi - radon mi (индекс поддерживаемости) + quality gate"
	@echo " hal - radon hal (метрика халстеда)"
	@echo " raw - radon raw (SLOC, LLOC, комментарии, число функций/классов)"
	@echo " check - быстрый локальный quality gate (ruff+mypy+bandit+radon)"


# ===============================
# Ruff: линт и форматирование
# ===============================
lint:
	uv run ruff check $(PY_SRCS) --fix

fmt:
	uv run ruff format $(PY_SRCS)

# ===============================
# Mypy: проверка типов
# (если есть mypy.ini / pyproject.toml, он подхватится автоматически)
# ===============================

type:
	uv run mypy $(PY_SRCS)

# ===============================
# Bandit: анализ безопасности
# ===============================
security:
# -r: рекурсивно, -lll: максимум строгости вывода,
# -x: исключения (подправьте под проект)
	uv run bandit -r $(PY_SRCS) -lll -x .venv,venv,build,dist,migrations

# ===============================
# Radon: метрики
# ===============================
# Цикломатическая сложность: подробный вывод (-s), среднее (-a)
cc:
	uv run radon cc -s -a $(PY_SRCS)
	@# QUALITY GATE: проваливаем, если есть элементы со сложностью E/F
	@if uv run radon cc -s $(PY_SRCS) | grep -E " - [EF] \("; then \
		echo "❌ Radon CC: обнаружены функции со сложностью E/F"; \
		exit 1; \
	else \
		echo "✅ Radon CC: нет функций с E/F"; \
	fi

# Индекс поддерживаемости
mi:
	@uv run radon mi -s $(PY_SRCS)
	@MI_BAD=$$(uv run radon mi -s $(PY_SRCS) | tr -d '()' | awk -v limit=$(RADON_MIN_MI) '$$NF ~ /^[0-9.]+$$/ && $$NF+0 < limit {print $$0}'); \
	if [ -n "$$MI_BAD" ]; then \
		echo "❌ Radon MI: найден MI < $(RADON_MIN_MI)"; \
		exit 1; \
	else \
		echo "✅ Radon MI: все файлы с MI >= $(RADON_MIN_MI)"; \
	fi
# Метрика халстеда
hal:
	uv run radon hal $(PY_SRCS)
# Метрика Raw
raw:
	uv run radon raw $(PY_SRCS)

test:
	@echo "Подготовка тестовой базы данных..."
	docker exec delivery_mysql mysql -uroot -p"$(DB_ROOT_PASS)" -e \
		"CREATE DATABASE IF NOT EXISTS delivery_db_test; \
		GRANT ALL PRIVILEGES ON delivery_db_test.* TO '$(DB_USER)'@'%'; \
		FLUSH PRIVILEGES;"
	@echo "Запуск тестов..."
	TESTING=1 DB_HOST=127.0.0.1 REDIS_HOST=127.0.0.1 uv run pytest -v --cov=src tests/

# ===============================
# Комплексные цели
# ===============================
# Локальный быстрый прогон с автофиксом Ruff
check: lint fmt type security cc mi hal raw 
