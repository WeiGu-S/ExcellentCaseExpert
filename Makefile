# 测试用例生成器项目的Makefile

.PHONY: help install install-dev test test-unit test-integration lint format type-check clean build sync run

help:
	@echo "可用命令："
	@echo "  install      使用uv安装生产环境依赖"
	@echo "  install-dev  使用uv安装开发环境依赖"
	@echo "  sync         使用uv同步依赖"
	@echo "  test         运行所有测试"
	@echo "  test-unit    仅运行单元测试"
	@echo "  test-integration 仅运行集成测试"
	@echo "  lint         运行代码检查"
	@echo "  format       使用black格式化代码"
	@echo "  type-check   使用mypy进行类型检查"
	@echo "  clean        清理构建产物"
	@echo "  build        构建包"
	@echo "  run          运行应用程序"

install:
	uv pip install -r requirements.txt

install-dev:
	uv pip install -r requirements.txt -r requirements-dev.txt
	uv pip install -e .

sync:
	uv pip sync requirements.txt requirements-dev.txt

test:
	uv run pytest tests/ -v

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v

lint:
	uv run flake8 src/ tests/

format:
	uv run black src/ tests/

type-check:
	uv run mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:
	uv buildru
n:
	python src/main.py