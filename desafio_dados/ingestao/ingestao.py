import pandas as pd
import json
import os
from datetime import datetime

def processar_pipeline(config):
    inicio_proc = datetime.now()
    log_rejeitados = []

    # -------------------------------------------------------------------------
    # RF02 & RF03 — LEITURA E VALIDAÇÃO: CATÁLOGO DE CONTEÚDOS (CSV)
    # -------------------------------------------------------------------------
    df_cat = pd.read_csv(config['arquivos']['catalogo_csv'])
    qtd_lidos_cat = len(df_cat)
    
    # Validação baseada em Pandas
    df_cat['status_validacao'] = 'valido'
    df_cat['motivo_rejeicao'] = ''

    # Regra: Campos obrigatórios nulos
    campos_obg_cat = ['conteudo_id', 'titulo', 'tipo', 'categoria', 'nivel', 'carga_horaria_min', 'data_publicacao']
    for campo in campos_obg_cat:
        invalidos = df_cat[df_cat[campo].isna()].index
        if not invalidos.empty:
            df_cat.loc[invalidos, 'status_validacao'] = 'incompleto'
            df_cat.loc[invalidos, 'motivo_rejeicao'] += f'Campo obrigatório {campo} ausente; '

    # Regra: Valores numéricos negativos ou incompatíveis
    negativos_cat = df_cat[df_cat['carga_horaria_min'] < 0].index
    if not negativos_cat.empty:
        df_cat.loc[negativos_cat, 'status_validacao'] = 'invalido'
        df_cat.loc[negativos_cat, 'motivo_rejeicao'] += 'Carga horaria negativa; '

    # Separar os válidos para processamento e registrar rejeitados
    rejeitados_cat = df_cat[df_cat['status_validacao'] != 'valido']
    for _, row in rejeitados_cat.iterrows():
        log_rejeitados.append({'origem': 'catalogo_csv', 'id': str(row['conteudo_id']), 'status': row['status_validacao'], 'motivo': row['motivo_rejeicao']})

    df_cat_validos = df_cat[df_cat['status_validacao'] == 'valido'].copy()
    
    # RF04 - Tratamento e Eliminação de Duplicados
    qtd_duplicados_cat = df_cat_validos.duplicated(subset=['conteudo_id']).sum()
    df_cat_validos = df_cat_validos.drop_duplicates(subset=['conteudo_id'], keep='first')

    # RF04 - Padronização de strings
    df_cat_validos['titulo'] = df_cat_validos['titulo'].str.strip()
    df_cat_validos['categoria'] = df_cat_validos['categoria'].str.strip().str.title()
    df_cat_validos['tipo'] = df_cat_validos['tipo'].str.strip().str.title()
    df_cat_validos['nivel'] = df_cat_validos['nivel'].str.strip().str.title()
    df_cat_validos['data_publicacao'] = pd.to_datetime(df_cat_validos['data_publicacao']).dt.strftime('%Y-%m-%d')

    # -------------------------------------------------------------------------
    # RF02 & RF03 — LEITURA E VALIDAÇÃO: INTERAÇÕES DOS USUÁRIOS (JSON)
    # -------------------------------------------------------------------------
    df_int = pd.read_json(config['arquivos']['interacoes_json'])
    qtd_lidos_int = len(df_int)
    
    df_int['status_validacao'] = 'valido'
    df_int['motivo_rejeicao'] = ''

    # Verificar chaves estrangeiras lógicas com o catálogo tratado
    id_conteudos_validos = set(df_cat_validos['conteudo_id'])
    invalidos_ref = df_int[~df_int['conteudo_id'].isin(id_conteudos_validos)].index
    if not invalidos_ref.empty:
        df_int.loc[invalidos_ref, 'status_validacao'] = 'invalido'
        df_int.loc[invalidos_ref, 'motivo_rejeicao'] += 'Referencia a conteudo_id inexistente ou rejeitado; '

    # AJUSTE: Regra de Negócio para "conclusão" sem avaliação atribuída
    invalidos_conclusao = df_int[(df_int['tipo_interacao'] == 'conclusao') & (df_int['avaliacao_atribuida'].isna())].index
    if not invalidos_conclusao.empty:
        df_int.loc[invalidos_conclusao, 'status_validacao'] = 'invalido'
        df_int.loc[invalidos_conclusao, 'motivo_rejeicao'] += 'Interacao de conclusao nao possui avaliacao atribuida; '

    # AJUSTE: Regra de Negócio para "avaliação" com percentual de conclusão menor que 100%
    invalidos_avaliacao = df_int[(df_int['tipo_interacao'] == 'avaliacao') & (df_int['percentual_conclusao'] < 100.0)].index
    if not invalidos_avaliacao.empty:
        df_int.loc[invalidos_avaliacao, 'status_validacao'] = 'invalido'
        df_int.loc[invalidos_avaliacao, 'motivo_rejeicao'] += 'Usuario avaliou o conteudo sem atingir 100% de conclusao; '

    # Registrar os rejeitados das interações no log
    rejeitados_int = df_int[df_int['status_validacao'] != 'valido']
    for idx, row in rejeitados_int.iterrows():
        log_rejeitados.append({'origem': 'interacoes_json', 'linha_indice': idx, 'status': row['status_validacao'], 'motivo': row['motivo_rejeicao']})

    df_int_validos = df_int[df_int['status_validacao'] == 'valido'].copy()
    qtd_duplicados_int = df_int_validos.duplicated().sum()
    df_int_validos = df_int_validos.drop_duplicates()

    # Padronizações nas Interações
    df_int_validos['tipo_interacao'] = df_int_validos['tipo_interacao'].str.strip().str.lower()
    df_int_validos['data_hora'] = pd.to_datetime(df_int_validos['data_hora']).dt.strftime('%Y-%m-%dT%H:%M:%S')

    # -------------------------------------------------------------------------
    # RF02 & RF03 — LEITURA E VALIDAÇÃO: COMENTÁRIOS E AVALIAÇÕES (JSON)
    # -------------------------------------------------------------------------
    df_com = pd.read_json(config['arquivos']['comentarios_json'])
    qtd_lidos_com = len(df_com)
    
    df_com['status_validacao'] = 'valido'
    df_com['motivo_rejeicao'] = ''

    # Regra: Nota de avaliação fora do intervalo (1 a 5)
    invalidos_nota = df_com[(df_com['avaliacao'] < 1) | (df_com['avaliacao'] > 5)].index
    if not invalidos_nota.empty:
        df_com.loc[invalidos_nota, 'status_validacao'] = 'invalido'
        df_com.loc[invalidos_nota, 'motivo_rejeicao'] += 'Avaliacao fora do intervalo permitido de 1 a 5; '

    rejeitados_com = df_com[df_com['status_validacao'] != 'valido']
    for idx, row in rejeitados_com.iterrows():
        log_rejeitados.append({'origem': 'comentarios_json', 'linha_indice': idx, 'status': row['status_validacao'], 'motivo': row['motivo_rejeicao']})

    df_com_validos = df_com[df_com['status_validacao'] == 'valido'].copy()
    qtd_duplicados_com = df_com_validos.duplicated(subset=['usuario_id', 'conteudo_id', 'data']).sum()
    df_com_validos = df_com_validos.drop_duplicates(subset=['usuario_id', 'conteudo_id', 'data'])

    # -------------------------------------------------------------------------
    # SALVANDO DADOS TRATADOS E GERANDO RELATÓRIO (RF04 & RF05)
    # -------------------------------------------------------------------------
    dir_proc = config['arquivos']['diretorio_processados']
    os.makedirs(dir_proc, exist_ok=True)
    
    df_cat_validos.to_csv(os.path.join(dir_proc, 'catalogo_conteudos_limpo.csv'), index=False)
    df_int_validos.to_json(os.path.join(dir_proc, 'interacoes_usuarios_limpo.json'), orient='records', indent=2)
    df_com_validos.to_json(os.path.join(dir_proc, 'comentarios_avaliacoes_limpo.json'), orient='records', indent=2)

    fim_proc = datetime.now()
    tempo_total = (fim_proc - inicio_proc).total_seconds()

    resumo = {
        "status": "sucesso",
        "quantidade_registros_lidos": qtd_lidos_cat + qtd_lidos_int + qtd_lidos_com,
        "detalhe_fontes": {
            "catalogo_csv": {"lidos": qtd_lidos_cat, "validos": len(df_cat_validos), "duplicados": int(qtd_duplicados_cat), "invalidos": len(df_cat) - len(df_cat_validos) - int(qtd_duplicados_cat)},
            "interacoes_json": {"lidos": qtd_lidos_int, "validos": len(df_int_validos), "duplicados": int(qtd_duplicados_int), "invalidos": len(df_int) - len(df_int_validos) - int(qtd_duplicados_int)},
            "comentarios_json": {"lidos": qtd_lidos_com, "validos": len(df_com_validos), "duplicados": int(qtd_duplicados_com), "invalidos": len(df_com) - len(df_com_validos) - int(qtd_duplicados_com)}
        },
        "tempo_total_processamento_segundos": tempo_total,
        "data_execucao": inicio_proc.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(os.path.join(dir_proc, 'resumo_ingestao.json'), 'w') as f:
        json.dump(resumo, f, indent=2)

    # Log das falhas/rejeitados exigido pelo RF14
    with open(os.path.join(dir_proc, 'registro_execucao_erros.json'), 'w') as f:
        json.dump(log_rejeitados, f, indent=2)

    return resumo
