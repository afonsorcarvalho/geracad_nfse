# -*- coding: utf-8 -*-
"""
Script de migração para preservar dados do campo nfse_CNAE
que está mudando de Char para Many2one
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migra o campo nfse_CNAE de Char para Many2one
    preservando os dados existentes
    """
    _logger.info("Iniciando migração do campo nfse_CNAE")
    
    # Verifica se a coluna antiga existe
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='geracad_nfse' 
        AND column_name='nfse_cnae'
    """)
    
    if cr.fetchone():
        _logger.info("Campo nfse_cnae encontrado. Criando campo temporário...")
        
        # Cria campo temporário para armazenar os dados antigos
        cr.execute("""
            ALTER TABLE geracad_nfse 
            ADD COLUMN IF NOT EXISTS nfse_cnae_old VARCHAR;
        """)
        
        # Copia os dados existentes para o campo temporário
        cr.execute("""
            UPDATE geracad_nfse 
            SET nfse_cnae_old = nfse_cnae 
            WHERE nfse_cnae IS NOT NULL AND nfse_cnae != '';
        """)
        
        # Conta quantos registros foram salvos
        cr.execute("""
            SELECT COUNT(*) 
            FROM geracad_nfse 
            WHERE nfse_cnae_old IS NOT NULL
        """)
        count = cr.fetchone()[0]
        
        _logger.info(f"Migração pré-atualização concluída: {count} registros com CNAE preservados no campo temporário")
    else:
        _logger.info("Campo nfse_cnae não encontrado. Pulando migração.")
    
    return True

