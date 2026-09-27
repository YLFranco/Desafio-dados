# src/processamento_gold.py
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import os
import hashlib
import json

SALT_KEY = "FicDevIA_Secret_Salt_2026!" #alterar depois

def aplicar_criptografia_salt(usuario_id):
    """RF33 - Garante a proteção dos dados pessoais gerando um hash seguro com Salt"""
    if not usuario_id:
        return "ANONIMO"
    string_combinada = f"{usuario_id}{SALT_KEY}"
    return hashlib.sha256(string_combinada.encode('utf-8')).hexdigest()[:16]

class ProcessarMétricasGold(beam.DoFn):
    """RF25 - Extrai e limpa as linhas vindas do separador de colunas da Silver"""
    def process(self, elemento):
        try:
            # Garante a divisão das colunas baseada no ponto e vírgula do Hop
            campos = elemento.split(';')
            if len(campos) < 7 or campos[0] == 'usuario_id':
                return 
            
            usuario_id = campos[0]
            conteudo_id = campos[1]
            tipo_interacao = campos[2]
            tempo_consumido = float(campos[4])
            
            usuario_criptografado = aplicar_criptografia_salt(usuario_id)
            
            yield (conteudo_id, {
                "usuario_hash": usuario_criptografado,
                "tipo": tipo_interacao,
                "tempo": tempo_consumido
            })
        except Exception:
            pass

def formatar_para_lista_json(lista_dicts):
    """Converte a lista consolidada de métricas em uma única string JSON válida [...]"""
    return json.dumps(lista_dicts, indent=4, ensure_ascii=False)

def executar_pipeline_gold():
    print("[BEAM] Iniciando orquestração da Camada Gold com Apache Beam (DirectRunner)...")
    
    arquivo_silver = "dados/Silver/interacoes_usuarios_silver.txt"
    diretorio_gold = "dados/gold"
    
    # Mudamos o nome base para forçar o VS Code e o sistema operacional a gerarem um arquivo limpo e atualizado
    arquivo_final_base = os.path.join(diretorio_gold, "metricas_finais_gold")
    
    os.makedirs(diretorio_gold, exist_ok=True)
    
    if not os.path.exists(arquivo_silver):
        print(f"[AVISO] Arquivo {arquivo_silver} não encontrado na Camada Silver.")
        return

    options = PipelineOptions()
    with beam.Pipeline(options=options) as pipeline:
        (
            pipeline
            | "1. Ler Camada Silver" >> beam.io.ReadFromText(arquivo_silver)
            | "2. Aplicar LGPD e IA" >> beam.ParDo(ProcessarMétricasGold())
            | "3. Agrupar por Conteúdo" >> beam.GroupByKey()
            | "4. Calcular KPIs da Gold" >> beam.Map(lambda x: {
                "conteudo_id": str(x[0]),
                "total_interacoes": int(len(x[1])),
                "tempo_total_minutos": round(float(sum(item['tempo'] for item in x[1])), 2),
                "usuarios_unicos_impactados": int(len(set(item['usuario_hash'] for item in x[1])))
            })
            | "5. Agrupar em Elemento Único" >> beam.combiners.ToList()
            | "6. Formatar String JSON" >> beam.Map(formatar_para_lista_json)
            | "7. Gravar Arquivo Físico" >> beam.io.WriteToText(
                arquivo_final_base, 
                file_name_suffix=".json",
                shard_name_template=""  # Força o Beam a gerar um arquivo único sem sufixos numéricos de partição
            )
        )
        
    print(f"[BEAM] Sucesso! Arquivo estruturado gerado em: {arquivo_final_base}.json")

if __name__ == "__main__":
    executar_pipeline_gold()
