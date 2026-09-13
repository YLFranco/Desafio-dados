# src/ingestao.py
import json
import os
from datetime import datetime

import pandas as pd


def processar_pipeline(config):
    inicio_proc = datetime.now()
    log_rejeitados = []

    STATUS_VALIDO = 'valido'

    # -------------------------------------------------------------------------
    # LEITURA E VALIDAÇÃO: CATÁLOGO DE CONTEÚDOS (CSV)
    # -------------------------------------------------------------------------
    df_cat = pd.read_csv(config['arquivos']['catalogo_csv'])
    qtd_lidos_cat = len(df_cat)
    
    # Formatação preventiva de strings para evitar duplicados invisíveis por espaços em branco
    df_cat['titulo'] = df_cat['titulo'].astype(str).str.strip()
    
    # Contabiliza e descarta duplicados na raiz
    qtd_duplicados_cat = df_cat.duplicated(subset=['conteudo_id']).sum()
    df_cat = df_cat.drop_duplicates(subset=['conteudo_id'], keep='first')
    
    df_cat['status_validacao'] = STATUS_VALIDO
    df_cat['motivo_rejeicao'] = ''

    # Validação estrutural de nulos
    campos_obg_cat = ['conteudo_id', 'titulo', 'tipo', 'categoria', 'nivel', 'carga_horaria_min', 'data_publicacao']
    for campo in campos_obg_cat:
        invalidos = df_cat[df_cat[campo].isna()].index
        if not invalidos.empty:
            df_cat.loc[invalidos, 'status_validacao'] = 'incompleto'
            df_cat.loc[invalidos, 'motivo_rejeicao'] += f'Campo obrigatório {campo} ausente; '

    # Validação de regras numéricas
    negativos_cat = df_cat[df_cat['carga_horaria_min'] < 0].index
    if not negativos_cat.empty:
        df_cat.loc[negativos_cat, 'status_validacao'] = 'invalido'
        df_cat.loc[negativos_cat, 'motivo_rejeicao'] += 'Carga horaria negativa; '

    rejeitados_cat = df_cat[df_cat['status_validacao'] != STATUS_VALIDO]
    for _, row in rejeitados_cat.iterrows():
        log_rejeitados.append({
            'origem': 'catalogo_csv', 'id': str(row['conteudo_id']), 
            'status': row['status_validacao'], 'motivo': row['motivo_rejeicao']
        })

    df_cat_validos = df_cat[df_cat['status_validacao'] == STATUS_VALIDO].copy()
    
    # Padronização corporativa final das strings
    df_cat_validos['categoria'] = df_cat_validos['categoria'].str.title()
    df_cat_validos['tipo'] = df_cat_validos['tipo'].str.title()
    df_cat_validos['nivel'] = df_cat_validos['nivel'].str.title()
    df_cat_validos['data_publicacao'] = pd.to_datetime(df_cat_validos['data_publicacao']).dt.strftime('%Y-%m-%d')

    # -------------------------------------------------------------------------
    # LEITURA E VALIDAÇÃO: INTERAÇÕES DOS USUÁRIOS (JSON)
    # -------------------------------------------------------------------------
    df_int = pd.read_json(config['arquivos']['interacoes_json'])
    qtd_lidos_int = len(df_int)
    
    # Normalização de strings de interações antes de checar duplicidade
    df_int['tipo_interacao_limpo'] = df_int['tipo_interacao'].astype(str).str.strip().str.lower()
    
    # Rastreia duplicados com base nos eixos chaves (Mismo usuário, mesmo curso, mesma ação e hora)
    chaves_int = ['usuario_id', 'conteudo_id', 'tipo_interacao_limpo', 'data_hora']
    qtd_duplicados_int = df_int.duplicated(subset=chaves_int).sum()
    df_int = df_int.drop_duplicates(subset=chaves_int, keep='first')
    
    df_int['status_validacao'] = STATUS_VALIDO
    df_int['motivo_rejeicao'] = ''

    # Validação de integridade referencial lógica (Chave Estrangeira com catálogo válido)
    id_conteudos_validos = set(df_cat_validos['conteudo_id'])
    invalidos_ref = df_int[~df_int['conteudo_id'].isin(id_conteudos_validos)].index
    if not invalidos_ref.empty:
        df_int.loc[invalidos_ref, 'status_validacao'] = 'invalido'
        df_int.loc[invalidos_ref, 'motivo_rejeicao'] += 'Referencia a conteudo_id inexistente ou rejeitado; '

    # Regra de Negócio: Conclusão sem Nota atribuída
    invalidos_conclusao = df_int[df_int['tipo_interacao_limpo'].isin(['conclusao', 'conclusão']) & (df_int['avaliacao_atribuida'].isna())].index
    if not invalidos_conclusao.empty:
        df_int.loc[invalidos_conclusao, 'status_validacao'] = 'invalido'
        df_int.loc[invalidos_conclusao, 'motivo_rejeicao'] += 'Interacao de conclusao nao possui avaliacao atribuida; '

    # Regra de Negócio: Avaliação sem ter atingido 100% do material consumido
    invalidos_avaliacao = df_int[df_int['tipo_interacao_limpo'].isin(['avaliacao', 'avaliação']) & (df_int['percentual_conclusao'] < 100.0)].index
    if not invalidos_avaliacao.empty:
        df_int.loc[invalidos_avaliacao, 'status_validacao'] = 'invalido'
        df_int.loc[invalidos_avaliacao, 'motivo_rejeicao'] += 'Usuario avaliou o conteudo sem atingir 100% de conclusao; '

    rejeitados_int = df_int[df_int['status_validacao'] != STATUS_VALIDO]
    for idx, row in rejeitados_int.iterrows():
        log_rejeitados.append({
            'origem': 'interacoes_json', 'linha_indice': idx, 
            'status': row['status_validacao'], 'motivo': row['motivo_rejeicao']
        })

    df_int_validos = df_int[df_int['status_validacao'] == STATUS_VALIDO].copy()
    df_int_validos['tipo_interacao'] = df_int_validos['tipo_interacao_limpo']
    df_int_validos['data_hora'] = pd.to_datetime(df_int_validos['data_hora']).dt.strftime('%Y-%m-%dT%H:%M:%S')
    df_int_validos = df_int_validos.drop(columns=['tipo_interacao_limpo'])

    # -------------------------------------------------------------------------
    # LEITURA E VALIDAÇÃO: COMENTÁRIOS E AVALIAÇÕES (JSON)
    # -------------------------------------------------------------------------
    df_com = pd.read_json(config['arquivos']['comentarios_json'])
    qtd_lidos_com = len(df_com)
    
    # Rastreia duplicados estruturais de comentários
    chaves_com = ['usuario_id', 'conteudo_id', 'data']
    qtd_duplicados_com = df_com.duplicated(subset=chaves_com).sum()
    df_com = df_com.drop_duplicates(subset=chaves_com, keep='first')
    
    df_com['status_validacao'] = STATUS_VALIDO
    df_com['motivo_rejeicao'] = ''

    # Regra de Negócio: Notas fora do limite de escala de 1 a 5 estrelas
    invalidos_nota = df_com[(df_com['avaliacao'] < 1) | (df_com['avaliacao'] > 5)].index
    if not invalidos_nota.empty:
        df_com.loc[invalidos_nota, 'status_validacao'] = 'invalido'
        df_com.loc[invalidos_nota, 'motivo_rejeicao'] += 'Avaliacao fora do intervalo permitido de 1 a 5; '

    rejeitados_com = df_com[df_com['status_validacao'] != STATUS_VALIDO]
    for idx, row in rejeitados_com.iterrows():
        log_rejeitados.append({
            'origem': 'comentarios_json', 'linha_indice': idx, 
            'status': row['status_validacao'], 'motivo': row['motivo_rejeicao']
        })

    df_com_validos = df_com[df_com['status_validacao'] == STATUS_VALIDO].copy()


    # EXPEDIÇÃO DE ARQUIVOS SANITIZADOS E RELATÓRIO OPERACIONAL
    dir_proc = config['arquivos']['diretorio_processados']
    os.makedirs(dir_proc, exist_ok=True)
    
    df_cat_validos.to_csv(os.path.join(dir_proc, 'catalogo_conteudos_limpo.csv'), index=False)
    df_int_validos.to_json(os.path.join(dir_proc, 'interacoes_usuarios_limpo.json'), orient='records', indent=2)
    df_com_validos.to_json(os.path.join(dir_proc, 'comentarios_avaliacoes_limpo.json'), orient='records', indent=2)

    fim_proc = datetime.now()
    tempo_total = (fim_proc - inicio_proc).total_seconds()

    resumo = {
        "status": "sucesso",
        "quantidade_registros_lidos": int(qtd_lidos_cat + qtd_lidos_int + qtd_lidos_com),
        "detalhe_fontes": {
            "catalogo_csv": {
                "lidos": int(qtd_lidos_cat), "validos": int(len(df_cat_validos)), 
                "duplicados": int(qtd_duplicados_cat), 
                "invalidos": int(qtd_lidos_cat - len(df_cat_validos) - int(qtd_duplicados_cat))
            },
            "interacoes_json": {
                "lidos": int(qtd_lidos_int), "validos": int(len(df_int_validos)), 
                "duplicados": int(qtd_duplicados_int), 
                "invalidos": int(qtd_lidos_int - len(df_int_validos) - int(qtd_duplicados_int))
            },
            "comentarios_json": {
                "lidos": int(qtd_lidos_com), "validos": int(len(df_com_validos)), 
                "duplicados": int(qtd_duplicados_com), 
                "invalidos": int(qtd_lidos_com - len(df_com_validos) - int(qtd_duplicados_com))
            }
        },
        "tempo_total_processamento_segundos": float(tempo_total),
        "data_execucao": inicio_proc.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(os.path.join(dir_proc, 'resumo_ingestao.json'), 'w') as f:
        json.dump(resumo, f, indent=2)

    with open(os.path.join(dir_proc, 'registro_execucao_erros.json'), 'w') as f:
        json.dump(log_rejeitados, f, indent=2)

    return resumo
