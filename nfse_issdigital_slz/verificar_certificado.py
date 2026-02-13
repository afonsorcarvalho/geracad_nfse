# -*- coding: utf-8 -*-
"""
Script para verificar se o certificado digital está correto
Execute antes de tentar emitir notas

Autor: Afonso Carvalho
"""

import sys
import os
from datetime import datetime

print("="*70)
print("🔐 VERIFICAÇÃO DE CERTIFICADO DIGITAL")
print("="*70)

# Solicita caminho do certificado
print("\n📋 Informe o caminho do certificado .pfx:")
certificado_pfx = input("Caminho: ").strip()

if not certificado_pfx:
    print("❌ Caminho vazio!")
    sys.exit(1)

if not os.path.exists(certificado_pfx):
    print(f"❌ Arquivo não encontrado: {certificado_pfx}")
    sys.exit(1)

# Solicita senha
print("\n🔑 Informe a senha do certificado:")
senha = input("Senha: ").strip()

if not senha:
    print("❌ Senha vazia!")
    sys.exit(1)

# Tenta carregar o certificado
print("\n⏳ Verificando certificado...")

try:
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.hazmat.backends import default_backend
    from cryptography import x509
    
    # Carrega o arquivo
    with open(certificado_pfx, 'rb') as f:
        pfx_data = f.read()
    
    # Tenta carregar com a senha
    try:
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, 
            senha.encode(),
            backend=default_backend()
        )
    except Exception as e:
        print(f"\n❌ ERRO: Senha incorreta ou certificado inválido!")
        print(f"   Detalhes: {e}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✅ CERTIFICADO VÁLIDO E CARREGADO COM SUCESSO!")
    print("="*70)
    
    # Extrai informações do subject
    subject = certificate.subject
    issuer = certificate.issuer
    
    # Titular
    print(f"\n📋 Titular:")
    cn = None
    org = None
    for attribute in subject:
        if attribute.oid == x509.NameOID.COMMON_NAME:
            cn = attribute.value
        elif attribute.oid == x509.NameOID.ORGANIZATION_NAME:
            org = attribute.value
    
    if cn:
        print(f"   CN (Nome): {cn}")
    if org:
        print(f"   Organização: {org}")
    
    # Emissor
    print(f"\n🏢 Emissor:")
    issuer_cn = None
    for attribute in issuer:
        if attribute.oid == x509.NameOID.COMMON_NAME:
            issuer_cn = attribute.value
            break
    if issuer_cn:
        print(f"   {issuer_cn}")
    
    # Serial
    print(f"\n🔢 Número Serial:")
    print(f"   {certificate.serial_number}")
    
    # Validade
    not_before = certificate.not_valid_before
    not_after = certificate.not_valid_after
    
    print(f"\n📅 Validade:")
    print(f"   De: {not_before}")
    print(f"   Até: {not_after}")
    
    # Verifica se está válido
    if hasattr(not_after, 'tzinfo') and not_after.tzinfo:
        hoje = datetime.now(not_after.tzinfo)
    else:
        hoje = datetime.now()
    
    if not_after < hoje:
        print(f"\n❌ CERTIFICADO VENCIDO!")
        print(f"   Venceu em: {not_after.strftime('%d/%m/%Y')}")
        print(f"   Você precisa renovar o certificado!")
    else:
        dias_restantes = (not_after - hoje).days
        print(f"\n✅ Certificado válido!")
        print(f"   Dias restantes: {dias_restantes}")
        
        if dias_restantes < 30:
            print(f"   ⚠️  ATENÇÃO: Certificado vence em menos de 30 dias!")
            print(f"   Providencie a renovação!")
    
    # Instruções de uso
    print("\n" + "="*70)
    print("📝 COMO USAR ESTE CERTIFICADO")
    print("="*70)
    
    print("\n1️⃣ Configure variáveis de ambiente:")
    print(f"   export ISS_CERT_PFX='{certificado_pfx}'")
    print(f"   export ISS_CERT_SENHA='{senha}'")
    
    print("\n2️⃣ Execute o teste:")
    print("   python teste_issdigital.py")
    
    print("\n3️⃣ Ou use diretamente no código:")
    print("   from nfse_issdigital_slz import ISSDigitalSLZ")
    print("   ")
    print("   api = ISSDigitalSLZ(")
    print("       inscricao_prestador='48779000',")
    print("       cnpj_prestador='05108721000133',")
    print(f"       certificado_pfx='{certificado_pfx}',")
    print(f"       senha_certificado='{senha}',")
    print("       homologacao=False")
    print("   )")
    
    print("\n" + "="*70)
    print("✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print("\n🎉 Seu certificado está pronto para usar!\n")
    
except ImportError:
    print("\n❌ ERRO: Biblioteca cryptography não instalada!")
    print("\n📦 Instale as dependências:")
    print("   pip install -r requirements.txt")
    print("\nOu:")
    print("   pip install cryptography")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

