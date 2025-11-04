# 🔍 Modo Debug - Focus NFSe

## O que é o modo Debug?

O modo debug permite visualizar **exatamente** o que está sendo enviado na requisição HTTP para a API do Focus NFSe, incluindo:

- 📍 URL completa
- 📋 Parâmetros (ref)
- 🔑 Token de autenticação (parcialmente oculto)
- 📦 Dados JSON completos
- 📥 Resposta da API com headers e corpo

## Como usar?

### Método 1: Usar o script de teste

```bash
cd /home/afonso/docker/odoo_geracad/addons/geracad_nfse/nfse_focusnfe
python teste_debug.py
```

### Método 2: Na sua aplicação

```python
from pyfocusnfse import FocusNFSeAPI

api = FocusNFSeAPI("seu_token", homologacao=True)

# Adicione debug=True no send_nfse
status, response = api.send_nfse(
    referencia="TESTE_001", 
    data=dados_nfse,
    debug=True  # 👈 ATIVA O DEBUG
)
```

### Método 3: No script principal

Edite o arquivo `pyfocusnfse.py` na linha 371:

```python
# Linha 371 - já está com debug=True
status_code, response_json = focus_api.send_nfse(referencia, data_nfse, debug=True)
```

## O que o Debug mostra?

### 1️⃣ Informações da Requisição

```
============================================================
🔍 DEBUG - ENVIANDO NFSE
============================================================
📍 URL: https://homologacao.focusnfe.com.br/v2/nfse
📋 Parâmetros: {'ref': 'TESTE_001'}
🔑 Token: S0IxodlsyU...Pggc
🔐 Auth: ('S0IxodlsyU...', '')

📦 Dados JSON sendo enviados:
{
  "data_emissao": "2025-10-20T10:00:00",
  "prestador": {
    "cnpj": "05108721000133",
    ...
  }
}
============================================================
```

### 2️⃣ Resposta da API

```
============================================================
📥 RESPOSTA DA API
============================================================
📊 Status Code: 422
📄 Headers da Resposta:
   Content-Type: application/json
   Date: Mon, 20 Oct 2025 13:00:00 GMT
   ...

📝 Corpo da Resposta:
{
  "codigo": "permissao_negada",
  "mensagem": "CNPJ do emitente não autorizado."
}
============================================================
```

## Interpretando os Resultados

### ✅ Status 200/201/202 - Sucesso

A NFSe foi enviada com sucesso. Você pode consultar o status posteriormente.

### ❌ Status 400 - Dados Inválidos

**Problema:** O JSON enviado está com erro de formato ou campos inválidos.

**Solução:** 
1. Verifique no debug o JSON que foi enviado
2. Compare com a documentação oficial
3. Corrija os campos inválidos

### ❌ Status 401 - Não Autorizado

**Problema:** Token de autenticação inválido.

**Solução:**
1. Verifique se o token está correto
2. Gere um novo token no painel do Focus NFSe

### ❌ Status 422 - CNPJ Não Autorizado

**Problema:** A empresa não está cadastrada na API.

**Solução:**
1. Acesse: https://homologacao.focusnfe.com.br
2. Cadastre a empresa manualmente
3. Envie o certificado digital (.pfx)
4. Aguarde a validação

### ❌ Status 404 - Não Encontrado

**Problema:** Endpoint incorreto.

**Solução:**
1. Verifique se a URL está correta
2. Confira se está usando `/v2/nfse` e não `/v2/empresas`

## Exemplo de Saída Completa

```bash
$ python teste_debug.py

🚀 INICIANDO TESTE COM DEBUG ATIVADO

============================================================
🔍 DEBUG - ENVIANDO NFSE
============================================================
📍 URL: https://homologacao.focusnfe.com.br/v2/nfse
📋 Parâmetros: {'ref': 'TESTE_DEBUG_001'}
🔑 Token: S0IxodlsyU...Pggc
🔐 Auth: ('S0IxodlsyU...', '')

📦 Dados JSON sendo enviados:
{
  "data_emissao": "2025-10-20T10:00:00",
  "prestador": {
    "cnpj": "05108721000133",
    "inscricao_municipal": "48779000",
    "codigo_municipio": "2111300"
  },
  "tomador": {
    "cnpj": "79159001372",
    "razao_social": "AFONSO FLÁVIO RIBEIRO DE CARVALHO",
    "email": "afonso@jgma.com.br",
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
    "aliquota": 5.0,
    "discriminacao": "EDUCACAO PROFISSIONAL DE NIVEL TECNICO",
    "iss_retido": "false",
    "item_lista_servico": "08.01",
    "codigo_tributario_municipio": "2111300",
    "valor_servicos": 1.0,
    "valor_deducoes": 0.0,
    "valor_pis": 0.0,
    "valor_cofins": 0.0,
    "valor_inss": 0.0,
    "valor_ir": 0.0,
    "valor_csll": 0.0,
    "valor_iss": 0.05,
    "valor_liquido": 0.95,
    "codigo_cnae": "8541400"
  }
}
============================================================


============================================================
📥 RESPOSTA DA API
============================================================
📊 Status Code: 422
📄 Headers da Resposta:
   Server: nginx
   Date: Mon, 20 Oct 2025 13:00:00 GMT
   Content-Type: application/json; charset=utf-8
   Transfer-Encoding: chunked
   Connection: keep-alive

📝 Corpo da Resposta:
{
  "codigo": "permissao_negada",
  "mensagem": "CNPJ do emitente não autorizado."
}
============================================================


=== Envio de NFSe ===
Status Code: 422
Response: {'codigo': 'permissao_negada', 'mensagem': 'CNPJ do emitente não autorizado.'}

============================================================
✅ RESULTADO FINAL
============================================================
Status HTTP: 422
❌ Erro 422: CNPJ não autorizado. Cadastre a empresa no painel web.

Detalhes: {'codigo': 'permissao_negada', 'mensagem': 'CNPJ do emitente não autorizado.'}
============================================================
```

## Quando Usar Debug?

✅ **Use debug quando:**
- Está testando pela primeira vez
- Recebe erros e não sabe o motivo
- Precisa validar se os dados estão corretos
- Quer entender como a API funciona
- Está fazendo troubleshooting

❌ **Não use debug quando:**
- Em produção (pode expor dados sensíveis)
- Em logs públicos
- Processando muitas notas (muito verboso)

## Desativar Debug

Simples! Basta **não passar** o parâmetro `debug` ou passar `debug=False`:

```python
# Debug desativado (padrão)
status, response = api.send_nfse(referencia, data)

# Debug desativado (explícito)
status, response = api.send_nfse(referencia, data, debug=False)
```

## Dicas

1. **Copie o JSON do debug** e valide em: https://jsonlint.com
2. **Compare com a documentação** oficial do Focus NFSe
3. **Salve o output** do debug para análise posterior
4. **Use em ambiente de teste** primeiro

## Arquivos Relacionados

- `pyfocusnfse.py` - Biblioteca principal com debug
- `teste_debug.py` - Script de teste rápido
- `exemplo_oficial.py` - Exemplo seguindo a documentação oficial
- `GUIA_RAPIDO.md` - Guia para resolver erros comuns

## Suporte

Se mesmo com o debug você não conseguir resolver o problema:

1. Leia o `GUIA_RAPIDO.md`
2. Consulte a documentação: https://focusnfe.com.br/doc/?python#nfse
3. Entre em contato: suporte@focusnfe.com.br

