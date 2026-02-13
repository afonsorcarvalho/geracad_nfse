# -*- coding: utf-8 -*-
"""
Teste simples de consulta de NFS-e
Apenas consulta notas existentes, não envia nada novo
"""

from pyissdigital import ISSDigitalSLZ
from datetime import datetime, timedelta

print("="*70)
print("🔍 TESTE DE CONSULTA DE NOTAS - ISS DIGITAL SÃO LUÍS")
print("="*70)

# Configuração do Prestador
inscricao_municipal = "48779000"
cnpj_prestador = "05108721000133"
razao_social = "NETCOM SOLUCOES EM INFORMATICA LTDA"

# ⚠️  IMPORTANTE: Ambiente de homologação não existe em São Luís!
# A URL beta.semfaz.saoluis.ma.gov.br retorna 404
# É necessário usar PRODUÇÃO direto (com certificado)

print("\n📡 Inicializando API com certificado...")
print("⚠️  ATENÇÃO: São Luís não possui ambiente de homologação!")
print("   Usando ambiente de PRODUÇÃO diretamente")

api = ISSDigitalSLZ(
    inscricao_prestador=inscricao_municipal,
    cnpj_prestador=cnpj_prestador,
    razao_social_prestador=razao_social,
    certificado_pfx="70282505233bd928.pfx",  # CERTIFICADO OBRIGATÓRIO
    senha_certificado="Ccbcxr05",
    token_envio="1234567890",
    homologacao=False,  # PRODUÇÃO (homologação não existe)
    codigo_cidade="0921"
)
print("✅ API inicializada!")

# Período de consulta: últimos 30 dias
data_fim = datetime.now().strftime("%Y-%m-%d")
data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

print("\n" + "="*70)
print("📋 TESTE: CONSULTAR NOTAS POR PERÍODO")
print("="*70)
print(f"📅 Data Início: {data_inicio}")
print(f"📅 Data Fim: {data_fim}")
print(f"📄 Nota Inicial: 1")
print(f"🏢 CNPJ: {cnpj_prestador}")
print(f"📋 Inscrição Municipal: {inscricao_municipal}")

try:
    status, response = api.consultar_notas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        nota_inicial=0,
        debug=True
    )
    
    print("\n" + "-"*70)
    print("📊 RESULTADO DA CONSULTA")
    print("-"*70)
    print(f"Status HTTP: {status}")
    print(f"Resposta: {response}")
    
    if response.get('sucesso') == 'true' or response.get('sucesso') == 'S':
        print(f"\n✅ Consulta realizada com sucesso!")
        
        if 'notas' in response and response['notas']:
            print(f"\n📄 Notas encontradas: {len(response['notas'])}")
            for i, nota in enumerate(response['notas'][:5], 1):  # Mostra as 5 primeiras
                print(f"\n   {i}. NFS-e: {nota.get('numero_nfse')}")
                print(f"      Código de Verificação: {nota.get('codigo_verificacao')}")
                print(f"      Inscrição Prestador: {nota.get('inscricao_prestador')}")
            
            if len(response['notas']) > 5:
                print(f"\n   ... e mais {len(response['notas']) - 5} nota(s)")
        else:
            print(f"\n⚠️  Nenhuma nota encontrada no período")
            print(f"   Isso é normal se ainda não houver notas emitidas")
    
    elif 'erros' in response:
        print(f"\n❌ Erro na consulta!")
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
    import traceback
    traceback.print_exc()

# Resumo
print("\n" + "="*70)
print("🏁 TESTE DE CONSULTA CONCLUÍDO")
print("="*70)
print("\n📝 Observações:")
print("   - Se sucesso='true': Credenciamento OK, webservice funciona!")
print("   - Se erro de permissão: Verifique CNPJ e Inscrição Municipal")
print("   - Se erro de validação: Verifique os dados conforme manual")
print("   - Consulte TROUBLESHOOTING.md para mais ajuda")
print("\n" + "="*70 + "\n")

