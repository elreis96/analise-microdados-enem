# 🎓 Análise Comparativa dos Microdados do ENEM

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Arquitetura do Código](#arquitetura-do-código)
- [Saídas Geradas](#saídas-geradas)
- [Troubleshooting](#troubleshooting)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Fontes de Dados](#fontes-de-dados)
- [Licença](#licença)

---
## 🎯 Sobre o Projeto

Este projeto realiza uma **análise comparativa** dos microdados do ENEM, focando especialmente em participantes dos grupos de renda:
- **Grupo A**: Nenhuma renda
- **Grupo B**: Até R$ 1.300,00

A análise utiliza **PostgreSQL** para armazenamento eficiente dos dados e **Python** para processamento e visualização.

### 📊 Objetivo

Identificar e visualizar as diferenças de desempenho no ENEM entre diferentes grupos socioeconômicos, considerando variáveis como:
- Notas nas diferentes áreas de conhecimento
- Cor/Raça
- Sexo
- Estado (UF)

---

## ✨ Funcionalidades

- ✅ **ETL automatizado**: Carrega dados dos CSVs para PostgreSQL
- ✅ **Cache inteligente**: Detecta se os dados já foram carregados
- ✅ **Análise SQL otimizada**: Queries eficientes com JOIN
- ✅ **Visualizações profissionais**: Gráficos em alta resolução (300 DPI)
- ✅ **Exportação para Power BI**: CSV formatado para análises adicionais
- ✅ **Estatísticas descritivas**: Média, mediana e desvio padrão
- ✅ **Segurança**: Credenciais protegidas em arquivo `.env`
- ✅ **Tratamento de erros**: Mensagens claras e logging detalhado

---

## 📦 Requisitos

### Sistema Operacional
- Windows 10/11
- Linux (Ubuntu 20.04+, Debian, etc.)
- macOS 10.15+

### Software
- **Python**: 3.10 ou superior
- **PostgreSQL**: 12 ou superior
- **pgAdmin** (opcional, mas recomendado)

### Dados
- Microdados do ENEM 2024 (disponíveis no site do INEP)
  - `PARTICIPANTES_2024.csv` (~4,3 milhões de registros)
  - `RESULTADOS_2024.csv` (~4,3 milhões de registros)

---

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/analise-enem.git
cd analise-enem
```

### 2. Crie um Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

**Conteúdo do `requirements.txt`:**
```txt
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
sqlalchemy>=2.0.0
psycopg[binary]>=3.1.0
python-dotenv>=1.0.0
chardet>=5.0.0              # Detecção automática de encoding
```

**Alternativa (se psycopg falhar):**
```bash
pip install pg8000>=1.30.0
```

### 4. Instale o PostgreSQL

#### Windows:
1. Baixe em: https://www.postgresql.org/download/windows/
2. Execute o instalador
3. Anote a senha do usuário `postgres`

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### macOS:
```bash
brew install postgresql
brew services start postgresql
```

---

## ⚙️ Configuração

### 1. Criar o Banco de Dados

Abra o **pgAdmin** ou terminal PostgreSQL:

```sql
CREATE DATABASE enem_db;
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Windows (PowerShell)
New-Item .env

# Linux/Mac
touch .env
```

**Conteúdo do `.env`:**

```env
# Configurações do Banco de Dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=enem_db
DB_USER=postgres
DB_PASS=SUA_SENHA_AQUI

# Caminhos dos Arquivos
ARQUIVO_PARTICIPANTES=microdados_enem_2024/DADOS/PARTICIPANTES_2024.csv
ARQUIVO_RESULTADOS=microdados_enem_2024/DADOS/RESULTADOS_2024.csv

# Nomes das Tabelas
TABELA_PARTICIPANTES=participantes
TABELA_RESULTADOS=resultados
```

⚠️ **IMPORTANTE**: 
- Substitua `SUA_SENHA_AQUI` pela sua senha real do PostgreSQL
- **NUNCA** commite o arquivo `.env` no Git!

### 3. Baixar os Microdados do ENEM

1. Acesse: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
2. Baixe os microdados do ano desejado (ex: 2024)
3. Extraia os arquivos para a pasta do projeto:

```
seu_projeto/
├── microdados_enem_2024/
│   └── DADOS/
│       ├── PARTICIPANTES_2024.csv
│       └── RESULTADOS_2024.csv
```

### 4. Criar o `.gitignore`

```gitignore
# Arquivo de ambiente (senhas)
.env

# Dados sensíveis
microdados_enem_2024/

# Resultados das análises
analise_enem_*/

# Python
__pycache__/
*.py[cod]
venv/
.Python

# IDEs
.vscode/
.idea/
*.swp
```

---

## 🎮 Como Usar

### Execução Básica

```bash
python dados.py
```

### O que acontece na primeira execução:

1. ✅ **Verifica dependências** (drivers PostgreSQL)
2. ✅ **Carrega configurações** do `.env`
3. ✅ **Conecta ao PostgreSQL**
4. ⏳ **Carrega dados** (pode demorar 1-2 horas!)
   - Lê CSVs em chunks de 50.000 registros
   - Insere no PostgreSQL
5. ✅ **Executa análise SQL**
6. ✅ **Gera gráficos e estatísticas**
7. ✅ **Salva resultados** em pasta com timestamp

### Execuções seguintes:

- ⚡ **MUITO mais rápido** (segundos!)
- Os dados já estão no banco
- Pula direto para a análise

---

## 📁 Estrutura do Projeto

```
analise-enem/
│
├── dados.py                          # Script principal
├── .env                              # Credenciais (NÃO commitar!)
├── .env.example                      # Modelo de configuração
├── .gitignore                        # Arquivos ignorados pelo Git
├── requirements.txt                  # Dependências Python
├── README.md                         # Esta documentação
│
├── microdados_enem_2024/            # Dados do INEP
│   └── DADOS/
│       ├── PARTICIPANTES_2024.csv
│       └── RESULTADOS_2024.csv
│
└── analise_enem_YYYYMMDD_HHMMSS/    # Resultados (gerados)
    ├── dados_analise_enem.csv        # Para Power BI
    ├── estatisticas_descritivas.csv  # Médias, medianas, etc.
    ├── boxplots.png                  # Distribuição de notas
    ├── comparativo_raca.png          # Análise por cor/raça
    ├── comparativo_sexo.png          # Análise por sexo
    └── diferenca_estados.png         # Análise por UF
```

---

## 🏗️ Arquitetura do Código

### Módulos e Funções

```python
# 1. CONFIGURAÇÕES INICIAIS
verificar_driver_postgresql()    # Detecta psycopg ou pg8000
carregar_config()                # Lê variáveis do .env

# 2. CONEXÃO COM O BANCO
conectar_db()                    # Cria engine SQLAlchemy

# 3. ETL (CARGA DOS DADOS)
carregar_tabela_csv()            # Carrega participantes
carregar_tabela_resultados()     # Carrega resultados + JOIN
verificar_e_carregar_tabelas()   # Orquestra ETL

# 4. ANÁLISE
extrair_e_processar_dados()      # Query SQL + processamento

# 5. SAÍDAS
gerar_csv_para_powerbi()         # Exporta CSV
gerar_estatisticas()             # Calcula estatísticas
gerar_graficos()                 # Cria visualizações

# 6. FLUXO PRINCIPAL
main()                           # Orquestra tudo
```

### Fluxo de Execução

```
┌─────────────────────────┐
│  Carregar .env          │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Verificar Driver       │ (psycopg ou pg8000)
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Conectar PostgreSQL    │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Tabelas existem?       │
└───────────┬─────────────┘
            │
      ┌─────┴─────┐
      │           │
    SIM          NÃO
      │           │
      │     ┌─────▼─────────────┐
      │     │ Carregar CSVs     │ (1-2 horas)
      │     │ - Participantes   │
      │     │ - Resultados      │
      │     └─────┬─────────────┘
      │           │
      └─────┬─────┘
            │
┌───────────▼─────────────┐
│  Executar SQL Query     │ (JOIN das tabelas)
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Processar DataFrame    │
│  - Limpar NaN           │
│  - Calcular médias      │
│  - Criar labels         │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Gerar Saídas           │
│  - CSV (Power BI)       │
│  - Estatísticas         │
│  - 4 Gráficos PNG       │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  ✅ Concluído!          │
└─────────────────────────┘
```

---

## 📊 Saídas Geradas

### 1. **dados_analise_enem.csv**
- Dados processados prontos para o Power BI
- Colunas: notas, grupo de renda, sexo, cor/raça, UF, etc.
- Encoding: UTF-8 com BOM (compatível com Excel)

### 2. **estatisticas_descritivas.csv**
| Grupo Renda | Métrica | CN | CH | LC | MT | Redação | Média |
|-------------|---------|----|----|----|----|---------|-------|
| Nenhuma Renda | mean | 480 | 510 | 495 | 465 | 550 | 487 |
| Nenhuma Renda | median | 475 | 505 | 490 | 460 | 540 | 482 |
| Até 1,3k | mean | 505 | 530 | 515 | 490 | 580 | 510 |

### 3. **Gráficos (PNG, 300 DPI)**

#### boxplots.png
- 6 box plots (2x3 grid)
- Compara distribuição de notas entre os grupos
- Mostra: Média Objetiva, CN, CH, LC, MT, Redação

#### comparativo_raca.png
- Barras agrupadas por cor/raça
- Dois painéis (Nenhuma Renda | Até 1,3k)
- Ordem: Branca, Parda, Preta, Amarela, Indígena, Não Declarado

#### comparativo_sexo.png
- Barras comparando Feminino vs Masculino
- Dois painéis por grupo de renda
- Paleta: plasma

#### diferenca_estados.png
- Barras horizontais ordenadas por diferença
- Eixo X: diferença de pontos (+ ou -)
- Linha vertical em 0 para referência
- Paleta: coolwarm (azul = negativo, vermelho = positivo)

---

## 🐛 Troubleshooting

### ❌ Erro: "Nenhum driver PostgreSQL encontrado"

**Causa**: psycopg e pg8000 não estão instalados

**Solução**:
```bash
pip install psycopg[binary]
# OU
pip install pg8000
```

---

### ❌ Erro: "DLL load failed while importing _psycopg"

**Causa**: Python 3.14 é muito novo, psycopg não tem DLLs compatíveis

**Solução**:
```bash
pip uninstall psycopg psycopg2 psycopg2-binary
pip install pg8000
```

---

### ❌ Erro: "Senha do banco (DB_PASS) não configurada"

**Causa**: Arquivo `.env` não existe ou está vazio

**Solução**:
1. Crie o arquivo `.env` na raiz do projeto
2. Adicione: `DB_PASS=sua_senha`
3. Verifique se está no mesmo diretório do `dados.py`

---

### ❌ Erro: "Falha na conexão"

**Causa**: PostgreSQL não está rodando ou credenciais erradas

**Solução**:
1. Abra o pgAdmin
2. Tente conectar manualmente
3. Verifique se a senha no `.env` está correta
4. Confirme que o banco `enem_db` existe

**Windows - Verificar serviço:**
```powershell
Get-Service -Name postgresql*
```

**Linux - Verificar serviço:**
```bash
sudo systemctl status postgresql
```

---

### ❌ Erro: "Arquivo não encontrado: PARTICIPANTES_2024.csv"

**Causa**: Caminho incorreto no `.env`

**Solução**:
1. Verifique se os CSVs estão na pasta correta
2. Ajuste o caminho no `.env`:
```env
ARQUIVO_PARTICIPANTES=caminho/correto/PARTICIPANTES_2024.csv
```

---

### ❌ Erro: "coluna p.q006 não existe"

**Causa**: Nomes de colunas sem aspas no SQL

**Solução**: Já corrigido no código! Use aspas duplas:
```sql
p."Q006" -- ✅ Correto
p.Q006   -- ❌ Errado
```

---

### ⚠️ A carga está muito lenta

**Normal!** A primeira carga demora **1-2 horas** porque:
- São ~4,3 milhões de registros
- Driver pg8000 é mais lento
- PostgreSQL está indexando

---

### Dicas:

- Deixe rodando o script em segundo plano

- Evite usar o computador enquanto o ETL está em execução

- Execuções futuras serão instantâneas (dados já estarão no banco)

---
### 🧰 Tecnologias Utilizadas

O projeto foi desenvolvido utilizando tecnologias amplamente adotadas nas áreas de **engenharia de dados**, **análise estatística** e **visualização interativa**, garantindo desempenho, segurança e reprodutibilidade dos resultados.

| Categoria          | Tecnologia / Fonte                                                                 | Descrição                                       |
| ------------------ | ---------------------------------------------------------------------------------- | ----------------------------------------------- |
| 🐍 Linguagem       | **Python 3.10+**                                                                   | Utilizado para processamento de dados, ETL e automação das análises |
| 🗃️ Banco de Dados | **PostgreSQL 12+**                                                                 | Armazenamento relacional dos microdados do ENEM, com queries otimizadas |
| 📊 Análise         | **Pandas**, **NumPy**, **SQLAlchemy**                                              | Manipulação tabular, cálculos estatísticos e integração com SQL |
| 📈 Visualização    | **Matplotlib**, **Seaborn**, **Power BI**                                          | Criação de gráficos, comparativos e dashboards analíticos |
| 🔐 Segurança       | **python-dotenv**                                                                  | Gerenciamento seguro de credenciais e variáveis de ambiente |
| ⚙️ Automação       | **Chardet**, **Time**, **OS**                                                      | Detecção de encoding, controle de tempo e automação de tarefas do sistema |


---

### 💡 Observações

- O projeto é **totalmente reproduzível** em qualquer ambiente com Python 3.10+ e PostgreSQL.  
- Todas as dependências estão listadas no arquivo [`requirements.txt`](./requirements.txt).  
- As credenciais sensíveis são gerenciadas via arquivo `.env`, que **não deve ser versionado**.  
- Os dados do ENEM foram obtidos diretamente do portal de dados abertos do **[INEP](https://www.gov.br/inep)**.

---

### 🧠 Fontes de Dados

Os dados utilizados nesta análise foram obtidos do portal oficial do INEP:
📊 Microdados do Enem 2024 > 🔗 Fonte oficial dos dados: [Microdados do Enem 2024 - INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)


O projeto utilizou os seguintes arquivos disponibilizados publicamente:

PARTICIPANTES_2024.csv – Informações demográficas e socioeconômicas dos candidatos

RESULTADOS_2024.csv – Desempenho dos participantes em cada área de conhecimento

🔒 Todos os dados são anônimos e de acesso público, seguindo as diretrizes de transparência e LGPD.

---

### 📜 Licença

Este projeto é distribuído sob a licença MIT — veja o arquivo LICENSE
 para mais detalhes.

⚠️ Este repositório tem fins exclusivamente educacionais e analíticos.
Nenhuma informação pessoal dos candidatos é utilizada ou divulgada.
