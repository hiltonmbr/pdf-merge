# 📄 pdf-merge — Auto Dossier PDF Merger

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen)](https://opensource.org/licenses/MIT)

> **Junta PDFs de múltiplas pastas em um único documento** com capas estilizadas por seção. Leitura e escrita 100% local via sistema de arquivos — usa o Google Drive Desktop Sync como transporte, sem chamadas de API.

---

## ✨ Features

- 📁 **Detecção automática de subpastas** — cada subvira uma seção com capa própria
- 🖋️ **Gera capas estilizadas** com ReportLab
- 📄 **Mescla tudo em um PDF único**
- 🔖 **Bookmarks/outline por seção** — navegue direto pelo painel do leitor de PDF
- 💾 **Salva direto no Google Drive sincronizado** (ou qualquer pasta local)
- 🔒 **Zero dependências de rede** — sem OAuth, sem API calls, offline
- ⚙️ **uv** para gerenciamento de dependências (rápido e confiável)
- 🔍 **Ruff** para lint e formatação
- ✅ **Testes automatizados** com pytest + **CI** no GitHub Actions
- 🚀 **Makefile** com comandos simples

---

## 🗂️ Estrutura do Projeto

```
/
├── core/
│   └── utils.py          # Lógica principal (coleta, merge, save)
├── main.py               # Ponto de entrada (CLI com argparse)
├── config.py             # Carrega configuração do .env
├── tests/                # Suíte de testes (pytest)
├── .github/workflows/    # CI: lint, format e testes
├── Makefile              # Comandos: run, lint, format, test, sync, etc.
├── .env                  # Config local (NÃO commitado)
├── .env.example          # Template de configuração
├── pyproject.toml        # Projeto e dependências
├── uv.lock               # Lockfile (commitar)
└── .gitignore
```

---

## 📂 Estrutura de Pastas Esperada

O script lê **subpastas** dentro de um diretório raiz. Cada subpasta vira uma seção com capa.

```
📁 Curriculum Vitae/           ← CV_PATH
├── 📁 01 - Currículo Lattes
│   └── cv_lattes.pdf
├── 📁 02 - Formação Acadêmica
│   └── 01_diplomas.pdf
├── 📁 03 - Atividades de Ensino
│   └── ...
└── 📁 Curriculum Vitae Compilado/  ← OUTPUT_DIR (opcional)
    └── cv_hilton.pdf              ← PDF gerado
```

**Dica:** Use prefixos numéricos (`01 -`, `02 -`) para facilitar a leitura — a ordem das seções já é numérica (1, 2, ... 10), com ou sem zero à esquerda.

---

## ⚙️ Setup

### 1️⃣ Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Clonar e instalar dependências

```bash
git clone <repo>
cd pdf-merge
uv sync
```

### 3️⃣ Configurar

```bash
cp .env.example .env
```

Edite `.env` com o caminho da sua pasta:

```bash
# Caminho da pasta com subpastas de PDFs
CV_PATH=/caminho/para/sua/pasta

# Subpasta de output (relativa a CV_PATH ou caminho absoluto)
OUTPUT_DIR=Curriculum Vitae Compilado

# Nome do arquivo final
MERGED_PDF_NAME=cv_hilton.pdf
```

---

## ▶️ Uso

### Via Make

```bash
make run
```

### Via CLI

```bash
uv run python3 main.py --cv-path /caminho/da/pasta
```

### Output em diretório diferente

```bash
uv run python3 main.py --output-dir "/outro/caminho"
```

### Ajuda

```bash
uv run python3 main.py --help
```

---

## 🛠️ Comandos Disponíveis

| Comando | Ação |
|---|---|
| `make sync` | Instala/sincroniza dependências |
| `make run` | Executa o merger |
| `make lint` | Verifica código com Ruff |
| `make format` | Formata código com Ruff |
| `make check` | Lint + format |
| `make test` | Executa a suíte de testes (pytest) |
| `make clean` | Limpa caches e temporários |

---

## 📊 Exemplo de Output

```
============================================================
📄 PDF MERGE
============================================================

📂 Coletando PDFs de: /caminho/Curriculum Vitae

============================================================
📂 01 - Currículo Lattes
============================================================
  📄 cv_lattes.pdf (442 KB)
  ✓ 1 PDF(s) coletados
...

✅ Coleta concluída:
  • Seções: 14
  • PDFs:   87

🔗 Mesclando PDFs...

============================================================
[1/14] 01 - CURRÍCULO LATTES
  ✓ 46 página(s) adicionadas
...
============================================================
✅ Merge concluído — 314 páginas no total
============================================================

💾 Salvando PDF final...
💾 Salvo em: .../Curriculum Vitae Compilado/cv_hilton.pdf (19 MB)

============================================================
✅ PROCESSO CONCLUÍDO!
============================================================
📄 cv_hilton.pdf
📂 .../Curriculum Vitae Compilado
📊 14 seções, 87 PDFs
============================================================
```

Logs detalhados em `pdf_merger.log`.

---

## 📋 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `CV_PATH` | Caminho da pasta com subpastas de PDFs | — (obrigatório) |
| `OUTPUT_DIR` | Subpasta ou caminho absoluto de saída | `Curriculum Vitae Compilado` |
| `MERGED_PDF_NAME` | Nome do arquivo PDF final | `cv_hilton.pdf` |

---

## 🔒 Segurança

- `.env` está no `.gitignore` — nunca é commitado
- Nenhuma credencial, token ou acesso remoto é necessário
- Tudo roda localmente, sem chamadas de rede

---

## 📜 Licença

MIT — © LEMA-UFPB
