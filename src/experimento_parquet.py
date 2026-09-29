# src/experimento_parquet.py
import pandas as pd
import os
import time

def executar_experimento_parquet():
    print("\n================ [BENCHMARK] Iniciando Experimento Parquet (RF24) ================")
    
    arquivo_silver_txt = "dados/Silver/interacoes_usuarios_silver.txt"
    diretorio_parquet = "dados/silver_parquet"
    
    if not os.path.exists(arquivo_silver_txt):
        print(f" [ERRO] Arquivo {arquivo_silver_txt} não localizado para o experimento.")
        return

    print(" Carregando dados da camada Silver...")
    
    # Mudança para header=0 (Trata a primeira linha como cabeçalho original do Hop)
    df = pd.read_csv(arquivo_silver_txt, sep=';', header=0, dtype={
        'usuario_id': str,
        'conteudo_id': str,
        'tipo_interacao': str,
        'tempo_consumido': float,
        'percentual_conclusao': float,
        'avaliacao_atribuida': float,
        'origem_dado': str,
        'execucao_id': str
    })
    
    # Criando coluna inteligente para demonstrar a estratégia de particionamento corporativo
    df['categoria_curso'] = df['conteudo_id'].apply(lambda x: 'Engenharia de Dados' if int(x) % 2 == 0 else 'Ciência de Dados')

    # 2. Medição de Escrita em Parquet Particionado (RF24)
    os.makedirs(diretorio_parquet, exist_ok=True)
    
    inicio_parquet_w = time.time()
    # Exporta aplicando particionamento físico por categoria de curso
    df.to_parquet(diretorio_parquet, engine='pyarrow', partition_cols=['categoria_curso'], compression='snappy')
    fim_parquet_w = time.time()
    
    tempo_escrita_parquet = fim_parquet_w - inicio_parquet_w

    # 3. Medição de Leitura (Benchmark)
    inicio_csv_r = time.time()
    _ = pd.read_csv(arquivo_silver_txt, sep=';', header=0)
    fim_csv_r = time.time()
    tempo_leitura_csv = fim_csv_r - inicio_csv_r

    inicio_parquet_r = time.time()
    _ = pd.read_parquet(diretorio_parquet, engine='pyarrow')
    fim_parquet_r = time.time()
    tempo_leitura_parquet = fim_parquet_r - inicio_parquet_r

    # 4. Cálculo de Tamanho em Disco
    tamanho_csv = os.path.getsize(arquivo_silver_txt) / 1024  # KB
    
    tamanho_parquet = 0
    for raiz, _, arquivos in os.walk(diretorio_parquet):
        for f in arquivos:
            if f.endswith('.parquet'):
                tamanho_parquet += os.path.getsize(os.path.join(raiz, f))
    tamanho_parquet = tamanho_parquet / 1024  # KB

    # 5. Exibição dos Resultados do Experimento
    print("\n --- RESULTADOS DO EXPERIMENTO (MÉTRICAS REAIS) ---")
    print(f" Tamanho em Disco - Texto Original (Silver TXT): {tamanho_csv:.2f} KB")
    print(f" Tamanho em Disco - Binário Comprimido (Parquet): {tamanho_parquet:.2f} KB")
    print(f" Redução de Espaço Ocupado: {((tamanho_csv - tamanho_parquet) / tamanho_csv) * 100:.1f}%")
    print(f" Tempo de Leitura - Texto Original (Silver TXT): {tempo_leitura_csv:.4f} segundos")
    print(f" Tempo de Leitura - Parquet: {tempo_leitura_parquet:.4f} segundos")
    print(f" Ganho de Performance na Leitura: {(tempo_leitura_csv / tempo_leitura_parquet):.1f}x mais rápido")
    print("========================================================================\n")

if __name__ == "__main__":
    executar_experimento_parquet()
