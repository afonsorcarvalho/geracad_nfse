# -*- coding: utf-8 -*-
"""
Módulo de integração com ISS Digital - São Luís/MA

Sistema de emissão de NFSe da Prefeitura Municipal de São Luís
Baseado nos XSD disponíveis em:
https://www.semfaz.saoluis.ma.gov.br/fckeditor/userfiles/xsd_producao.rar

Exemplo de uso:
    from nfse_issdigital_slz import ISSDigitalSLZ
    
    api = ISSDigitalSLZ(
        inscricao_prestador="48779000",
        cnpj_prestador="05108721000133",
        homologacao=True
    )
    status, response = api.enviar_rps(dados_rps)
"""

from .pyissdigital import ISSDigitalSLZ

__all__ = ['ISSDigitalSLZ']
__version__ = '1.0.0'
__author__ = 'Afonso Carvalho'

