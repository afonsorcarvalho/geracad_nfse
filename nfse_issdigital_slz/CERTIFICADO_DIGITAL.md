# 🔐 Guia Completo - Certificado Digital para ISS Digital São Luís

## ⚠️ AVISO IMPORTANTE

O ISS Digital de São Luís **EXIGE** certificado digital A1 para assinar o XML antes do envio ao webservice. **SEM o certificado, suas notas serão REJEITADAS!**

## 🎯 O Que Você Precisa

- ✅ Certificado digital **e-CNPJ tipo A1**
- ✅ Arquivo `.pfx` ou `.p12` do certificado
- ✅ Senha do certificado
- ✅ Certificado **válido** (não vencido)
- ✅ Certificado do **CNPJ da empresa prestadora**

## 📋 Passo a Passo para Obter

### 1. Escolher uma Autoridade Certificadora (AC)

Autoridades Certificadoras credenciadas no Brasil:
- **Serasa Experian** - https://certificadodigital.serasaexperian.com.br/
- **Certisign** - https://www.certisign.com.br/
- **Valid Certificadora** - https://www.validcertificadora.com.br/
- **Soluti** - https://www.soluti.com.br/

### 2. Adquirir o Certificado

1. **Acesse** o site da AC escolhida
2. **Selecione:** e-CNPJ **Tipo A1** (arquivo)
3. **Validade:** 1 ano (padrão)
4. **Preço:** Aproximadamente R$ 200-300/ano

### 3. Validação Presencial

Você precisará fazer **validação presencial** em um posto da AC com:
- 📄 Documento de identificação (RG/CNH)
- 📄 Procuração (se não for o representante legal)
- 📄 Cartão CNPJ da empresa
- 📄 Documentos societários da empresa

### 4. Baixar o Certificado

Após aprovação:
1. Você receberá email com **código/token**
2. Acesse o site da AC
3. Faça **download** do certificado (arquivo `.pfx`)
4. **Anote a senha** fornecida!

### 5. Armazenar com Segurança

```bash
# Crie um diretório seguro
mkdir -p /opt/certificados
chmod 700 /opt/certificados

# Copie o certificado
cp certificado.pfx /opt/certificados/empresa.pfx

# Configure permissões restritas
chmod 400 /opt/certificados/empresa.pfx
chown usuario:grupo /opt/certificados/empresa.pfx
```

## 💻 Como Usar no Código

### Básico

```python
from nfse_issdigital_slz import ISSDigitalSLZ

api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    certificado_pfx="/opt/certificados/empresa.pfx",
    senha_certificado="SenhaSecreta123",
    homologacao=False
)
```

### Com Variáveis de Ambiente (Recomendado)

```python
import os
from nfse_issdigital_slz import ISSDigitalSLZ

# Configure variáveis de ambiente
# export CERT_PFX="/opt/certificados/empresa.pfx"
# export CERT_SENHA="SenhaSecreta123"

api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    certificado_pfx=os.getenv("CERT_PFX"),
    senha_certificado=os.getenv("CERT_SENHA"),
    homologacao=False
)
```

### Em Produção Odoo

```python
# No modelo Odoo
class GeracadNfse(models.Model):
    _name = "geracad.nfse"
    
    def enviar_issdigital(self):
        # Busca configuração do certificado
        cert_config = self.env['geracad.certificado'].search([
            ('company_id', '=', self.company_id.id),
            ('ativo', '=', True)
        ], limit=1)
        
        if not cert_config:
            raise UserError("Certificado digital não configurado!")
        
        # Inicializa API com certificado
        api = ISSDigitalSLZ(
            inscricao_prestador=self.company_id.inscricao_municipal,
            cnpj_prestador=self.company_id.cnpj,
            certificado_pfx=cert_config.arquivo_pfx,
            senha_certificado=cert_config.senha,
            homologacao=False
        )
        
        # Envia RPS...
```

## 🔍 Verificar se o Certificado Está Correto

### Verificação Rápida (Terminal)

```bash
# Ver informações do certificado
openssl pkcs12 -in certificado.pfx -noout -info

# Ver dados do certificado (pede senha)
openssl pkcs12 -in certificado.pfx -info

# Extrair certificado (sem chave privada)
openssl pkcs12 -in certificado.pfx -clcerts -nokeys -out cert.pem

# Ver validade
openssl x509 -in cert.pem -noout -dates
```

### Verificação com Python

```python
from OpenSSL import crypto
from datetime import datetime

def verificar_certificado(pfx_file, senha):
    try:
        # Carrega o certificado
        with open(pfx_file, 'rb') as f:
            pfx_data = f.read()
        
        p12 = crypto.load_pkcs12(pfx_data, senha.encode())
        cert = p12.get_certificate()
        
        # Informações
        print("="*60)
        print("📋 INFORMAÇÕES DO CERTIFICADO")
        print("="*60)
        print(f"Titular: {cert.get_subject().CN}")
        print(f"Emissor: {cert.get_issuer().CN}")
        print(f"Serial: {cert.get_serial_number()}")
        
        # Validade
        not_before = cert.get_notBefore().decode()
        not_after = cert.get_notAfter().decode()
        print(f"Válido de: {not_before}")
        print(f"Válido até: {not_after}")
        
        # Verifica se está válido
        # (Formato: YYYYMMDDHHMMSSZ)
        from datetime import datetime
        validade = datetime.strptime(not_after, "%Y%m%d%H%M%SZ")
        hoje = datetime.now()
        
        if validade < hoje:
            print("❌ CERTIFICADO VENCIDO!")
        else:
            dias_restantes = (validade - hoje).days
            print(f"✅ Certificado válido! ({dias_restantes} dias restantes)")
        
        print("="*60)
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# Uso
verificar_certificado("/opt/certificados/empresa.pfx", "senha")
```

## ⚙️ Configuração no Sistema

### 1. Instalar Dependências

```bash
pip install pyOpenSSL signxml cryptography lxml
```

### 2. Testar Certificado

```bash
cd /home/afonso/docker/odoo_geracad/addons/geracad_nfse/nfse_issdigital_slz
python3 << EOF
from pyissdigital import ISSDigitalSLZ

api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    certificado_pfx="/opt/certificados/empresa.pfx",
    senha_certificado="SenhaSecreta123",
    homologacao=False
)
print("✅ Certificado configurado com sucesso!")
EOF
```

## 🔒 Segurança

### ✅ Boas Práticas

1. **Nunca** comite o certificado no Git
2. **Nunca** exponha a senha em código
3. Use **variáveis de ambiente** ou **cofre de senhas**
4. Configure **permissões restritas** (chmod 400)
5. Faça **backup** do certificado em local seguro
6. **Monitore** a validade (renove antes do vencimento)

### ❌ Más Práticas

```python
# ❌ NÃO FAÇA ISSO!
certificado_pfx = "/home/usuario/Downloads/cert.pfx"  # Local inseguro
senha_certificado = "senha123"  # Senha hardcoded no código

# ❌ NÃO FAÇA ISSO!
# arquivo: certificado.pfx commitado no Git

# ❌ NÃO FAÇA ISSO!
chmod 777 certificado.pfx  # Permissões abertas
```

### ✅ Forma Correta

```python
# ✅ Use variáveis de ambiente
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega do .env (que não vai pro Git!)

certificado_pfx = os.getenv("ISS_CERT_PFX")
senha_certificado = os.getenv("ISS_CERT_SENHA")

# .env (NÃO commitar!)
# ISS_CERT_PFX=/opt/certificados/empresa.pfx
# ISS_CERT_SENHA=SenhaSecreta123

# .gitignore
# .env
# *.pfx
# *.p12
```

## 🚨 Problemas Comuns

### 1. "Certificado vencido"
**Solução:** Renove o certificado com a AC.

### 2. "Senha incorreta"
**Solução:** Verifique a senha fornecida pela AC.

### 3. "Arquivo não encontrado"
**Solução:** Verifique o caminho do arquivo `.pfx`.

### 4. "Certificado de CNPJ diferente"
**Solução:** O certificado deve ser do CNPJ prestador.

### 5. "Erro ao assinar XML"
**Solução:** Verifique as dependências (pyOpenSSL, signxml).

## 📊 Tipos de Certificado

| Tipo | Formato | Armazenamento | Custo | Uso API |
|------|---------|---------------|-------|---------|
| **A1** | Arquivo (`.pfx`) | Servidor | ~R$ 200/ano | ✅ Recomendado |
| **A3** | Token USB/Cartão | Físico | ~R$ 300/ano | ❌ Difícil |

**Para automação via API, use SEMPRE certificado A1!**

## 🔄 Renovação do Certificado

Certificados A1 têm validade de **1 ano**. Para renovar:

1. **30 dias antes** do vencimento, inicie a renovação
2. Processo é **mais simples** que a emissão inicial
3. **Não precisa** validação presencial (geralmente)
4. **Atualize** o arquivo `.pfx` no servidor
5. **Reinicie** a aplicação

## 📞 Suporte

### Problemas com o Certificado
- Suporte da AC contratada
- Serasa: (11) 3003-8888
- Certisign: (11) 3993-6800

### Problemas com ISS Digital
- SEMFAZ São Luís: (98) 3214-8900
- Portal: https://www.semfaz.saoluis.ma.gov.br/

## 📝 Checklist

Antes de começar a emitir notas:

- [ ] Certificado A1 adquirido
- [ ] Arquivo `.pfx` baixado
- [ ] Senha anotada em local seguro
- [ ] Certificado armazenado com permissões restritas
- [ ] Dependências instaladas (pyOpenSSL, signxml)
- [ ] Certificado testado no código
- [ ] Validade verificada (não vencido)
- [ ] CNPJ do certificado = CNPJ prestador
- [ ] Variáveis de ambiente configuradas
- [ ] Backup do certificado realizado

---

**Versão:** 1.0.0  
**Data:** Outubro 2025  
**Autor:** Netcom Treinamentos e Soluções Tecnológicas

