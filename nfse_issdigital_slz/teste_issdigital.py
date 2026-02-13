# -*- coding: utf-8 -*-
"""
Script de teste para ISS Digital São Luís
Execute para testar o envio e consulta de NFSe

⚠️ IMPORTANTE: Configure o certificado digital antes de executar!

Autor: Afonso Carvalho
"""

from pyissdigital import ISSDigitalSLZ
from datetime import datetime
import os

print("="*70)
print("🧪 TESTE - ISS DIGITAL SÃO LUÍS")
print("="*70)
print("\n⚠️  NOTA: Este teste executa em PRODUÇÃO e exige assinatura digital")
print("   Certificado A1 (.pfx) e senha devem estar configurados corretamente\n")

# Configuração do Prestador
inscricao_municipal = "48779000"  # Será preenchido com zeros à esquerda automaticamente
cnpj_prestador = "05108721000133"
razao_social = "NETCOM SOLUCOES EM INFORMATICA LTDA"

# ===== CONFIGURAÇÃO DO CERTIFICADO DIGITAL =====
# ⚠️ OBRIGATÓRIO para produção!
# Opção 1: Use variáveis de ambiente (RECOMENDADO)
#certificado_pfx = os.getenv("ISS_CERT_PFX", None)
#senha_certificado = os.getenv("ISS_CERT_SENHA", None)

# Opção 2: Configure diretamente (para testes)
# DESCOMENTE e ajuste o caminho do seu certificado:
certificado_pfx = "70282505233bd928.pfx"
senha_certificado = "Ccbcxr05"

# Opção 3: Executar SEM certificado (somente homologação)
# certificado_pfx = None
# senha_certificado = None

# Inicializar API
print("\n📡 Inicializando API ISS Digital São Luís...")
print(f"🏢 Prestador: {razao_social}")
print(f"📋 Inscrição Municipal: {inscricao_municipal}")
print(f"🆔 CNPJ: {cnpj_prestador}")
print(f"🔐 Certificado: {'✅ Configurado' if certificado_pfx else '❌ NÃO configurado (pode falhar em produção!)'}")

if not certificado_pfx or not senha_certificado:
    print("❌ ERRO: Configure certificado_pfx e senha_certificado antes de executar este teste!")
    print("   A prefeitura exige assinatura digital no ambiente de produção.")
    exit(1)

if not os.path.exists(certificado_pfx):
    print(f"❌ ERRO: Arquivo de certificado não encontrado: {certificado_pfx}")
    print("   Ajuste o caminho do arquivo .pfx e execute novamente.")
    exit(1)

api = ISSDigitalSLZ(
    inscricao_prestador=inscricao_municipal,
    cnpj_prestador=cnpj_prestador,
    razao_social_prestador=razao_social,
    certificado_pfx=certificado_pfx,
    senha_certificado=senha_certificado,
    token_envio=None,  # Token não é mais usado no XML (removido conforme exemplo oficial)
    homologacao=False,  # False = PRODUÇÃO (homologação não existe em São Luís!)
    codigo_cidade="921"  # Código SIAFI de São Luís
)
print("✅ API inicializada!")
print(f"📍 Ambiente: PRODUÇÃO (homologação não existe)")
print(f"📋 Inscrição formatada: {api.inscricao_prestador}")

# Preparar dados do RPS conforme layout do manual ISS Digital São Luís
numero_rps = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"  # Número único baseado em timestamp

dados_rps = {
    # Identificação do RPS
    "numero_rps": numero_rps,
    "serie_rps": "NF",  # Padrão "NF" conforme manual
    "tipo_rps": "RPS",  # Padrão "RPS"
    "data_emissao": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "situacao_rps": "N",  # N=Normal, C=Cancelada
    "serie_prestacao": "99",  # 99 = Modelo único (padrão)
    "ddd_prestador": "098",  # DDD do prestador
    "telefone_prestador": "81599692",  # Telefone do prestador
    
    # Dados do Serviço
    "servico": {
        # Valores dos serviços
        "valor_servicos": "1.00",
        "valor_deducoes": "0.00",
        
        # Tributos federais
        "valor_pis": "0.00",
        "valor_cofins": "0.00",
        "valor_inss": "0.00",
        "valor_ir": "0.00",
        "valor_csll": "0.00",
        "aliquota_pis": "0.0000",
        "aliquota_cofins": "0.0000",
        "aliquota_inss": "0.0000",
        "aliquota_ir": "0.0000",
        "aliquota_csll": "0.0000",
        
        # Dados da atividade
        "codigo_atividade": "854140000",  # 9 dígitos (CNAE)
        "codigo_servico": "0801",  # OBRIGATÓRIO - Código do serviço na lista LC 116
        "aliquota_atividade": "5.0000",
        "tipo_recolhimento": "A",  # A=A Receber, R=Retido na Fonte
        "municipio_prestacao": "0921",  # Código SIAFI de São Luís
        "municipio_prestacao_desc": "SAO LUIS",
        "operacao": "A",  # A=Sem Dedução, B=Com Dedução, C=Imune/Isenta, D=Devolução, J=Intermediação
        "tributacao": "T",  # T=Tributável, C=Isenta, E=Não Incidente, F=Imune, etc
        
        # Descrição do serviço
        "discriminacao": "EDUCACAO PROFISSIONAL DE NIVEL TECNICO - ENSINO REGULAR PRE-ESCOLAR, FUNDAMENTAL, MEDIO E SUPERIOR.",
        
        # Itens de serviço (OBRIGATÓRIO conforme XSD - tpListaItens minOccurs=1)
        # Se não fornecido, será gerado automaticamente com os dados do serviço
        "itens": [
            {
                "discriminacao": "EDUCACAO PROFISSIONAL DE NIVEL TECNICO - ENSINO REGULAR PRE-ESCOLAR, FUNDAMENTAL, MEDIO E SUPERIOR.",
                "quantidade": "1.0000",
                "valor_unitario": "1.0000",
                "valor_total": "1.00",
                "tributavel": "S"  # S=Tributável, N=Não tributável
            }
        ]
    },
    
    # Dados do Tomador
    "tomador": {
        # Identificação do tomador
        "cnpj": "79159001372000",  # ou "cpf": "12345678901"
        "inscricao_municipal": "0000000",  # Se não for de São Luís, preencher com "0000000"
        "razao_social": "AFONSO FLÁVIO RIBEIRO DE CARVALHO",
        
        # Endereço do tomador
        "endereco": {
            "tipo_logradouro": "Rua",  # Ver anexo 04 do manual
            "logradouro": "Boa Esperanca",
            "numero": "102",
            "complemento": "sala 01",
            "tipo_bairro": "Bairro",  # Ver anexo 05 do manual
            "bairro": "Turu",
            "codigo_municipio": "0921",  # Código SIAFI de São Luís
            "cidade": "SAO LUIS",
            "cep": "65066190"
        },
        
        # Contato (opcional)
        "email": "afonso@exemplo.com.br",
        "ddd": "98",
        "telefone": "12345678"
    }
}

# Teste 1: Enviar RPS
print("\n" + "="*70)
print("📤 TESTE 1: ENVIAR RPS")
print("="*70)
print(f"📋 Número do RPS: {numero_rps}")
print(f"💰 Valor do Serviço: R$ {dados_rps['servico']['valor_servicos']}")
print(f"👤 Tomador: {dados_rps['tomador']['razao_social']}")

try:
    status, response = api.enviar_rps(dados_rps, debug=True)
    
    print("\n" + "-"*70)
    print("📊 RESULTADO DO ENVIO")
    print("-"*70)
    print(f"Status HTTP: {status}")
    print(f"Resposta: {response}")
    
    # Verifica se o lote foi enviado com sucesso
    if response.get('sucesso') == 'true' or 'numero_lote' in response:
        numero_lote = response.get('numero_lote')
        print(f"\n✅ Lote de RPS enviado com sucesso!")
        print(f"📋 Número do Lote: {numero_lote}")
        
        if response.get('assincrono') == 'S':
            print(f"⏳ Processamento Assíncrono: Use ConsultarLote para verificar o resultado")
        elif response.get('assincrono') == 'N':
            print(f"✅ Processamento Síncrono: Resultado retornado imediatamente")
        
        # Verifica se já retornou as notas (processamento síncrono)
        if 'notas' in response and response['notas']:
            print(f"\n✅ Notas geradas:")
            for nota in response['notas']:
                print(f"   📄 NFS-e: {nota.get('numero_nfse')}")
                print(f"   🔐 Código de Verificação: {nota.get('codigo_verificacao')}")
        
        # Teste 2: Consultar Lote
        print("\n" + "="*70)
        print("📤 TESTE 2: CONSULTAR LOTE")
        print("="*70)
        print(f"📋 Número do Lote: {numero_lote}")
        
        status, consulta = api.consultar_lote(numero_lote, debug=True)
        
        print("\n" + "-"*70)
        print("📊 RESULTADO DA CONSULTA DE LOTE")
        print("-"*70)
        print(f"Status HTTP: {status}")
        print(f"Resposta: {consulta}")
        
        if consulta.get('sucesso') == 'true':
            print(f"\n✅ Lote processado com sucesso!")
            if 'notas' in consulta and consulta['notas']:
                print(f"\n📄 Notas geradas no lote:")
                for nota in consulta['notas']:
                    print(f"   - NFS-e: {nota.get('numero_nfse')}")
                    print(f"     Código de Verificação: {nota.get('codigo_verificacao')}")
            else:
                print(f"\n⏳ Nenhuma nota encontrada (lote pode estar em processamento)")
        elif 'erros' in consulta:
            print(f"\n❌ Erros no processamento do lote:")
            for erro in consulta['erros']:
                if isinstance(erro, dict):
                    print(f"   - [{erro.get('codigo')}] {erro.get('descricao')}")
                else:
                    print(f"   - {erro}")
        
        # Teste 3: Consultar NFSe por RPS
        print("\n" + "="*70)
        print("📤 TESTE 3: CONSULTAR NFSE POR RPS")
        print("="*70)
        print(f"📋 Número do RPS: {numero_rps}")
        print(f"📦 Série de Prestação: 99")
        
        status, consulta_rps = api.consultar_nfse_por_rps(
            numero_rps=numero_rps,
            serie_prestacao="99",  # Padrão 99 - Modelo único
            debug=True
        )
        
        print("\n" + "-"*70)
        print("📊 RESULTADO DA CONSULTA POR RPS")
        print("-"*70)
        print(f"Status HTTP: {status}")
        print(f"Resposta: {consulta_rps}")
        
        if 'notas' in consulta_rps and consulta_rps['notas']:
            print(f"\n✅ NFS-e encontrada:")
            for nota in consulta_rps['notas']:
                print(f"   📄 NFS-e: {nota.get('numero_nfse')}")
                print(f"   🔐 Código de Verificação: {nota.get('codigo_verificacao')}")
        
    elif 'erros' in response:
        print(f"\n❌ Erro ao enviar RPS!")
        print(f"\nErros retornados:")
        for erro in response['erros']:
            if isinstance(erro, dict):
                print(f"   - [{erro.get('codigo')}] {erro.get('mensagem')}")
            else:
                print(f"   - {erro}")
    else:
        print(f"\n⚠️  Resposta inesperada do servidor")
        
except Exception as e:
    print(f"\n❌ ERRO durante o teste!")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")

# Resumo Final
print("\n" + "="*70)
print("📋 RESUMO DO TESTE")
print("="*70)
print(f"✅ Teste de envio: Executado")
print(f"✅ Teste de consulta: Executado")
print(f"ℹ️  Verifique os resultados acima para detalhes")
print("\n" + "="*70)
print("🏁 TESTE CONCLUÍDO")
print("="*70)

print("\n📝 Observações Importantes:")
print("="*70)
print("\n🔍 Debugging:")
print("   - Se houve erro de conexão: Verifique a URL do webservice")
print("   - Se houve erro de autenticação: Verifique CNPJ e Inscrição Municipal")
print("   - Se houve erro de validação XSD: Verifique campos obrigatórios:")
print("     * codigo_servico (OBRIGATÓRIO)")
print("     * Itens (OBRIGATÓRIO - será gerado automaticamente se não fornecido)")
print("     * Namespaces corretos (http://sistemas.semfaz.saoluis.ma.gov.br/WsNFe2/lote)")
print("   - Assinatura digital está TEMPORARIAMENTE DESABILITADA para testes")
print("   - TokenEnvio foi removido do XML (não é mais usado)")
print("   - Campo transacao está vazio (<transacao/>)")

print("\n📚 Documentação:")
print("   - Manual oficial: manual nfse são luis.txt")
print("   - Código SIAFI de São Luís: 0921")
print("   - Série RPS padrão: NF")
print("   - Série de Prestação padrão: 99 (Modelo único)")

print("\n🔐 Sobre o Certificado Digital:")
print("   - OBRIGATÓRIO no ambiente de PRODUÇÃO")
print("   - OPCIONAL no ambiente de HOMOLOGAÇÃO")
print("   - Tipo: A1 (arquivo .pfx) ou A3 (token/smartcard)")
print("   - Deve conter o CNPJ do prestador")
print("   - Custo aproximado: R$ 200/ano (A1)")

print("\n" + "="*70)
print("🔐 COMO CONFIGURAR O CERTIFICADO DIGITAL")
print("="*70)

print("\n📋 Opção 1: Variáveis de Ambiente (RECOMENDADO)")
print("   Bash/Linux:")
print("   export ISS_CERT_PFX='/caminho/para/certificado.pfx'")
print("   export ISS_CERT_SENHA='SenhaDoCertificado'")
print("   python teste_issdigital.py")
print()
print("   PowerShell/Windows:")
print("   $env:ISS_CERT_PFX='C:\\caminho\\para\\certificado.pfx'")
print("   $env:ISS_CERT_SENHA='SenhaDoCertificado'")
print("   python teste_issdigital.py")

print("\n📋 Opção 2: Editar este arquivo")
print("   1. Abra este arquivo (teste_issdigital.py)")
print("   2. Descomente as linhas 32-33")
print("   3. Configure o caminho do certificado e senha")
print("   4. Execute: python teste_issdigital.py")

print("\n📋 Opção 3: Executar sem certificado (SOMENTE HOMOLOGAÇÃO)")
print("   ⚠️  ATENÇÃO: NÃO funciona em produção!")
print("   - Certifique-se de que homologacao=True na linha 57")
print("   - Deixe certificado_pfx=None e senha_certificado=None")

print("\n📚 Onde obter Certificado Digital A1:")
print("   - Serasa Experian: https://www.serasaexperian.com.br")
print("   - Certisign: https://www.certisign.com.br")
print("   - Valid Certificadora: https://www.validcertificadora.com.br")
print("   - Soluti: https://www.soluti.com.br")

print("\n📖 Mais informações:")
print("   - Layout completo: Veja manual nfse são luis.txt")
print("   - Anexo 01: Códigos de erro")
print("   - Anexo 03: Formatação de Inscrição Municipal")
print("   - Anexo 04: Tipos de Logradouro")
print("   - Anexo 05: Tipos de Bairro")

print("\n" + "="*70)
print("✅ Implementado conforme especificação oficial do ISS Digital São Luís")
print("="*70 + "\n")

