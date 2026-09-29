# src/processamento_gold.py
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import os
import hashlib
import json
import argparse
import time

SALT_KEY = "FicDevIA_Secret_Salt_2026!"

def aplicar_criptografia_salt(usuario_id):
    if not usuario_id:
        return "ANONIMO"
    string_combinada = f"{usuario_id}{SALT_KEY}"
    return hashlib.sha256(string_combinada.encode('utf-8')).hexdigest()[:16]

def formatar_para_lista_json(lista_dicts):
    return json.dumps(lista_dicts, indent=4, ensure_ascii=False)

def executar_pipeline_gold(runner_escolhido="DirectRunner"):
    print(f"\n[BEAM] Iniciando pipeline da Camada Gold com Apache Beam ({runner_escolhido})...")
    
    diretorio_silver_parquet = "dados/silver_parquet"
    diretorio_gold = "dados/gold"
    arquivo_final_base = os.path.join(diretorio_gold, "metricas_finais_gold")
    
    os.makedirs(diretorio_gold, exist_ok=True)
    
    argumentos_pipeline = []
    
    if runner_escolhido == "SparkRunner":
        # Correção Canônica baseada no aviso do SDK do Beam (RF25)
        argumentos_pipeline.extend([
            '--runner=SparkRunner',
            '--spark_master_url=local[*]'  # Aloca dinamicamente todos os cores da CPU simulando o motor Spark local
        ])
    else:
        argumentos_pipeline.extend([
            '--runner=DirectRunner'
        ])

    options = PipelineOptions(argumentos_pipeline)
    inicio_exec = time.time()

    with beam.Pipeline(options=options) as pipeline:
        (
            pipeline
            | "1. Ler Parquet Silver" >> beam.io.ReadFromParquet(os.path.join(diretorio_silver_parquet, "**/*.parquet"))
            | "2. Aplicar LGPD Hash com Salt" >> beam.Map(lambda x: (x['conteudo_id'], {
                "usuario_hash": aplicar_criptografia_salt(x['usuario_id']),
                "tipo": x['tipo_interacao'],
                "tempo": float(x['tempo_consumido'])
            }))
            | "3. Agrupar por Conteúdo" >> beam.GroupByKey()
            | "4. Produzir Regra de Negócio" >> beam.Map(lambda x: {
                "conteudo_id": str(x[0]),
                "total_interacoes": int(len(x[1])),
                "tempo_total_minutos": round(float(sum(item['tempo'] for item in x[1])), 2),
                "usuarios_unicos_impactados": int(len(set(item['usuario_hash'] for item in x[1])))
            })
            | "5. Agrupar em Elemento Único" >> beam.combiners.ToList()
            | "6. Formatar String JSON" >> beam.Map(formatar_para_lista_json)
            | "7. Gravar JSON Analítico Gold" >> beam.io.WriteToText(
                arquivo_final_base, 
                file_name_suffix=".json",
                shard_name_template=""
            )
        )
        
    fim_exec = time.time()
    duracao = fim_exec - inicio_exec
    print(f"✅ [BEAM SUCESSO] Tempo de execução ({runner_escolhido}): {duracao:.4f} segundos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", default="DirectRunner", help="DirectRunner ou SparkRunner")
    args = parser.parse_args()
    executar_pipeline_gold(runner_escolhido=args.runner)
