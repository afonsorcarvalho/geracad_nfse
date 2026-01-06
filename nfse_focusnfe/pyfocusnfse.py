# -*- coding: utf-8 -*-
"""
Integração com Focus NFe API
API REST para emissão de NFSe, NFe, NFCe, CTe e MDFe

Documentação: https://focusnfe.com.br/doc/?python#nfse

Autor: Afonso Carvalho
"""

import requests
import json
import re
from requests.auth import HTTPBasicAuth
import base64

class FocusNFSeAPI:
    """
    Classe para integração com a API do Focus NFSe Nacional.
    Documentação: https://focusnfe.com.br/doc/#nfse-nacional
    Endpoint: /v2/nfsen (NFSe Nacional)
    """
    
    def __init__(self,  homologacao=True):
        """
        Inicializa a API do Focus NFSe.
        
        Args:
            api_token (str): Token de acesso da API
            homologacao (bool): True para ambiente de homologação, False para produção
        """
        # URLs conforme documentação oficial
        if homologacao:
            self.api_token = "S0IxodlsyUAF5E2bunyvdHZYdUgbPpgc"
            self.base_url = "https://homologacao.focusnfe.com.br"
        else:
            self.api_token = "xhXaKQsnkxdOHVmxDMhgMlTqJxCpQLgr"
            self.base_url = "https://api.focusnfe.com.br"
    
    def send_nfse(self, referencia, data, debug=False):
        """
        Envia uma NFSe Nacional para autorização.
        Segue o padrão da documentação oficial: https://focusnfe.com.br/doc/#nfse-nacional
        Endpoint: /v2/nfsen (NFSe Nacional)
        
        Args:
            referencia (str): Identificador único da nota (controlado pela aplicação)
            data (dict): Dados da NFSe no formato da API Focus NFSe Nacional (campos na raiz)
            debug (bool): Se True, exibe informações detalhadas da requisição
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/nfsen"
        params = {"ref": referencia}
        
        # DEBUG: Mostra o que está sendo enviado
        if debug:
            print("\n" + "="*60)
            print("🔍 DEBUG - ENVIANDO NFSE")
            print("="*60)
            print(f"📍 URL: {url}")
            print(f"📋 Parâmetros: {params}")
            print(f"🔑 Token: {self.api_token[:10]}...{self.api_token[-5:]}")
            print(f"🔐 Auth: ('{self.api_token[:10]}...', '')")
            print(f"\n📦 Dados JSON sendo enviados:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("="*60 + "\n")
        
        # Conforme documentação oficial: usa data=json.dumps() e auth como tupla
        response = requests.post(
            url, 
            params=params, 
            data=json.dumps(data),  # ✅ Converte dict para JSON string
            auth=(self.api_token, "")
        )
        
        # DEBUG: Mostra a resposta
        if debug:
            print("\n" + "="*60)
            print("📥 RESPOSTA DA API")
            print("="*60)
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Headers da Resposta:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")
            print(f"\n📝 Corpo da Resposta:")
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2, ensure_ascii=False))
            except:
                print(response.text)
            print("="*60 + "\n")
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def get_nfse(self, referencia):
        """
        Consulta uma NFSe Nacional pela referência.
        Endpoint: /v2/nfsen (NFSe Nacional)
        
        Args:
            referencia (str): Identificador único da nota usado no envio
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/nfsen/{referencia}"
        response = requests.get(url, auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def cancel_nfse(self, referencia, justificativa):
        """
        Cancela uma NFSe Nacional.
        Endpoint: /v2/nfsen (NFSe Nacional)
        
        Args:
            referencia (str): Identificador único da nota usado no envio
            justificativa (str): Justificativa do cancelamento
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/nfsen/{referencia}"
        data = {"justificativa": justificativa}
        response = requests.delete(url, data=json.dumps(data), auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def get_pdf_nfse(self, referencia, caminho_arquivo="nfse_baixada.pdf"):
        """
        Baixa o PDF de uma NFSe Nacional autorizada.
        Endpoint: /v2/nfsen (NFSe Nacional)
        
        Args:
            referencia (str): Identificador único da nota usado no envio
            caminho_arquivo (str): Caminho onde o PDF será salvo
            
        Returns:
            tuple: (status_code, response)
        """
        url = f"{self.base_url}/v2/nfsen/{referencia}.pdf"
        response = requests.get(url, auth=(self.api_token, ""), stream=True)
        
        if response.status_code == 200:
            # Salvar o arquivo PDF localmente
            with open(caminho_arquivo, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            
            print(f"Arquivo PDF baixado com sucesso em: {caminho_arquivo}")
        
        return response.status_code, response
    
    def resend_email(self, referencia, emails):
        """
        Reenvia o email de uma NFSe Nacional autorizada.
        Endpoint: /v2/nfsen (NFSe Nacional)
        
        Args:
            referencia (str): Identificador único da nota usado no envio
            emails (list): Lista de emails para reenvio
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/nfsen/{referencia}/email"
        data = {"emails": emails}
        response = requests.post(url, data=json.dumps(data), auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    # === Métodos de Gerenciamento de Empresas ===
    
    def create_empresa(self, data_empresa):
        """
        Cria/cadastra uma nova empresa no Focus NFSe.
        
        Args:
            data_empresa (dict): Dados da empresa conforme documentação (deve incluir o CNPJ)
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/empresas"
        response = requests.post(url, data=json.dumps(data_empresa), auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def get_empresa(self, cnpj):
        """
        Consulta uma empresa cadastrada.
        
        Args:
            cnpj (str): CNPJ da empresa (somente números)
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/empresas/{cnpj}"
        response = requests.get(url, auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def update_empresa(self, cnpj, data_empresa):
        """
        Atualiza os dados de uma empresa cadastrada.
        
        Args:
            cnpj (str): CNPJ da empresa (somente números)
            data_empresa (dict): Dados da empresa a serem atualizados
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/empresas/{cnpj}"
        response = requests.put(url, data=json.dumps(data_empresa), auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def delete_empresa(self, cnpj):
        """
        Exclui uma empresa cadastrada.
        
        Args:
            cnpj (str): CNPJ da empresa (somente números)
            
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/empresas/{cnpj}"
        response = requests.delete(url, auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def list_empresas(self):
        """
        Lista todas as empresas cadastradas.
        
        Returns:
            tuple: (status_code, response_json)
        """
        url = f"{self.base_url}/v2/empresas"
        response = requests.get(url, auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}
    
    def consultar_cep(self, cep):
        """
        Consulta endereço através do CEP usando a API da FocusNFE.
        Documentação: https://doc.focusnfe.com.br/reference/consultarceps
        
        Args:
            cep (str): CEP a ser consultado (com ou sem formatação)
            
        Returns:
            tuple: (status_code, response_json)
        """
        # Remove formatação do CEP (mantém apenas números)
        cep_limpo = re.sub(r'[^0-9]', '', str(cep))
        
        if len(cep_limpo) != 8:
            return 400, {"erro": "CEP deve conter 8 dígitos"}
        
        url = f"{self.base_url}/v2/ceps/{cep_limpo}"
        response = requests.get(url, auth=(self.api_token, ""))
        
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {"erro": response.text}


# Exemplo de uso da classe
if __name__ == "__main__":
    # Token de API - substitua pelo seu token real
    api_token = "S0IxodlsyUAF5E2bunyvdHZYdUgbPpgc"
    
    # Inicializar a API em modo homologação
    focus_api = FocusNFSeAPI( homologacao=False)
    
    # Dados de exemplo para envio de NFSe
    # Estrutura EXATAMENTE como no exemplo oficial da documentação Focus NFSe
    # Baseado em: https://focusnfe.com.br/doc/?python#nfse
    
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
    nfse["servico"]["codigo_atividade"] = "854140000"
    nfse["servico"]["codigo_cnae"] = "854140000"
    nfse["servico"]["codigo_tributario_municipio"] = "854140000"
   
    
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
    
    # ===== PASSO 1: CADASTRAR A EMPRESA PRIMEIRO =====
    # Antes de emitir notas, você precisa cadastrar a empresa na API Focus NFSe
    
    # NOTA: Os endpoints de empresas podem não estar disponíveis no ambiente de homologação
    # ou podem estar em uma URL diferente. Verifique a documentação ou use produção.
    
    # Exemplo A: Listar empresas já cadastradas
    # print("\n=== Listando empresas cadastradas ===")
    # status_code, response_json = focus_api.list_empresas()
    # print(f"Status Code: {status_code}")
    # print(f"Empresas: {response_json}")
    
    # Se receber erro 404, os endpoints de empresa podem não estar disponíveis em homologação
    # if status_code == 404:
    #     print("\n⚠️  ATENÇÃO: Endpoint de empresas não encontrado!")
    #     print("Possíveis soluções:")
    #     print("1. O cadastro de empresas pode ser feito apenas pelo painel web em homologação")
    #     print("2. Tente usar o ambiente de produção (homologacao=False)")
    #     print("3. Acesse: https://homologacao.focusnfe.com.br para cadastrar via web")
    #     print("4. O certificado digital da empresa deve ser enviado via painel web")
    
    # Exemplo B: Consultar uma empresa específica
    # cnpj_empresa = "05108721000133"
    # print(f"\n=== Consultando empresa {cnpj_empresa} ===")
    # status_code, response_json = focus_api.get_empresa(cnpj_empresa)
    # print(f"Status Code: {status_code}")
    # print(f"Empresa: {response_json}")
    
    # Exemplo C: Cadastrar uma nova empresa (necessário antes de emitir notas)
    # IMPORTANTE: Pode ser necessário cadastrar via painel web em homologação
    # data_cadastro_empresa = {
    #     "nome": "NETCOM TREINAMENTOS E SOLUCOES TECNOLOGICAS LTDA",
    #     "nome_fantasia": "NETCOM",
    #     "email": "financeiro@netcom-ma.com.br",
    #     "cnpj": "05108721000133",
    #     "inscricao_municipal": "48779000",
    #     "inscricao_estadual": "",
    #     "regime_tributario": "3",  # 1=Simples Nacional, 2=Simples Nacional Excesso, 3=Regime Normal
    #     "cep": "65066190",
    #     "logradouro": "Rua Boa Esperanca",
    #     "numero": "102",
    #     "complemento": "Sala 01",
    #     "bairro": "Turu",
    #     "codigo_municipio": "2111300",  # Código IBGE de São Luís/MA
    #     "municipio": "São Luis",
    #     "uf": "MA",
    #     "telefone": "9898159969",
    #     "habilita_nfse": True,  # Habilitar emissão de NFSe
    # }
    # 
    # print(f"\n=== Cadastrando empresa ===")
    # status_code, response_json = focus_api.create_empresa(data_cadastro_empresa)
    # print(f"Status Code: {status_code}")
    # print(f"Response: {response_json}")
    
    # ===== PASSO 2: EMITIR A NFSe =====
    # Só emita a nota depois de cadastrar a empresa
    
    # Exemplo 1: Enviar NFSe com DEBUG ATIVADO
    referencia = "NFSE_TESTE_007"
    status_code, response_json = focus_api.send_nfse(referencia, nfse, debug=True)
    print(f"\n=== Envio de NFSe ===")
    print(f"Status Code: {status_code}")
    print(f"Response: {response_json}")
    
    # Exemplo 2: Consultar NFSe
    # referencia = "NFSE_TESTE_001"
    # status_code, response_json = focus_api.get_nfse(referencia)
    # print(f"\n=== Consulta NFSe ===")
    # print(f"Status Code: {status_code}")
    # print(f"Response: {response_json}")
    
    # Exemplo 3: Baixar PDF da NFSe
    # referencia = "NFSE_TESTE_001"
    # status_code, response = focus_api.get_pdf_nfse(referencia, "nfse_teste.pdf")
    # print(f"\n=== Download PDF ===")
    # print(f"Status Code: {status_code}")
    
    # Exemplo 4: Cancelar NFSe
    # referencia = "NFSE_TESTE_001"
    # justificativa = "Nota emitida incorretamente"
    # status_code, response_json = focus_api.cancel_nfse(referencia, justificativa)
    # print(f"\n=== Cancelamento ===")
    # print(f"Status Code: {status_code}")
    # print(f"Response: {response_json}")
    
    # Exemplo 5: Reenviar email
    # referencia = "NFSE_TESTE_001"
    # emails = ["afonso@jgma.com.br"]
    # status_code, response_json = focus_api.resend_email(referencia, emails)
    # print(f"\n=== Reenvio Email ===")
    # print(f"Status Code: {status_code}")
    # print(f"Response: {response_json}")

