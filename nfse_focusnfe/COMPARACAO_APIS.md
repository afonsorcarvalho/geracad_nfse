# 📊 Comparação: PlugNotas vs Focus NFSe

## Resumo Executivo

| Característica | PlugNotas | Focus NFSe |
|----------------|-----------|------------|
| **Autenticação** | x-api-key no header | Basic Auth (token + senha vazia) |
| **Identificador de Nota** | ID automático | Referência manual |
| **Cadastro de Empresa via API** | ✅ Sim | ❌ Não (em homologação) |
| **Formato de Dados** | JSON proprietário | JSON proprietário |
| **Ambiente de Homologação** | Sandbox completo | Limitado (sem API empresas) |

## 🔑 Autenticação

### PlugNotas
```python
headers = {
    "Content-Type": "application/json",
    "x-api-key": "sua_api_key_aqui"
}
```

### Focus NFSe
```python
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth(api_token, '')  # Token como usuário, senha vazia
```

## 📝 Envio de NFSe

### PlugNotas
- **URL:** `POST https://api.plugnotas.com.br/nfse`
- **ID:** Gerado automaticamente pela API
- **Retorno:** Retorna o ID da nota criada

```python
response = requests.post(url, headers=headers, json=data)
# Response: {"id": "6702f13a72ffd16e793bae6d", ...}
```

### Focus NFSe
- **URL:** `POST https://api.focusnfe.com.br/v2/nfse?ref=REFERENCIA`
- **ID:** Você define uma "referência" única
- **Retorno:** Usa a mesma referência para consultas

```python
url = f"{base_url}/v2/nfse?ref=NOTA_001"
response = requests.post(url, auth=auth, json=data)
```

## 🔍 Consulta de NFSe

### PlugNotas
```python
# Usa o ID retornado no envio
nfse_id = "6702f13a72ffd16e793bae6d"
url = f"https://api.plugnotas.com.br/nfse/{nfse_id}"
response = requests.get(url, headers=headers)
```

### Focus NFSe
```python
# Usa a referência que você definiu
referencia = "NOTA_001"
url = f"https://api.focusnfe.com.br/v2/nfse/{referencia}"
response = requests.get(url, auth=auth)
```

## 📄 Download de PDF

### PlugNotas
```python
url = f"https://api.plugnotas.com.br/nfse/pdf/{nfse_id}"
headers["Content-Type"] = "application/pdf"
response = requests.get(url, headers=headers, stream=True)
```

### Focus NFSe
```python
url = f"https://api.focusnfe.com.br/v2/nfse/{referencia}.pdf"
response = requests.get(url, auth=auth, stream=True)
```

## 🏢 Cadastro de Empresas

### PlugNotas
✅ **Disponível via API** em sandbox e produção
```python
url = "https://api.plugnotas.com.br/empresa"
response = requests.post(url, headers=headers, json=data_empresa)
```

### Focus NFSe
❌ **NÃO disponível em homologação**
- Cadastro deve ser feito via painel web
- Em produção, pode estar disponível via API `/v2/empresas`

## 🎯 Estrutura de Dados da NFSe

### PlugNotas
```python
data = [{
    "prestador": {"cpfCnpj": "05108721000133"},
    "tomador": {
        "cpfCnpj": "79159001372",
        "razaoSocial": "NOME CLIENTE",
        # ...
    },
    "servico": {
        "codigo": "0801",
        "descricaoLC116": "ENSINO...",
        "discriminacao": "EDUCACAO...",
        "cnae": "854140000",
        # ...
    }
}]
```

### Focus NFSe
```python
data = {
    "data_emissao": "2025-10-20T10:00:00",
    "prestador": {
        "cnpj": "05108721000133",
        "inscricao_municipal": "48779000",
        # ...
    },
    "tomador": {
        "cnpj": "79159001372",
        "razao_social": "NOME CLIENTE",
        # ...
    },
    "servico": {
        "aliquota": 5.00,
        "discriminacao": "EDUCACAO...",
        "item_lista_servico": "08.01",
        "codigo_cnae": "8541400",
        # ...
    }
}
```

## ⚡ Principais Diferenças nos Campos

| Campo | PlugNotas | Focus NFSe |
|-------|-----------|------------|
| CNPJ/CPF | `cpfCnpj` | `cnpj` ou `cpf` |
| Razão Social | `razaoSocial` | `razao_social` |
| Código de Serviço | `codigo` | `item_lista_servico` |
| Descrição LC116 | `descricaoLC116` | (não usado) |
| CNAE | `cnae` | `codigo_cnae` |
| Alíquota | `iss.aliquota` | `aliquota` |
| Tipo Tributação | `iss.tipoTributacao` | (implícito) |

## 🔄 Cancelamento

### PlugNotas
```python
url = f"https://api.plugnotas.com.br/nfse/{nfse_id}"
data = {"motivo": "Nota emitida incorretamente"}
response = requests.delete(url, headers=headers, json=data)
```

### Focus NFSe
```python
url = f"https://api.focusnfe.com.br/v2/nfse/{referencia}"
data = {"justificativa": "Nota emitida incorretamente"}
response = requests.delete(url, auth=auth, json=data)
```

## 📧 Reenvio de Email

### PlugNotas
```python
# Verificar documentação (não implementado no exemplo)
```

### Focus NFSe
```python
url = f"https://api.focusnfe.com.br/v2/nfse/{referencia}/email"
data = {"emails": ["cliente@email.com"]}
response = requests.post(url, auth=auth, json=data)
```

## 🌐 Ambientes

### PlugNotas
- **Sandbox:** `https://api.sandbox.plugnotas.com.br/nfse`
- **Produção:** `https://api.plugnotas.com.br/nfse`
- **API Key Sandbox:** `2da392a6-79d2-4304-a8b7-959572c7e44d` (pública)

### Focus NFSe
- **Homologação:** `https://homologacao.focusnfe.com.br`
- **Produção:** `https://api.focusnfe.com.br`
- **Token:** Gerado individualmente no painel web

## 🎭 Vantagens e Desvantagens

### PlugNotas

**Vantagens:**
- ✅ Sandbox completo e funcional
- ✅ Cadastro de empresa via API
- ✅ ID automático (não precisa gerenciar)
- ✅ API key pública para testes

**Desvantagens:**
- ❌ Precisa armazenar o ID retornado
- ❌ Formato JSON com camelCase

### Focus NFSe

**Vantagens:**
- ✅ Referência controlada por você (mais fácil de gerenciar)
- ✅ Formato JSON com snake_case (padrão Python)
- ✅ Mais endpoints de consulta

**Desvantagens:**
- ❌ Cadastro de empresa via painel web em homologação
- ❌ Precisa gerenciar referências únicas
- ❌ Ambiente de homologação limitado

## 💡 Recomendações

### Use PlugNotas se:
- Você precisa de um ambiente de sandbox completo
- Prefere não gerenciar IDs de notas
- Quer testar rapidamente sem configurações complexas

### Use Focus NFSe se:
- Você já tem integração com outros produtos Focus
- Prefere ter controle total sobre identificadores
- Está OK em cadastrar empresas via painel web
- Trabalha principalmente em produção

## 🔧 Migração de PlugNotas para Focus NFSe

Se você já usa PlugNotas e quer migrar para Focus NFSe:

1. **Mapeamento de Campos:**
   - `cpfCnpj` → `cnpj` ou `cpf`
   - `razaoSocial` → `razao_social`
   - `codigo` → `item_lista_servico`

2. **Sistema de IDs:**
   - Crie uma função para gerar referências únicas
   - Armazene o mapeamento ID_PlugNotas ↔ Referencia_Focus

3. **Autenticação:**
   - Substitua headers por HTTPBasicAuth

4. **Cadastro de Empresas:**
   - Cadastre via painel web do Focus NFSe
   - Envie o certificado digital

5. **Testes:**
   - Teste todas as funcionalidades em homologação
   - Valide os PDFs e XMLs gerados

## 📞 Suporte

- **PlugNotas:** https://plugnotas.com.br/suporte
- **Focus NFSe:** suporte@focusnfe.com.br

