# 📋 ISS Digital - São Luís/MA - Integração NFSe

Biblioteca Python para integração com o sistema ISS Digital da Prefeitura Municipal de São Luís/MA.

## 📚 Documentação Oficial

- XSD de Produção: https://www.semfaz.saoluis.ma.gov.br/fckeditor/userfiles/xsd_producao.rar
- Portal da SEMFAZ: https://www.semfaz.saoluis.ma.gov.br/

## 🔧 Instalação

### Dependências Necessárias

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install requests lxml pyOpenSSL signxml cryptography
```

### ⚠️ IMPORTANTE: Certificado Digital Obrigatório

O ISS Digital de São Luís **EXIGE certificado digital A1** para assinar o XML antes do envio. Você precisa:

1. **Certificado Digital A1** (arquivo `.pfx` ou `.p12`)
2. **Senha** do certificado
3. Certificado **válido** (não vencido)
4. Certificado do **CNPJ da empresa** prestadora

**Sem o certificado, a nota NÃO será aceita pelo webservice!**

## 🚀 Como Usar

### 1. Inicialização COM Certificado Digital (Obrigatório em Produção)

```python
from nfse_issdigital_slz import ISSDigitalSLZ

# Inicializar API COM certificado digital
api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    certificado_pfx="/caminho/para/certificado.pfx",  # ✅ Certificado A1
    senha_certificado="senha_do_certificado",          # ✅ Senha do certificado
    homologacao=False
)
```

**Ao inicializar, você verá:**
```
✅ Certificado carregado com sucesso!
   Titular: NETCOM TREINAMENTOS E SOLUCOES TECNOLOGICAS LTDA
   Validade: 20240401150325Z até 20250401150325Z
```

### 1.1 Inicialização SEM Certificado (Apenas para Testes)

⚠️ **ATENÇÃO:** Sem certificado, o webservice pode rejeitar a requisição!

```python
# Para testes SEM certificado (pode não funcionar)
api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    homologacao=True  # Sem certificado
)
```

### 2. Enviar RPS

```python
# Dados do RPS
dados_rps = {
    "numero_rps": "1",
    "serie_rps": "1",
    "tipo_rps": "1",  # 1=RPS
    "data_emissao": "2025-10-21T10:00:00",
    "servico": {
        "valor_servicos": "100.00",
        "valor_deducoes": "0.00",
        "iss_retido": "2",  # 1=Sim, 2=Não
        "valor_iss": "5.00",
        "base_calculo": "100.00",
        "aliquota": "5.00",
        "valor_liquido": "95.00",
        "item_lista_servico": "0801",  # Código LC 116
        "codigo_cnae": "854140000",
        "codigo_tributacao_municipio": "854140000",
        "discriminacao": "Descrição do serviço prestado",
        "codigo_municipio": "2111300"  # São Luís
    },
    "tomador": {
        "cnpj": "12345678000195",  # ou "cpf": "12345678901"
        "razao_social": "Nome do Cliente",
        "endereco": {
            "logradouro": "Rua Exemplo",
            "numero": "123",
            "complemento": "Sala 1",
            "bairro": "Centro",
            "codigo_municipio": "2111300",
            "uf": "MA",
            "cep": "65000000"
        }
    }
}

# Enviar RPS
status, response = api.enviar_rps(dados_rps, debug=True)
print(f"Status: {status}")
print(f"Resposta: {response}")
```

### 3. Consultar Lote

```python
# Consultar pelo protocolo retornado no envio
protocolo = response['protocolo']
status, response = api.consultar_lote(protocolo, debug=True)
print(f"Resposta: {response}")
```

### 4. Consultar NFSe por RPS

```python
status, response = api.consultar_nfse_por_rps(
    numero_rps="1",
    serie_rps="1",
    tipo_rps="1",
    debug=True
)
print(f"Resposta: {response}")
```

## 📋 Estrutura de Dados

### Tipos de RPS

| Código | Descrição |
|--------|-----------|
| 1 | RPS |
| 2 | Nota Fiscal Conjugada |
| 3 | Cupom |

### ISS Retido

| Código | Descrição |
|--------|-----------|
| 1 | Sim |
| 2 | Não |

### Item Lista de Serviço (LC 116/2003)

Exemplos comuns:
- `0801` - Ensino regular pré-escolar, fundamental, médio e superior
- `0802` - Instrução, treinamento, orientação pedagógica
- `0101` - Análise e desenvolvimento de sistemas
- `1705` - Reparação, conservação e reforma de edifícios

**Consulte a lista completa da LC 116/2003!**

## ⚠️ Campos Obrigatórios

### RPS
- ✅ `numero_rps`
- ✅ `serie_rps`
- ✅ `tipo_rps`
- ✅ `data_emissao`

### Prestador
- ✅ `cnpj_prestador` (configurado na inicialização)
- ✅ `inscricao_prestador` (configurado na inicialização)

### Serviço
- ✅ `valor_servicos`
- ✅ `base_calculo`
- ✅ `aliquota`
- ✅ `item_lista_servico`
- ✅ `discriminacao`

### Tomador
- ✅ `cnpj` ou `cpf`
- ✅ `razao_social`
- ✅ `endereco.logradouro`
- ✅ `endereco.numero`
- ✅ `endereco.bairro`
- ✅ `endereco.codigo_municipio`
- ✅ `endereco.uf`
- ✅ `endereco.cep`

## 🔍 Modo Debug

Use `debug=True` em qualquer método para ver:
- XML gerado
- Envelope SOAP
- Request completo
- Response XML
- Parse dos dados

```python
status, response = api.enviar_rps(dados_rps, debug=True)
```

## 🔐 URLs do WebService

### Produção
- WSDL: `https://www.semfaz.saoluis.ma.gov.br/nfse/NfseService.svc?wsdl`
- Endpoint: `https://www.semfaz.saoluis.ma.gov.br/nfse/NfseService.svc`

### Homologação
- WSDL: `https://www.semfaz.saoluis.ma.gov.br/nfse_homologacao/NfseService.svc?wsdl`
- Endpoint: `https://www.semfaz.saoluis.ma.gov.br/nfse_homologacao/NfseService.svc`

⚠️ **Nota:** A URL de homologação pode não estar disponível publicamente.

## 📊 Métodos Disponíveis

| Método | Descrição |
|--------|-----------|
| `enviar_rps(dados_rps, debug=False)` | Envia RPS para gerar NFSe |
| `consultar_lote(protocolo, debug=False)` | Consulta lote pelo protocolo |
| `consultar_nfse_por_rps(numero, serie, tipo, debug=False)` | Consulta NFSe por RPS |

## 🎯 Fluxo de Emissão

1. **Enviar RPS** → Recebe `protocolo`
2. **Consultar Lote** (usando protocolo) → Recebe `numero_nfse` e `codigo_verificacao`
3. **Guardar** número e código para futuras consultas

## ⚠️ Importante

### Certificado Digital

O ISS Digital de São Luís pode requerer certificado digital (A1 ou A3). Neste caso:
1. Você precisará assinar o XML antes de enviar
2. Use bibliotecas como `lxml` e `signxml` para assinar
3. Configure o certificado no código

### Numeração de RPS

- A numeração de RPS deve ser **sequencial**
- Não pode haver "buracos" na numeração
- Controle a numeração no seu sistema

### Código do Município

- São Luís/MA: `2111300` (Código IBGE)
- Use sempre este código para serviços prestados em São Luís

## 🧪 Testando

Execute o script de teste:

```bash
cd /home/afonso/docker/odoo_geracad/addons/geracad_nfse/nfse_issdigital_slz
python pyissdigital.py
```

## ❌ Erros Comuns

### 1. "Prestador não encontrado"
**Causa:** CNPJ ou Inscrição Municipal incorretos.
**Solução:** Verifique se está cadastrado na SEMFAZ.

### 2. "RPS já utilizado"
**Causa:** Número de RPS duplicado.
**Solução:** Use numeração sequencial única.

### 3. "Serviço não encontrado"
**Causa:** Código de serviço inválido.
**Solução:** Verifique o código na LC 116/2003.

### 4. "Timeout"
**Causa:** Webservice fora do ar ou lento.
**Solução:** Tente novamente mais tarde.

## 🔐 Como Obter o Certificado Digital

### Passo a Passo

1. **Adquirir Certificado A1**
   - Procure uma Autoridade Certificadora credenciada (Serasa, Certisign, etc.)
   - Escolha **e-CNPJ tipo A1** (arquivo)
   - Validade: 1 ano

2. **Baixar o Certificado**
   - Após emissão, baixe o arquivo `.pfx` ou `.p12`
   - Guarde a senha fornecida

3. **Armazenar com Segurança**
   ```bash
   # Coloque em local seguro
   /home/usuario/certificados/empresa.pfx
   
   # Configure permissões restritas
   chmod 400 /home/usuario/certificados/empresa.pfx
   ```

4. **Usar na Aplicação**
   ```python
   certificado_pfx = "/home/usuario/certificados/empresa.pfx"
   senha_certificado = "SenhaDoC3rtificado"
   ```

### Tipos de Certificado

| Tipo | Formato | Onde Fica | Uso |
|------|---------|-----------|-----|
| **A1** | Arquivo `.pfx` | No servidor | ✅ Recomendado para API |
| **A3** | Token/Smartcard | Físico | ❌ Difícil de automatizar |

**Para ISS Digital, use certificado A1!**

### Verificar Validade do Certificado

```bash
# Linux/Mac
openssl pkcs12 -in certificado.pfx -noout -info

# Ou use o código Python
python -c "
from OpenSSL import crypto
with open('certificado.pfx', 'rb') as f:
    p12 = crypto.load_pkcs12(f.read(), b'senha')
    cert = p12.get_certificate()
    print('Titular:', cert.get_subject().CN)
    print('Validade:', cert.get_notAfter().decode())
"
```

## 📞 Suporte

- SEMFAZ São Luís: https://www.semfaz.saoluis.ma.gov.br/
- Telefone: (98) 3214-8900

## 🔗 Links Úteis

- [LC 116/2003 - Lista de Serviços](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp116.htm)
- [Código IBGE dos Municípios](https://www.ibge.gov.br/explica/codigos-dos-municipios.php)
- [CNAE - Classificação Nacional de Atividades Econômicas](https://cnae.ibge.gov.br/)

## 📝 Exemplo Completo

```python
from nfse_issdigital_slz import ISSDigitalSLZ

# Configurar
api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    homologacao=False
)

# Preparar dados
dados_rps = {
    "numero_rps": "1",
    "serie_rps": "1",
    "tipo_rps": "1",
    "servico": {
        "valor_servicos": "1000.00",
        "aliquota": "5.00",
        "valor_iss": "50.00",
        "valor_liquido": "950.00",
        "item_lista_servico": "0801",
        "codigo_cnae": "854140000",
        "discriminacao": "Curso técnico profissionalizante"
    },
    "tomador": {
        "cnpj": "12345678000195",
        "razao_social": "Cliente Exemplo Ltda",
        "endereco": {
            "logradouro": "Av. Principal",
            "numero": "100",
            "bairro": "Centro",
            "codigo_municipio": "2111300",
            "uf": "MA",
            "cep": "65000000"
        }
    }
}

# Enviar
print("Enviando RPS...")
status, response = api.enviar_rps(dados_rps, debug=True)

if 'protocolo' in response:
    print(f"\n✅ RPS enviado! Protocolo: {response['protocolo']}")
    
    # Consultar
    print("\nConsultando lote...")
    status, consulta = api.consultar_lote(response['protocolo'], debug=True)
    
    if 'numero_nfse' in consulta:
        print(f"\n✅ NFSe gerada! Número: {consulta['numero_nfse']}")
        print(f"Código de Verificação: {consulta['codigo_verificacao']}")
    else:
        print("\n⏳ NFSe ainda em processamento. Tente novamente em alguns instantes.")
else:
    print(f"\n❌ Erro ao enviar RPS: {response}")
```

---

**Versão:** 1.0.0  
**Autor:** Netcom Treinamentos e Soluções Tecnológicas  
**Data:** Outubro 2025

