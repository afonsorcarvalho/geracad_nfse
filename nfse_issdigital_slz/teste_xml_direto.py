# -*- coding: utf-8 -*-
"""
Script de teste para enviar XML direto do arquivo XML_ENVIO CERTO (3).xml
Este teste lê o XML do arquivo e envia diretamente para o webservice

Autor: Afonso Carvalho
"""

from pyissdigital import ISSDigitalSLZ
import os
import requests
import re
from datetime import datetime

print("="*70)
print("🧪 TESTE - ENVIO DE XML DIRETO DO ARQUIVO (COM PREENCHIMENTO)")
print("="*70)
print("\n⚠️  NOTA: Este teste preenche os campos vazios do XML antes de enviar")
print("   'XML_ENVIO CERTO (3).xml'\n")

# Configuração básica (necessária para inicializar a API)
inscricao_municipal = "48779000"
cnpj_prestador = "05108721000133"
razao_social = "NETCOM SOLUCOES EM INFORMATICA LTDA"

# Dados do tomador (para preencher campos vazios)
cnpj_tomador = "79159001372000"
razao_social_tomador = "AFONSO FLAVIO RIBEIRO DE CARVALHO"
tipo_logradouro_tomador = "Rua"
logradouro_tomador = "Boa Esperanca"
numero_endereco_tomador = "102"
tipo_bairro_tomador = "Bairro"
bairro_tomador = "Turu"
cep_tomador = "65066190"
codigo_atividade = "854140000"
codigo_servico = "0801"
discriminacao_servico = "EDUCACAO PROFISSIONAL DE NIVEL TECNICO - ENSINO REGULAR PRE-ESCOLAR, FUNDAMENTAL, MEDIO E SUPERIOR."
telefone_prestador = "81599692"

# Inicializar API (apenas para obter URLs e headers)
api = ISSDigitalSLZ(
    inscricao_prestador=inscricao_municipal,
    cnpj_prestador=cnpj_prestador,
    razao_social_prestador=razao_social,
    certificado_pfx=None,  # Não precisa de certificado para este teste
    senha_certificado=None,
    token_envio=None,
    homologacao=False,  # PRODUÇÃO
    codigo_cidade="0921"
)

# Caminho do arquivo XML
arquivo_xml = "XML_ENVIO CERTO (3).xml"

if not os.path.exists(arquivo_xml):
    print(f"❌ ERRO: Arquivo não encontrado: {arquivo_xml}")
    print(f"   Certifique-se de que o arquivo está no mesmo diretório deste script")
    exit(1)

# Função para atualizar namespaces para URLs do semfaz
def atualizar_namespaces_xml(xml_content):
    """Atualiza os namespaces do XML para usar URLs do sistema semfaz"""
    xml_atualizado = xml_content
    
    # Atualizar namespace ns1
    # Se existir prefixo ns1, converte para namespace padrão
    xml_atualizado = re.sub(
        r'<ns1:ReqEnvioLoteRPS',
        '<ReqEnvioLoteRPS',
        xml_atualizado
    )
    xml_atualizado = re.sub(
        r'</ns1:ReqEnvioLoteRPS>',
        '</ReqEnvioLoteRPS>',
        xml_atualizado
    )
    xml_atualizado = re.sub(
        r'xmlns:ns1="http://localhost:8080/WsNFe2/lote"',
        'xmlns="http://sistemas.semfaz.saoluis.ma.gov.br/WsNFe2/lote"',
        xml_atualizado
    )
    xml_atualizado = re.sub(
        r'xmlns:ns1="http://sistemas.semfaz.saoluis.ma.gov.br/WsNFe2/lote"',
        'xmlns="http://sistemas.semfaz.saoluis.ma.gov.br/WsNFe2/lote"',
        xml_atualizado
    )
    xml_atualizado = re.sub(
        r' xmlns:ns1="[^"]*"',
        '',
        xml_atualizado
    )
    
    # Atualizar namespace tipos
    xml_atualizado = re.sub(
        r'xmlns:tipos="http://localhost:8080/WsNFe2/tp"',
        'xmlns:tipos="http://sistemas.semfaz.saoluis.ma.gov.br/WsNFe2/tp"',
        xml_atualizado
    )
    
    # Atualizar schemaLocation
    xml_atualizado = re.sub(
        r'xsi:schemaLocation="http://localhost:8080/WsNFe2/lote http://localhost:8080/WsNFe2/xsd/ReqEnvioLoteRPS.xsd"',
        'xsi:schemaLocation="http://sistemas.semfaz.saoluis.ma.gov.br/WsNFe2/lote http://sistemas.semfaz.saoluis.ma.gov.br/WsNFe2/xsd/ReqEnvioLoteRPS.xsd"',
        xml_atualizado
    )
    
    return xml_atualizado

# Função para preencher campos vazios do XML
def preencher_campos_xml(xml_content, api_instance):
    """Preenche campos vazios do XML com dados do prestador e tomador"""
    xml_preenchido = xml_content
    
    # Preencher campos do cabeçalho
    xml_preenchido = re.sub(r'<CPFCNPJRemetente></CPFCNPJRemetente>', 
                           f'<CPFCNPJRemetente>{api_instance.cnpj_prestador}</CPFCNPJRemetente>', xml_preenchido)
    xml_preenchido = re.sub(r'<CPFCNPJRemetente/>', 
                           f'<CPFCNPJRemetente>{api_instance.cnpj_prestador}</CPFCNPJRemetente>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<RazaoSocialRemetente></RazaoSocialRemetente>', 
                           f'<RazaoSocialRemetente>{api_instance.razao_social_prestador}</RazaoSocialRemetente>', xml_preenchido)
    xml_preenchido = re.sub(r'<RazaoSocialRemetente/>', 
                           f'<RazaoSocialRemetente>{api_instance.razao_social_prestador}</RazaoSocialRemetente>', xml_preenchido)
    
    # Preencher campos do prestador no RPS
    xml_preenchido = re.sub(r'<InscricaoMunicipalPrestador></InscricaoMunicipalPrestador>', 
                           f'<InscricaoMunicipalPrestador>{api_instance.inscricao_prestador}</InscricaoMunicipalPrestador>', xml_preenchido)
    xml_preenchido = re.sub(r'<InscricaoMunicipalPrestador/>', 
                           f'<InscricaoMunicipalPrestador>{api_instance.inscricao_prestador}</InscricaoMunicipalPrestador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<RazaoSocialPrestador></RazaoSocialPrestador>', 
                           f'<RazaoSocialPrestador>{api_instance.razao_social_prestador}</RazaoSocialPrestador>', xml_preenchido)
    xml_preenchido = re.sub(r'<RazaoSocialPrestador/>', 
                           f'<RazaoSocialPrestador>{api_instance.razao_social_prestador}</RazaoSocialPrestador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<TelefonePrestador></TelefonePrestador>', 
                           f'<TelefonePrestador>{telefone_prestador}</TelefonePrestador>', xml_preenchido)
    xml_preenchido = re.sub(r'<TelefonePrestador/>', 
                           f'<TelefonePrestador>{telefone_prestador}</TelefonePrestador>', xml_preenchido)
    
    # Preencher campos do tomador
    xml_preenchido = re.sub(r'<CPFCNPJTomador></CPFCNPJTomador>', 
                           f'<CPFCNPJTomador>{cnpj_tomador}</CPFCNPJTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<CPFCNPJTomador/>', 
                           f'<CPFCNPJTomador>{cnpj_tomador}</CPFCNPJTomador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<RazaoSocialTomador></RazaoSocialTomador>', 
                           f'<RazaoSocialTomador>{razao_social_tomador}</RazaoSocialTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<RazaoSocialTomador/>', 
                           f'<RazaoSocialTomador>{razao_social_tomador}</RazaoSocialTomador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<TipoLogradouroTomador></TipoLogradouroTomador>', 
                           f'<TipoLogradouroTomador>{tipo_logradouro_tomador}</TipoLogradouroTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<TipoLogradouroTomador/>', 
                           f'<TipoLogradouroTomador>{tipo_logradouro_tomador}</TipoLogradouroTomador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<LogradouroTomador></LogradouroTomador>', 
                           f'<LogradouroTomador>{logradouro_tomador}</LogradouroTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<LogradouroTomador/>', 
                           f'<LogradouroTomador>{logradouro_tomador}</LogradouroTomador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<NumeroEnderecoTomador></NumeroEnderecoTomador>', 
                           f'<NumeroEnderecoTomador>{numero_endereco_tomador}</NumeroEnderecoTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<NumeroEnderecoTomador/>', 
                           f'<NumeroEnderecoTomador>{numero_endereco_tomador}</NumeroEnderecoTomador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<TipoBairroTomador></TipoBairroTomador>', 
                           f'<TipoBairroTomador>{tipo_bairro_tomador}</TipoBairroTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<TipoBairroTomador/>', 
                           f'<TipoBairroTomador>{tipo_bairro_tomador}</TipoBairroTomador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<BairroTomador></BairroTomador>', 
                           f'<BairroTomador>{bairro_tomador}</BairroTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<BairroTomador/>', 
                           f'<BairroTomador>{bairro_tomador}</BairroTomador>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<CEPTomador></CEPTomador>', 
                           f'<CEPTomador>{cep_tomador}</CEPTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<CEPTomador/>', 
                           f'<CEPTomador>{cep_tomador}</CEPTomador>', xml_preenchido)
    
    # Preencher campos de atividade e serviço
    xml_preenchido = re.sub(r'<CodigoAtividade></CodigoAtividade>', 
                           f'<CodigoAtividade>{codigo_atividade}</CodigoAtividade>', xml_preenchido)
    xml_preenchido = re.sub(r'<CodigoAtividade/>', 
                           f'<CodigoAtividade>{codigo_atividade}</CodigoAtividade>', xml_preenchido)
    
    xml_preenchido = re.sub(r'<CodigoServico></CodigoServico>', 
                           f'<CodigoServico>{codigo_servico}</CodigoServico>', xml_preenchido)
    xml_preenchido = re.sub(r'<CodigoServico/>', 
                           f'<CodigoServico>{codigo_servico}</CodigoServico>', xml_preenchido)
    
    # Preencher discriminação do serviço no item
    xml_preenchido = re.sub(r'<DiscriminacaoServico></DiscriminacaoServico>', 
                           f'<DiscriminacaoServico>{discriminacao_servico}</DiscriminacaoServico>', xml_preenchido)
    xml_preenchido = re.sub(r'<DiscriminacaoServico/>', 
                           f'<DiscriminacaoServico>{discriminacao_servico}</DiscriminacaoServico>', xml_preenchido)
    
    # Preencher campos opcionais que podem estar vazios (deixar vazios se necessário)
    # EmailTomador - deixar vazio ou preencher com "-" conforme manual
    xml_preenchido = re.sub(r'<EmailTomador/>', '<EmailTomador>-</EmailTomador>', xml_preenchido)
    xml_preenchido = re.sub(r'<EmailTomador></EmailTomador>', '<EmailTomador>-</EmailTomador>', xml_preenchido)
    
    # InscricaoMunicipalTomador - deixar como está (pode ser vazio)
    # Assinatura - deixar vazio (teste sem assinatura)
    xml_preenchido = re.sub(r'<Assinatura></Assinatura>', '<Assinatura/>', xml_preenchido)
    
    # Corrigir data (remover zero extra e atualizar para data atual)
    data_atual = datetime.now().strftime("%Y-%m-%d")
    xml_preenchido = re.sub(r'<dtInicio>2024-07-010</dtInicio>', 
                           f'<dtInicio>{data_atual}</dtInicio>', xml_preenchido)
    xml_preenchido = re.sub(r'<dtFim>2024-07-10</dtFim>', 
                           f'<dtFim>{data_atual}</dtFim>', xml_preenchido)
    
    # Atualizar DataEmissaoRPS para data/hora atual
    data_hora_atual = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    xml_preenchido = re.sub(r'<DataEmissaoRPS>2024-07-10T00:00:00</DataEmissaoRPS>', 
                           f'<DataEmissaoRPS>{data_hora_atual}</DataEmissaoRPS>', xml_preenchido)
    
    # Gerar número único para o RPS baseado em timestamp
    numero_rps_unico = datetime.now().strftime("%Y%m%d%H%M%S")
    xml_preenchido = re.sub(r'<NumeroRPS>1</NumeroRPS>', 
                           f'<NumeroRPS>{numero_rps_unico}</NumeroRPS>', xml_preenchido)
    
    # Atualizar ID do RPS e do Lote para serem únicos
    xml_preenchido = re.sub(r'<RPS Id="rps1">', 
                           f'<RPS Id="rps{numero_rps_unico}">', xml_preenchido)
    xml_preenchido = re.sub(r'<Lote Id="lote1">', 
                           f'<Lote Id="lote{numero_rps_unico}">', xml_preenchido)
    
    return xml_preenchido

# Ler o XML do arquivo
print(f"📖 Lendo arquivo XML: {arquivo_xml}")
with open(arquivo_xml, 'r', encoding='utf-8') as f:
    xml_conteudo = f.read()

print(f"✅ XML lido com sucesso!")
print(f"   Tamanho original: {len(xml_conteudo)} caracteres")

# Atualizar namespaces para URLs do semfaz
print(f"\n🌐 Atualizando namespaces para URLs do sistema semfaz...")
xml_conteudo = atualizar_namespaces_xml(xml_conteudo)
print(f"✅ Namespaces atualizados!")

# Preencher campos vazios
print(f"\n🔧 Preenchendo campos vazios do XML...")
xml_conteudo = preencher_campos_xml(xml_conteudo, api)
print(f"✅ Campos preenchidos!")
print(f"   Tamanho após preenchimento: {len(xml_conteudo)} caracteres")

print(f"\n📄 Conteúdo do XML (primeiros 800 caracteres):")
print("-" * 70)
print(xml_conteudo[:800])
print("..." if len(xml_conteudo) > 800 else "")
print("-" * 70)

# Criar envelope SOAP com o XML lido
print(f"\n📦 Criando envelope SOAP...")
soap_envelope = api._criar_envelope_soap(xml_conteudo, "enviar")
print(f"✅ Envelope SOAP criado!")
print(f"   Tamanho total: {len(soap_envelope)} caracteres")

# Exibir informações do envio
print("\n" + "="*70)
print("🚀 ENVIANDO XML PARA ISS DIGITAL SÃO LUÍS")
print("="*70)
print(f"📍 URL: {api.base_url}")
print(f"📋 Arquivo XML: {arquivo_xml}")
print(f"\n📤 SOAP Envelope (primeiros 1000 caracteres):")
print("-" * 70)
print(soap_envelope[:1000] + ("..." if len(soap_envelope) > 1000 else ""))
print("-" * 70)

# Enviar requisição
try:
    print(f"\n⏳ Enviando requisição ao webservice...")
    headers = api.headers.copy()
    
    response = requests.post(
        api.base_url,
        data=soap_envelope.encode('utf-8'),
        headers=headers,
        timeout=60
    )
    
    print(f"✅ Resposta recebida!")
    print(f"   Status HTTP: {response.status_code}")
    
    print("\n" + "="*70)
    print("📥 RESPOSTA DO WEBSERVICE")
    print("="*70)
    print(f"Status HTTP: {response.status_code}")
    print(f"\n📝 XML de Resposta:")
    print(response.text)
    print("="*70)
    
    # Tentar fazer parse da resposta
    try:
        response_dict = api._parse_response_envio(response.text)
        print(f"\n📊 Resposta Parseada:")
        print(f"   Sucesso: {response_dict.get('sucesso', 'N/A')}")
        if 'numero_lote' in response_dict:
            print(f"   Número do Lote: {response_dict.get('numero_lote')}")
        if 'erros' in response_dict:
            print(f"   Erros: {response_dict['erros']}")
        if 'notas' in response_dict:
            print(f"   Notas: {len(response_dict['notas'])} nota(s) gerada(s)")
    except Exception as e:
        print(f"\n⚠️  Não foi possível fazer parse da resposta: {e}")
    
    # Verificar se foi bem-sucedido
    if response.status_code == 200:
        if 'sucesso' in response.text.lower() or 'numero_lote' in response.text.lower():
            print(f"\n✅ XML enviado com sucesso!")
        elif 'erro' in response.text.lower():
            print(f"\n❌ Erro detectado na resposta")
        else:
            print(f"\n⚠️  Resposta recebida, mas status não claro")
    else:
        print(f"\n❌ Erro HTTP: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ ERRO ao enviar XML!")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    import traceback
    print(f"\n📋 Traceback completo:")
    traceback.print_exc()

print("\n" + "="*70)
print("🏁 TESTE CONCLUÍDO")
print("="*70)

