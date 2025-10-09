import os
import sys
import time
import warnings
from datetime import datetime
from typing import Dict, Any
from urllib.parse import quote_plus

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

# Ignorar avisos futuros para uma saída mais limpa
warnings.filterwarnings("ignore", category=FutureWarning)

# ==================== 1. CONFIGURAÇÕES INICIAIS ==================== #

def verificar_driver_postgresql() -> str:
    """
    Verifica e retorna o driver PostgreSQL disponível.
    Prioriza 'psycopg' e, se não disponível, tenta 'pg8000'.
    Encerra o programa se nenhum driver for encontrado.
    """
    try:
        import psycopg
        print(f"✅ psycopg (versão {psycopg.__version__}) encontrado")
        return 'psycopg'
    except ImportError:
        print("⚠️  psycopg não encontrado. Tentando driver alternativo...")
        try:
            import pg8000
            print("✅ pg8000 encontrado (driver alternativo)")
            return 'pg8000'
        except ImportError:
            print("\n❌ ERRO: Nenhum driver PostgreSQL (psycopg ou pg8000) foi encontrado!")
            print("   Instale com: pip install psycopg[binary] ou pip install pg8000")
            sys.exit(1)


def detectar_encoding_arquivo(caminho_arquivo: str, sample_size: int = 100000) -> str:
    """
    Detecta automaticamente o encoding de um arquivo CSV.
    
    Args:
        caminho_arquivo: Caminho do arquivo
        sample_size: Tamanho da amostra em bytes
    
    Returns:
        String com o encoding detectado
    """
    try:
        import chardet
        
        with open(caminho_arquivo, 'rb') as f:
            raw_data = f.read(sample_size)
        
        resultado = chardet.detect(raw_data)
        encoding = resultado['encoding']
        confianca = resultado['confidence']
        
        print(f"   🔍 Encoding detectado: {encoding} (confiança: {confianca*100:.1f}%)")
        
        # Fallback para ISO-8859-1 se confiança muito baixa
        if confianca < 0.7:
            print(f"   ⚠️  Confiança baixa, usando ISO-8859-1 como padrão")
            return 'ISO-8859-1'
        
        return encoding
    
    except ImportError:
        print("   ℹ️  chardet não instalado, usando ISO-8859-1 como padrão")
        print("   ℹ️  Utilize 'pip install chardet' para melhor detecção de encoding")
        return 'ISO-8859-1'
    except Exception as e:
        print(f"   ⚠️  Erro ao detectar encoding: {e}, usando ISO-8859-1 como padrão")
        return 'ISO-8859-1'
    


def carregar_config() -> Dict[str, Any]:
    """
    Carrega e valida as configurações do banco de dados a partir das variáveis de ambiente.
    Retorna um dicionário com as configurações.
    Encerra o programa se alguma configuração obrigatória estiver faltando.
    """
    config = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': int(os.getenv('DB_PORT')),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASS': os.getenv('DB_PASS'),
        'ARQUIVO_PARTICIPANTES': os.getenv('ARQUIVO_PARTICIPANTES'),
        'ARQUIVO_RESULTADOS': os.getenv('ARQUIVO_RESULTADOS'),
        'TABELA_PARTICIPANTES': os.getenv('TABELA_PARTICIPANTES'),
        'TABELA_RESULTADOS': os.getenv('TABELA_RESULTADOS')
    }
    
    if not config['DB_PASS']:
        print("\n❌ ERRO: Senha do banco (DB_PASS) não configurada no arquivo .env!")
        print("   Crie um arquivo .env com: DB_PASS=sua_senha")
        sys.exit(1)
    
    return config


# ==================== 2. CONEXÃO COM O BANCO ==================== #

def conectar_db(config: Dict[str, Any], driver: str) -> Engine:
    """
    Conecta ao banco de dados PostgreSQL usando SQLAlchemy.
    Retorna o engine de conexão.
    Encerra o programa se a conexão falhar.
    """
    print("\n🚀 Conectando ao banco de dados...")
    senha_tratada = quote_plus(config['DB_PASS'])
    db_url = f'postgresql+{driver}://{config["DB_USER"]}:{senha_tratada}@{config["DB_HOST"]}:{config["DB_PORT"]}/{config["DB_NAME"]}'
    
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL ({version.split(',')[0]})")
        return engine
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        print("\n💡 Verifique:")
        print("   1. PostgreSQL está rodando?")
        print("   2. Credenciais no .env estão corretas?")
        print("   3. O banco de dados existe?")
        sys.exit(1)


# ==================== 3. ETL (CARGA DOS DADOS) ==================== #

def carregar_tabela_csv(engine: Engine, nome_tabela: str, caminho_csv: str, chunksize: int = 50000):
    """
    Carrega dados de um arquivo CSV para uma tabela no banco de dados em chunks.
    
    Args:
        engine: Engine de conexão SQLAlchemy
        nome_tabela: Nome da tabela no banco
        caminho_csv: Caminho do arquivo CSV
        chunksize: Tamanho dos chunks para processamento
    """
    print(f"\n📊 Carregando tabela '{nome_tabela}'...")
    print(f"   Arquivo: {caminho_csv}")
    
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")
    
    start = time.time()
    chunk_iter = pd.read_csv(
        caminho_csv, 
        sep=';', 
        encoding='ISO-8859-1', 
        chunksize=chunksize, 
        low_memory=False
    )
    
    for i, chunk in enumerate(chunk_iter):
        print(f"   🔄️...processando lote {i+1} ({len(chunk):,} registros)")
        chunk.to_sql(
            nome_tabela, 
            engine, 
            if_exists='append' if i > 0 else 'replace', 
            index=False
        )
    
    elapsed = time.time() - start
    print(f"✅ Tabela '{nome_tabela}' carregada em {elapsed:.2f}s ({elapsed/60:.2f} min)")


def carregar_tabela_resultados(engine: Engine, config: Dict[str, Any], chunksize: int = 50000):
    """
    Carrega a tabela de resultados, adicionando a chave NU_INSCRICAO dos participantes.
    
    Args:
        engine: Engine de conexão SQLAlchemy
        config: Dicionário com configurações
        chunksize: Tamanho dos chunks para processamento
    """
    nome_tabela = config['TABELA_RESULTADOS']
    caminho_csv = config['ARQUIVO_RESULTADOS']
    
    print(f"\n📊 Carregando tabela '{nome_tabela}' (com JOIN de inscrições)...")
    print(f"   📁 Arquivo: {caminho_csv}")
    
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")
    
    start = time.time()
    
    # Ler números de inscrição dos participantes
    print("   📖...lendo números de inscrição...")
    df_inscricoes = pd.read_csv(
        config['ARQUIVO_PARTICIPANTES'], 
        sep=';', 
        encoding='ISO-8859-1', 
        usecols=['NU_INSCRICAO']
    )
    
    # Ler resultados
    print("   📖...lendo resultados...")
    df_resultados = pd.read_csv(
        caminho_csv, 
        sep=';', 
        encoding='ISO-8859-1', 
        low_memory=False
    )
    
    # Adicionar coluna de inscrição
    df_resultados['NU_INSCRICAO'] = df_inscricoes['NU_INSCRICAO']
    
    # Salvar no banco
    print("   💾...salvando no banco de dados...")
    df_resultados.to_sql(
        nome_tabela, 
        engine, 
        index=False, 
        if_exists='replace', 
        chunksize=chunksize
    )
    
    elapsed = time.time() - start
    print(f"✅ Tabela '{nome_tabela}' carregada em {elapsed:.2f}s ({elapsed/60:.2f} min)")


def verificar_carregar(engine: Engine, config: Dict[str, Any]):
    """
    Verifica se as tabelas existem no banco e carrega se necessário.
    
    Args:
        engine: Engine de conexão SQLAlchemy
        config: Dicionário com configurações
    """
    inspector = inspect(engine)
    tabela_p = config['TABELA_PARTICIPANTES']
    tabela_r = config['TABELA_RESULTADOS']
    
    tem_participantes = inspector.has_table(tabela_p)
    tem_resultados = inspector.has_table(tabela_r)
    
    if tem_participantes and tem_resultados:
        print("\n✅ Tabelas já existem no banco. Pulando etapa de carga (ETL).")
        return
    
    print("\n📥 Iniciando carga de dados (ETL)")
    print("   😴 (Isso pode demorar bastante, mas só ocorre uma vez)")
    
    if not tem_participantes:
        carregar_tabela_csv(
            engine, 
            tabela_p, 
            config['ARQUIVO_PARTICIPANTES']
        )
    
    if not tem_resultados:
        carregar_tabela_resultados(engine, config)


# ==================== 4. ANÁLISE E VISUALIZAÇÃO ==================== #

def extrair_processar(engine: Engine) -> pd.DataFrame:
    """
    Extrai e processa os dados necessários para a análise comparativa.
    Retorna um DataFrame com as colunas relevantes e a média das notas objetivas.
    
    Args:
        engine: Engine de conexão SQLAlchemy
        
    Returns:
        DataFrame processado pronto para análise
    """
    print("\n📊 Extraindo e processando dados para análise...")
    
    query = """
    SELECT
        p."Q006", p."TP_SEXO", p."TP_COR_RACA", p."SG_UF_PROVA",
        r."NU_NOTA_CN", r."NU_NOTA_CH", r."NU_NOTA_LC", r."NU_NOTA_MT", r."NU_NOTA_REDACAO"
    FROM participantes AS p
    JOIN resultados AS r ON p."NU_INSCRICAO" = r."NU_INSCRICAO"
    WHERE p."Q006" IN ('A', 'B');
    """
    
    start = time.time()
    df = pd.read_sql_query(query, engine)
    print(f"   📊 Dados extraídos: {len(df):,} registros em {time.time() - start:.2f}s")
    
    # Limpar dados
    col_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    df.dropna(subset=col_notas, inplace=True)
    
    # Calcular média objetiva
    df['NOTA_MEDIA_OBJETIVA'] = df[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT']].mean(axis=1)
    
    # Criar labels
    df['GRUPO_RENDA'] = df['Q006'].map({'A': 'Nenhuma Renda', 'B': 'Até 1,3k'})
    
    print(f"✅ Processamento concluído: {len(df):,} registros válidos\n")
    return df


# ==================== 5. GERAÇÃO DE SAÍDAS ==================== #

def gerar_csv_para_pbi(df: pd.DataFrame, pasta_resultados: str):
    """
    Exporta o DataFrame processado para CSV (uso no Power BI).
    
    Args:
        df: DataFrame processado
        pasta_resultados: Pasta onde salvar o arquivo
    """
    print("📤 Exportando dados para CSV...")
    caminho = os.path.join(pasta_resultados, 'dados_analise_enem.csv')
    df.to_csv(caminho, index=False, encoding='utf-8-sig')
    print(f"   📁 Arquivo salvo: {caminho}")


def gerar_estatisticas(df: pd.DataFrame, pasta_resultados: str):
    """
    Gera estatísticas descritivas e salva em CSV.
    
    Args:
        df: DataFrame processado
        pasta_resultados: Pasta onde salvar o arquivo
    """
    print("📈 Gerando estatísticas descritivas...")
    col_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO', 'NOTA_MEDIA_OBJETIVA']
    stats = df.groupby('GRUPO_RENDA')[col_notas].agg(['mean', 'median', 'std']).round(2)
    caminho = os.path.join(pasta_resultados, 'estatisticas_descritivas.csv')
    stats.to_csv(caminho)
    print(f"   📁 Arquivo salvo: {caminho}")


def gerar_graficos(df: pd.DataFrame, pasta_resultados: str):
    """
    Gera todos os gráficos comparativos e salva como imagens.
    
    Args:
        df: DataFrame processado
        pasta_resultados: Pasta onde salvar os gráficos
    """
    print("🎨 Gerando gráficos...")
    plt.style.use('seaborn-v0_8-whitegrid')
    start_time = time.time()
    
    # Fazer cópia para não modificar o original
    df = df.copy()
    
    # GRÁFICO 1: Box Plots
    print("   🎨...box plots")
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    col_plot = ['NOTA_MEDIA_OBJETIVA', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    tit_plot = ['Média Objetiva', 'Ciências da Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação']
    fig.suptitle('Distribuição de Notas: Nenhuma Renda vs. Até 1,3k', fontsize=20, weight='bold')
    
    for i, ax in enumerate(axes.flatten()):
        sns.boxplot(data=df, x='GRUPO_RENDA', y=col_plot[i], ax=ax, palette='viridis', width=0.5)
        ax.set_title(tit_plot[i], fontsize=12)
        ax.set_xlabel('')
        ax.set_ylabel('Nota')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    caminho = os.path.join(pasta_resultados, 'boxplots.png')
    plt.savefig(caminho, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"      💾 Salvo: {caminho}")
    
    # GRÁFICO 2: Cor/Raça
    if 'TP_COR_RACA' in df.columns:
        print("   ...comparativo por cor/raça")
        df['COR_RACA_LABEL'] = df['TP_COR_RACA'].map({
            0: 'Não D.', 1: 'Branca', 2: 'Preta', 3: 'Parda', 4: 'Amarela', 5: 'Indígena'
        })
        g = sns.catplot(
            data=df, x='COR_RACA_LABEL', y='NOTA_MEDIA_OBJETIVA', col='GRUPO_RENDA',
            kind='bar', palette='viridis', height=6, aspect=1.2,
            order=['Branca', 'Parda', 'Preta', 'Amarela', 'Indígena', 'Não D.']
        )
        g.fig.suptitle('Nota Média por Cor/Raça dentro de cada Grupo de Renda', y=1.03)
        g.set_axis_labels("Cor/Raça", "Nota Média")
        g.set_titles("Grupo: {col_name}")
        caminho = os.path.join(pasta_resultados, 'comparativo_raca.png')
        plt.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"      💾 Salvo: {caminho}")
    
    # GRÁFICO 3: Sexo
    if 'TP_SEXO' in df.columns:
        print("   🎨...comparativo por sexo")
        df['SEXO_LABEL'] = df['TP_SEXO'].map({'F': 'Feminino', 'M': 'Masculino'})
        g = sns.catplot(
            data=df, x='SEXO_LABEL', y='NOTA_MEDIA_OBJETIVA', col='GRUPO_RENDA',
            kind='bar', palette='plasma', height=6, aspect=1.2
        )
        g.fig.suptitle('Nota Média por Sexo dentro de cada Grupo de Renda', y=1.03, fontsize=14)
        g.set_axis_labels("Sexo", "Nota Média")
        g.set_titles("Grupo: {col_name}")
        caminho = os.path.join(pasta_resultados, 'comparativo_sexo.png')
        plt.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"      💾 Salvo: {caminho}")
    
    # GRÁFICO 4: Diferença por Estado
    if 'SG_UF_PROVA' in df.columns:
        print("   🎨...diferença por estado")
        media_uf_pivot = df.groupby(['SG_UF_PROVA', 'GRUPO_RENDA'])['NOTA_MEDIA_OBJETIVA'].mean().unstack()
        media_uf_pivot['DIFERENCA'] = media_uf_pivot['Até 1,3k'] - media_uf_pivot['Nenhuma Renda']
        media_uf_pivot = media_uf_pivot.sort_values('DIFERENCA', ascending=False).dropna()
        
        plt.figure(figsize=(12, 10))
        ax_uf = sns.barplot(
            data=media_uf_pivot, x='DIFERENCA', y=media_uf_pivot.index,
            palette='coolwarm_r', orient='h'
        )
        ax_uf.set_title("Diferença de Nota Média (Grupo 'Até 1,3k' vs 'Nenhuma Renda') por Estado", fontsize=14)
        ax_uf.set_xlabel("Diferença de Pontos")
        ax_uf.set_ylabel("Estado")
        ax_uf.axvline(0, color='black', linestyle='--', linewidth=1)
        plt.tight_layout()
        caminho = os.path.join(pasta_resultados, 'diferenca_estados.png')
        plt.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"      💾 Salvo: {caminho}")
    
    elapsed = time.time() - start_time
    print(f"✅ Gráficos gerados em {elapsed:.2f}s\n")


# ==================== 6. FLUXO PRINCIPAL ==================== #

def main():
    """
    Função principal que orquestra todo o fluxo de ETL, análise e geração de saídas.
    """
    # Carregar configurações
    load_dotenv()
    print("🔍 Verificando dependências...")
    driver = verificar_driver_postgresql()
    config = carregar_config()
    
    # Criar pasta de resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta_resultados = f'analise_enem_{timestamp}'
    os.makedirs(pasta_resultados, exist_ok=True)
    
    # Cabeçalho
    print("\n" + "="*80)
    print("🎓 ANÁLISE COMPARATIVA DOS MICRODADOS DO ENEM")
    print("="*80)
    print(f"📁 Pasta de resultados: {pasta_resultados}/")
    print(f"🔌 Driver utilizado: {driver}")
    print(f"🔐 Conectando ao banco de dados (credenciais via .env)...\n")
    
    # Conectar ao banco
    engine = conectar_db(config, driver)
    
    # ETL (carregar dados se necessário)
    verificar_carregar(engine, config)
    
    # Análise
    df_analise = extrair_processar(engine)
    
    # Gerar saídas
    print("📊 Gerando arquivos de saída...")
    gerar_csv_para_pbi(df_analise, pasta_resultados)
    gerar_estatisticas(df_analise, pasta_resultados)
    gerar_graficos(df_analise, pasta_resultados)
    
    # Mensagem final
    print("\n" + "="*80)
    print("🎯 ANÁLISE FINALIZADA COM SUCESSO!")
    print(f"📁 Resultados disponíveis em: {pasta_resultados}/")
    print("="*80)


# ==================== EXECUÇÃO ==================== #

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal no programa: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)