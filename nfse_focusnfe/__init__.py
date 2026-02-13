# -*- coding: utf-8 -*-
"""
Módulo de integração com a API Focus NFSe

Documentação: https://focusnfe.com.br/doc/?python#nfse

Autor: Afonso Carvalho

Exemplo de uso:
    from nfse_focusnfe import FocusNFSeAPI
    
    api = FocusNFSeAPI(api_token="seu_token", homologacao=True)
    status, response = api.send_nfse(referencia, dados_nfse)
"""

from .pyfocusnfse import FocusNFSeAPI

__all__ = ['FocusNFSeAPI']
__version__ = '1.0.0'
__author__ = 'Netcom Treinamentos e Soluções Tecnológicas'

