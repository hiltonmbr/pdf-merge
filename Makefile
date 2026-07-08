.DEFAULT_GOAL := help

.PHONY: help sync run lint format check test lock clean

help: ## 📖 Mostra esta ajuda
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║       📄 pdf-merge — Auto Dossier PDF Merger           ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  📋 Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-12s\033[0m → %s\n", $$1, $$2}'
	@echo ""

sync: ## 🔄 Sincroniza dependências com uv
	@echo "🔄  Sincronizando dependências..."
	@uv sync
	@echo "✅  Dependências atualizadas com sucesso!"

lock: ## 🔒 Atualiza o lockfile (uv.lock)
	@echo "🔒  Atualizando lockfile..."
	@uv lock
	@echo "✅  uv.lock atualizado!"

run: ## 🚀 Executa o merger (ex: make run ARGS="--cv-path /pasta")
	@echo "🚀  Iniciando pdf-merge..."
	@uv run python3 main.py $(ARGS)

lint: ## 🔍 Verifica o código com Ruff
	@echo "🔍  Verificando código com Ruff..."
	@uv run ruff check
	@echo "✅  Nenhum problema encontrado!"

format: ## ✨ Formata o código com Ruff
	@echo "✨  Formatando código com Ruff..."
	@uv run ruff format
	@echo "✅  Código formatado!"

check: lint format ## 🔍✨ Executa lint + format

test: ## 🧪 Executa a suíte de testes
	@echo "🧪  Executando testes..."
	@uv run pytest -q
	@echo "✅  Testes concluídos!"

clean: ## 🧹 Remove caches e arquivos temporários
	@echo "🧹  Limpando arquivos temporários..."
	@rm -rf __pycache__ core/__pycache__ .ruff_cache
	@rm -f temp_*.pdf pdf_merger.log
	@echo "✅  Limpeza concluída!"
