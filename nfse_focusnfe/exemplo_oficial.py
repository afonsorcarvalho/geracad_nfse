# -*- coding: utf-8 -*-
"""
Exemplo de envio de NFSe seguindo EXATAMENTE o padrão da documentação oficial do Focus NFSe
Documentação: https://focusnfe.com.br/doc/?python#nfse

Autor: Afonso Carvalho
"""

import json
import requests

# ====== CONFIGURAÇÃO ======

# Para ambiente de produção use:
# url = "https://api.focusnfe.com.br/v2/nfse"
url = "https://homologacao.focusnfe.com.br/v2/nfse"

# Substituir pela sua identificação interna da nota
ref = {"ref": "12345"}

# Token obtido no cadastro da empresa
token = "S0IxodlsyUAF5E2bunyvdHZYdUgbPpgc"

# ====== DADOS DA NOTA ======

# Usamos dicionários para armazenar os campos e valores que em seguida,
# serão convertidos em JSON e enviados para a API

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

# ====== ENVIO DA NOTA ======

print("\n========== ENVIANDO NFSE ==========")
print(f"URL: {url}")
print(f"Referência: {ref}")
print(f"\nDados da nota:")
print(json.dumps(nfse, indent=2, ensure_ascii=False))

# Enviar a requisição conforme documentação oficial
r = requests.post(url, params=ref, data=json.dumps(nfse), auth=(token, ""))

# Mostra na tela o código HTTP da requisição e a mensagem de retorno da API
print("\n========== RESPOSTA DA API ==========")
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}")

# ====== CONSULTAR A NOTA (se foi criada com sucesso) ======

if r.status_code in [200, 201, 202]:
    print("\n========== CONSULTANDO NFSE ==========")
    referencia = ref["ref"]
    url_consulta = f"https://homologacao.focusnfe.com.br/v2/nfse/{referencia}"
    
    r_consulta = requests.get(url_consulta, auth=(token, ""))
    print(f"Status Code: {r_consulta.status_code}")
    print(f"Response: {r_consulta.text}")
    
    # ====== BAIXAR PDF (se a nota foi autorizada) ======
    
    if r_consulta.status_code == 200:
        try:
            dados_nota = r_consulta.json()
            if dados_nota.get("status") == "autorizado":
                print("\n========== BAIXANDO PDF ==========")
                url_pdf = f"https://homologacao.focusnfe.com.br/v2/nfse/{referencia}.pdf"
                r_pdf = requests.get(url_pdf, auth=(token, ""), stream=True)
                
                if r_pdf.status_code == 200:
                    with open(f"nfse_{referencia}.pdf", 'wb') as file:
                        for chunk in r_pdf.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                    print(f"PDF salvo como: nfse_{referencia}.pdf")
                else:
                    print(f"Erro ao baixar PDF: {r_pdf.status_code}")
        except Exception as e:
            print(f"Erro: {e}")

print("\n========== FIM ==========")

