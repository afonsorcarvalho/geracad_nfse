# -*- coding: utf-8 -*-
"""
Script de teste com DEBUG ativado para ver exatamente o que está sendo enviado

Autor: Afonso Carvalho
"""

from pyfocusnfse import FocusNFSeAPI

# Inicializar a API em modo homologação
# O token já está hardcoded na classe FocusNFSeAPI
focus_api = FocusNFSeAPI(homologacao=True)

# Dados da NFSe - Estrutura EXATAMENTE como no exemplo oficial
# Baseado em: https://focusnfe.com.br/doc/?python#nfse

# Usamos dicionários para armazenar os campos e valores
nfse = {}
nfse["prestador"] = {}
nfse["servico"] = {}
nfse["tomador"] = {}
nfse["tomador"]["endereco"] = {}

# Dados da nota
nfse["data_emissao"] = "2025-10-20T12:00:00-03:00"
nfse["incentivador_cultural"] = "false"
nfse["natureza_operacao"] = "1"
nfse["optante_simples_nacional"] = "true"
nfse["status"] = "1"

# Dados do prestador (sua empresa)
nfse["prestador"]["cnpj"] = "05108721000133"
nfse["prestador"]["inscricao_municipal"] = "48779000"
nfse["prestador"]["codigo_municipio"] = "2111300"

# Dados do serviço
nfse["servico"]["aliquota"] = "5.00"
nfse["servico"]["base_calculo"] = "1.00"
nfse["servico"]["discriminacao"] = "EDUCACAO PROFISSIONAL DE NIVEL TECNICO - ENSINO REGULAR PRE-ESCOLAR, FUNDAMENTAL, MEDIO E SUPERIOR."
nfse["servico"]["iss_retido"] = "false"
nfse["servico"]["item_lista_servico"] = "08.01"
nfse["servico"]["valor_iss"] = "0.05"
nfse["servico"]["valor_liquido"] = "0.95"
nfse["servico"]["valor_servicos"] = "1.00"
nfse["servico"]["codigo_cnae"] = "8541400"

# Dados do tomador (cliente)
nfse["tomador"]["cnpj"] = "79159001372000"
nfse["tomador"]["razao_social"] = "AFONSO FLÁVIO RIBEIRO DE CARVALHO"
nfse["tomador"]["email"] = "afonso@jgma.com.br"
nfse["tomador"]["endereco"]["bairro"] = "Turu"
nfse["tomador"]["endereco"]["cep"] = "65066-190"
nfse["tomador"]["endereco"]["codigo_municipio"] = "2111300"
nfse["tomador"]["endereco"]["logradouro"] = "Rua Boa Esperanca"
nfse["tomador"]["endereco"]["numero"] = "102"
nfse["tomador"]["endereco"]["complemento"] = "sala 01"
nfse["tomador"]["endereco"]["uf"] = "MA"

# Enviar NFSe com DEBUG ATIVADO
print("\n" + "🚀 INICIANDO TESTE COM DEBUG ATIVADO" + "\n")

referencia = "TESTE_DEBUG_001"
status_code, response_json = focus_api.send_nfse(referencia, nfse, debug=True)

# Resultado final
print("\n" + "="*60)
print("✅ RESULTADO FINAL")
print("="*60)
print(f"Status HTTP: {status_code}")

if status_code in [200, 201, 202]:
    print("✅ Sucesso! NFSe enviada.")
elif status_code == 422:
    print("❌ Erro 422: CNPJ não autorizado. Cadastre a empresa no painel web.")
elif status_code == 400:
    print("❌ Erro 400: Dados inválidos. Verifique o JSON enviado.")
elif status_code == 401:
    print("❌ Erro 401: Token inválido.")
else:
    print(f"❌ Erro {status_code}")

print(f"\nDetalhes: {response_json}")
print("="*60)

