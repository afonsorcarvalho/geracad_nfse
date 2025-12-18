# -*- coding: utf-8 -*-
"""
Script de pós-migração para associar os códigos CNAE antigos
aos novos registros da tabela geracad_nfse_cnae
"""

import logging
import re

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Associa os códigos CNAE antigos (salvos em nfse_cnae_old)
    aos novos registros da tabela geracad_nfse_cnae
    """
    _logger.info("Iniciando pós-migração do campo nfse_CNAE")
    
    # Verifica se o campo temporário existe
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='geracad_nfse' 
        AND column_name='nfse_cnae_old'
    """)
    
    if not cr.fetchone():
        _logger.info("Campo temporário nfse_cnae_old não encontrado. Pulando pós-migração.")
        return True
    
    # Busca todos os registros com código CNAE antigo
    cr.execute("""
        SELECT id, nfse_cnae_old 
        FROM geracad_nfse 
        WHERE nfse_cnae_old IS NOT NULL 
        AND nfse_cnae_old != ''
        AND nfse_cnae IS NULL
    """)
    
    records = cr.fetchall()
    migrated_count = 0
    not_found_codes = set()
    
    _logger.info(f"Encontrados {len(records)} registros para migrar")
    
    for nfse_id, codigo_antigo in records:
        # Remove caracteres não numéricos
        codigo_limpo = re.sub(r'\D', '', codigo_antigo)
        
        if not codigo_limpo:
            continue
        
        # Tenta encontrar o CNAE correspondente na nova tabela
        cr.execute("""
            SELECT id 
            FROM geracad_nfse_cnae 
            WHERE codigo = %s 
            LIMIT 1
        """, (codigo_limpo,))
        
        result = cr.fetchone()
        
        if result:
            cnae_id = result[0]
            # Atualiza o registro com o novo CNAE
            cr.execute("""
                UPDATE geracad_nfse 
                SET nfse_cnae = %s 
                WHERE id = %s
            """, (cnae_id, nfse_id))
            migrated_count += 1
            _logger.debug(f"NFS-e {nfse_id}: CNAE {codigo_limpo} migrado com sucesso")
        else:
            not_found_codes.add(codigo_limpo)
            _logger.warning(f"NFS-e {nfse_id}: CNAE {codigo_limpo} não encontrado na tabela de CNAEs")
    
    if not_found_codes:
        _logger.warning(
            f"Pós-migração concluída. {migrated_count}/{len(records)} registros migrados. "
            f"CNAEs não encontrados: {', '.join(sorted(not_found_codes))}"
        )
        _logger.warning(
            "AÇÃO NECESSÁRIA: Cadastre os CNAEs faltantes em NFS-e > Configuração > CNAEs "
            "e execute manualmente a migração dos registros pendentes."
        )
    else:
        _logger.info(f"Pós-migração concluída com sucesso! {migrated_count} registros migrados.")
    
    return True

