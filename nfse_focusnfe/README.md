# Integração Focus NFSe - Python

Biblioteca Python para integração com a API Focus NFSe.

## 📋 Documentação Oficial

https://focusnfe.com.br/doc/?python#nfse

## 🚀 Como Usar

### 1. Instalação de Dependências

```bash
pip install requests
```

### 2. Inicialização

```python
from pyfocusnfse import FocusNFSeAPI

# Ambiente de homologação
api = FocusNFSeAPI(api_token="seu_token_aqui", homologacao=True)

# Ambiente de produção
api = FocusNFSeAPI(api_token="seu_token_aqui", homologacao=False)
```

## ⚠️ IMPORTANTE: Cadastrar Empresa ANTES de Emitir Notas

**O erro "CNPJ do emitente não autorizado" ocorre porque a empresa não está cadastrada na API.**

### 🔴 ATENÇÃO: Cadastro em Homologação

O endpoint de empresas (`/v2/empresas`) pode **não estar disponível no ambiente de homologação**. Se você receber erro 404 ao tentar listar ou cadastrar empresas, siga estas alternativas:

#### Opção 1: Cadastrar via Painel Web (Recomendado para Homologação)

1. Acesse: https://homologacao.focusnfe.com.br
2. Faça login com suas credenciais
3. Cadastre a empresa pelo painel
4. Faça upload do certificado digital (arquivo .pfx)

#### Opção 2: Usar API de Produção

O endpoint de empresas pode estar disponível apenas em produção:

```python
api = FocusNFSeAPI(api_token="seu_token", homologacao=False)
```

#### Opção 3: Cadastrar via API (se disponível)

```python
# Dados da empresa
data_empresa = {
    "nome": "NETCOM TREINAMENTOS E SOLUCOES TECNOLOGICAS LTDA",
    "nome_fantasia": "NETCOM",
    "email": "financeiro@netcom-ma.com.br",
    "cnpj": "05108721000133",
    "inscricao_municipal": "48779000",
    "inscricao_estadual": "",
    "regime_tributario": "3",  # 1=Simples Nacional, 2=Simples Excesso, 3=Regime Normal
    "cep": "65066190",
    "logradouro": "Rua Boa Esperanca",
    "numero": "102",
    "complemento": "Sala 01",
    "bairro": "Turu",
    "codigo_municipio": "2111300",  # Código IBGE
    "municipio": "São Luis",
    "uf": "MA",
    "telefone": "9898159969",
    "habilita_nfse": True,  # IMPORTANTE: habilitar NFSe
}

# Cadastrar
status, response = api.create_empresa(data_empresa)
print(f"Status: {status}")
print(f"Response: {response}")
```

### PASSO 2: Verificar se a Empresa foi Cadastrada

```python
# Listar todas as empresas
status, empresas = api.list_empresas()
if status == 200:
    print(empresas)
elif status == 404:
    print("Endpoint não disponível. Cadastre via painel web.")

# OU consultar uma empresa específica
status, empresa = api.get_empresa("05108721000133")
print(empresa)
```

### PASSO 3: Emitir a NFSe

```python
# Dados da nota
data_nfse = {
    "data_emissao": "2025-10-20T10:00:00",
    "prestador": {
        "cnpj": "05108721000133",
        "inscricao_municipal": "48779000",
        "codigo_municipio": "4115200"
    },
    "tomador": {
        "cnpj": "79159001372",
        "razao_social": "NOME DO CLIENTE",
        "email": "cliente@email.com.br",
        "endereco": {
            "logradouro": "Rua Boa Esperanca",
            "numero": "102",
            "complemento": "sala 01",
            "bairro": "Turu",
            "codigo_municipio": "2111300",
            "uf": "MA",
            "cep": "65066190"
        }
    },
    "servico": {
        "aliquota": 5.00,
        "discriminacao": "EDUCACAO PROFISSIONAL DE NIVEL TECNICO",
        "iss_retido": "false",
        "item_lista_servico": "08.01",
        "codigo_tributario_municipio": "4115200",
        "valor_servicos": 1.00,
        "valor_deducoes": 0.00,
        "valor_iss": 0.05,
        "valor_liquido": 0.95,
        "codigo_cnae": "8541400"
    }
}

# Enviar nota (referencia é um ID único controlado por você)
referencia = "NFSE_2025_001"
status, response = api.send_nfse(referencia, data_nfse)
print(f"Status: {status}")
print(f"Response: {response}")
```

## 📚 Métodos Disponíveis

### Gerenciamento de Empresas

| Método | Descrição |
|--------|-----------|
| `create_empresa(cnpj, data)` | Cadastra uma nova empresa |
| `get_empresa(cnpj)` | Consulta uma empresa |
| `update_empresa(cnpj, data)` | Atualiza dados da empresa |
| `delete_empresa(cnpj)` | Remove uma empresa |
| `list_empresas()` | Lista todas as empresas |

### Emissão de NFSe

| Método | Descrição |
|--------|-----------|
| `send_nfse(referencia, data)` | Envia NFSe para autorização |
| `get_nfse(referencia)` | Consulta NFSe pela referência |
| `get_pdf_nfse(referencia, arquivo)` | Baixa PDF da NFSe |
| `cancel_nfse(referencia, justificativa)` | Cancela uma NFSe |
| `resend_email(referencia, emails)` | Reenvia email da NFSe |

## 🔑 Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | Sucesso (consultas) |
| 201 | Criado com sucesso |
| 204 | Sucesso sem conteúdo |
| 400 | Requisição inválida |
| 401 | Não autenticado |
| 404 | Não encontrado |
| 422 | Erro de validação (ex: CNPJ não autorizado) |

## 🎯 Resolução de Problemas

### Erro 404: "Endpoint não encontrado" ao listar empresas

**Causa:** O endpoint `/v2/empresas` não está disponível no ambiente de homologação.

**Soluções:**
1. **Cadastre via Painel Web** (Recomendado):
   - Acesse: https://homologacao.focusnfe.com.br
   - Faça login e cadastre a empresa manualmente
   - Faça upload do certificado digital (.pfx)
   
2. **Use o ambiente de produção**:
   ```python
   api = FocusNFSeAPI(api_token="seu_token", homologacao=False)
   ```

3. **Entre em contato com o suporte** do Focus NFSe para confirmar disponibilidade do endpoint

### Erro 422: "CNPJ do emitente não autorizado"

**Causa:** A empresa não está cadastrada na API ou o certificado digital não foi enviado.

**Soluções:**
1. Cadastre a empresa via painel web (homologação) ou API (produção)
2. Certifique-se de que o certificado digital (.pfx) foi enviado e está válido
3. Aguarde alguns minutos após o cadastro para a empresa ser habilitada
4. Verifique se `habilita_nfse: true` foi configurado

### Erro 401: "Não autorizado"

**Causa:** Token de autenticação inválido ou expirado.

**Solução:** 
- Verifique se o token está correto
- Gere um novo token no painel do Focus NFSe se necessário

### Erro 404: "Não encontrado" ao consultar NFSe

**Causa:** A referência da nota não existe ou está incorreta.

**Solução:** 
- Verifique se a referência usada está correta
- Confirme se a nota foi realmente enviada com sucesso

## 📞 Suporte

Para dúvidas sobre a API, consulte:
- Documentação: https://focusnfe.com.br/doc/?python#nfse
- Suporte: suporte@focusnfe.com.br

## 🔐 Ambientes

### Homologação
- URL: `https://homologacao.focusnfe.com.br`
- Use para testes antes de ir para produção
- **Limitação:** Endpoint de empresas pode não estar disponível
- **Solução:** Cadastre empresas via painel web

### Produção
- URL: `https://api.focusnfe.com.br`
- Use apenas com dados reais e validados
- Todos os endpoints disponíveis

## 📜 Certificado Digital

**MUITO IMPORTANTE:** Para emitir NFSe, você PRECISA de um certificado digital válido (e-CPF ou e-CNPJ).

### Como Enviar o Certificado

O certificado digital **NÃO pode ser enviado via API**. Você deve:

1. Acessar o painel web do Focus NFSe:
   - Homologação: https://homologacao.focusnfe.com.br
   - Produção: https://app.focusnfe.com.br

2. Fazer login com suas credenciais

3. Ir na seção "Empresas" ou "Certificados"

4. Fazer upload do arquivo `.pfx` (certificado digital)

5. Informar a senha do certificado

6. Aguardar a validação (pode levar alguns minutos)

### Certificado de Homologação

Para ambiente de teste, você pode:
- Usar um certificado de homologação fornecido pela Receita Federal
- Usar seu certificado real (mas apenas para testes)
- Solicitar ao Focus NFSe um certificado de testes

