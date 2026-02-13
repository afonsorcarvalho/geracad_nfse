# 📋 Estrutura de Dados da NFSe - Focus NFSe

## ⚠️ IMPORTANTE: Ordem dos Campos

A API do Focus NFSe converte os dados JSON em XML, e **a ordem dos campos importa**!

Se você receber um erro como:
```
"Element 'X': This element is not expected. Expected is ( Y )."
```

Significa que os campos estão **fora de ordem** ou **faltando campos obrigatórios**.

## ✅ Estrutura Correta (Testada e Validada)

```python
data_nfse = {
    # === DADOS GERAIS DA NOTA ===
    "data_emissao": "2025-10-20T12:00:00-03:00",  # Obrigatório: Data/hora com timezone
    "incentivador_cultural": "false",              # String "true" ou "false"
    "natureza_operacao": "1",                      # 1=Tributação no município
    "optante_simples_nacional": "true",            # String "true" ou "false"
    "status": "1",                                 # 1=Normal
    
    # === PRESTADOR (VOCÊ - SUA EMPRESA) ===
    "prestador": {
        "cnpj": "05108721000133",                  # Obrigatório: CNPJ da sua empresa
        "inscricao_municipal": "48779000",         # Obrigatório: Inscrição municipal
        "codigo_municipio": "2111300"              # Obrigatório: Código IBGE do município
    },
    
    # === SERVIÇO ===
    "servico": {
        "aliquota": "5.00",                        # Obrigatório: Alíquota do ISS (string)
        "base_calculo": "1.00",                    # Base de cálculo
        "discriminacao": "Descrição do serviço",   # Obrigatório: Descrição detalhada
        "iss_retido": "false",                     # String "true" ou "false"
        "item_lista_servico": "08.01",            # Obrigatório: Código do serviço LC 116
        "valor_iss": "0.05",                      # Valor do ISS (string)
        "valor_liquido": "0.95",                  # Valor líquido (string)
        "valor_servicos": "1.00",                 # Obrigatório: Valor total (string)
        "codigo_cnae": "8541400"                  # Código CNAE
    },
    
    # === TOMADOR (CLIENTE) ===
    "tomador": {
        "cnpj": "79159001372000",                 # CNPJ do cliente (ou "cpf")
        "razao_social": "NOME DO CLIENTE",        # Obrigatório: Razão social/Nome
        "email": "cliente@email.com.br",          # Email para envio da nota
        "endereco": {
            "bairro": "Bairro",                   # Obrigatório
            "cep": "65066-190",                   # CEP formatado
            "codigo_municipio": "2111300",        # Código IBGE
            "logradouro": "Rua Exemplo",          # Obrigatório
            "numero": "102",                      # Número
            "complemento": "sala 01",             # Opcional
            "uf": "MA"                            # Obrigatório: UF (2 letras)
        }
    }
}
```

## 🔴 Campos Obrigatórios

### Nível Principal
- ✅ `data_emissao`

### Prestador
- ✅ `cnpj`
- ✅ `inscricao_municipal`
- ✅ `codigo_municipio`

### Serviço
- ✅ `aliquota`
- ✅ `discriminacao`
- ✅ `item_lista_servico`
- ✅ `valor_servicos`

### Tomador
- ✅ `cnpj` ou `cpf`
- ✅ `razao_social`
- ✅ `endereco.logradouro`
- ✅ `endereco.numero`
- ✅ `endereco.bairro`
- ✅ `endereco.codigo_municipio`
- ✅ `endereco.uf`

## 📝 Tipos de Dados

### Valores Numéricos
**SEMPRE use strings!** Não use float ou int.

```python
# ❌ ERRADO
"aliquota": 5.00

# ✅ CORRETO
"aliquota": "5.00"
```

### Booleanos
**SEMPRE use strings!** "true" ou "false" (minúsculas).

```python
# ❌ ERRADO
"iss_retido": False

# ✅ CORRETO
"iss_retido": "false"
```

### Data/Hora
Use o formato ISO 8601 com timezone:

```python
# ✅ CORRETO
"data_emissao": "2025-10-20T12:00:00-03:00"
```

### CEP
Pode ser com ou sem hífen:

```python
# ✅ Ambos funcionam
"cep": "65066-190"
"cep": "65066190"
```

## 🗂️ Códigos Importantes

### Natureza de Operação
- `1` = Tributação no município
- `2` = Tributação fora do município
- `3` = Isenção
- `4` = Imune
- `5` = Exigibilidade suspensa por decisão judicial
- `6` = Exigibilidade suspensa por procedimento administrativo

### Status
- `1` = Normal
- `2` = Cancelado

### Item Lista Serviço (LC 116/2003)
Exemplos:
- `01.01` = Análise e desenvolvimento de sistemas
- `08.01` = Ensino regular
- `08.02` = Instrução, treinamento, orientação pedagógica
- `17.05` = Reparação, conservação e reforma de edifícios

**Consulte a lista completa da LC 116/2003!**

## ❌ Erros Comuns

### 1. "Expected is ( RazaoSocialTomador )"
**Causa:** Campo `razao_social` faltando ou fora de ordem.

**Solução:**
```python
"tomador": {
    "cnpj": "...",
    "razao_social": "NOME CLIENTE",  # Deve vir logo após cnpj/cpf
    "email": "...",
    # ...
}
```

### 2. Valores numéricos como number
**Causa:** Enviou `"aliquota": 5.00` em vez de `"aliquota": "5.00"`

**Solução:** Sempre use strings para números:
```python
"servico": {
    "aliquota": "5.00",  # String, não float
    "valor_servicos": "1.00"  # String, não int
}
```

### 3. Booleanos como boolean
**Causa:** Enviou `"iss_retido": false` em vez de `"iss_retido": "false"`

**Solução:**
```python
"iss_retido": "false",  # String "true" ou "false"
```

### 4. CNPJ/CPF incompleto
**Causa:** CPF sem zeros à esquerda ou CNPJ curto.

**Solução:**
```python
# CPF: sempre 11 dígitos
"cpf": "79159001372"  # ✅

# CNPJ: sempre 14 dígitos  
"cnpj": "05108721000133"  # ✅
```

## 🔧 Validação dos Dados

Antes de enviar, verifique:

```python
# 1. Todos os campos obrigatórios estão presentes?
assert "data_emissao" in data_nfse
assert "prestador" in data_nfse
assert "cnpj" in data_nfse["prestador"]
assert "razao_social" in data_nfse["tomador"]

# 2. Valores são strings?
assert isinstance(data_nfse["servico"]["aliquota"], str)
assert isinstance(data_nfse["servico"]["valor_servicos"], str)

# 3. Booleanos são strings?
assert data_nfse["servico"]["iss_retido"] in ["true", "false"]

# 4. CNPJ tem 14 dígitos?
assert len(data_nfse["prestador"]["cnpj"]) == 14
```

## 📚 Campos Opcionais Úteis

```python
# Informações adicionais do serviço
"servico": {
    "codigo_tributario_municipio": "...",  # Código específico do município
    "valor_deducoes": "0.00",              # Deduções
    "valor_pis": "0.00",                   # PIS
    "valor_cofins": "0.00",                # COFINS
    "valor_inss": "0.00",                  # INSS
    "valor_ir": "0.00",                    # IR
    "valor_csll": "0.00",                  # CSLL
    # ...
}

# Informações adicionais do tomador
"tomador": {
    "telefone": {
        "ddd": "98",
        "numero": "981599692"
    },
    # ...
}
```

## 🧪 Testando

Use o modo debug para ver exatamente o que está sendo enviado:

```python
from pyfocusnfse import FocusNFSeAPI

api = FocusNFSeAPI("seu_token", homologacao=True)
status, response = api.send_nfse("REF_001", data_nfse, debug=True)
```

Ou execute:
```bash
python teste_debug.py
```

## 📖 Referências

- Documentação oficial: https://focusnfe.com.br/doc/?python#nfse
- Exemplo oficial: `exemplo_oficial.py`
- Script de teste: `teste_debug.py`
- Lista de serviços LC 116: http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp116.htm

## 💡 Dicas Finais

1. **Sempre copie a estrutura do `exemplo_oficial.py`** como base
2. **Use o modo debug** para ver erros detalhados
3. **Não invente campos** - use apenas os documentados
4. **Mantenha a ordem** dos campos conforme o exemplo
5. **Valide os dados** antes de enviar
6. **Teste em homologação** primeiro

