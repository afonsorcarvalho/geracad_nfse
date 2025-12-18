# 🔑 Como Obter o TokenEnvio para ISS Digital São Luís

## ⚠️ CAMPO OBRIGATÓRIO

O `<TokenEnvio>` é um campo **obrigatório** para usar o webservice da NFS-e de São Luís.

Conforme o XSD de produção:
```xml
<xs:element name="TokenEnvio" type="tipos:tpTokenEnvioRPS" minOccurs="0" maxOccurs="1">
    <xs:documentation>Token de envio do lote.</xs:documentation>
</xs:element>
```

**Características:**
- Tipo: String
- Tamanho: **32 caracteres exatos**
- Posição: **ANTES** de `<CodCidade>` no cabeçalho

---

## 📋 Como Obter o Token

### 1. Acesse o Site da NFS-e

**Produção:**
```
http://stm.semfaz.saoluis.ma.gov.br/
```

### 2. Faça Login

- Use o CNPJ: `05108721000133`
- Use a senha cadastrada

### 3. Credenciamento para Webservice

1. Acesse menu: **Configurações** ou **Regime Especial**
2. Selecione: **Entrega em Lote via Webservice**
3. Marque a opção de habilitação
4. Aguarde aprovação (se necessário)

### 4. Gere o Token

- Procure opção: **"Token de Integração"** ou **"Chave de Acesso"**
- Clique em **"Gerar Novo Token"** ou **"Visualizar Token"**
- Copie o token de 32 caracteres
- Exemplo: `abcd1234efgh5678ijkl9012mnop3456`

### 5. Configure no Script

```python
api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    razao_social_prestador="NETCOM",
    token_envio="SEU_TOKEN_DE_32_CARACTERES_AQUI",  # ⭐ OBRIGATÓRIO
    certificado_pfx="certificado.pfx",
    senha_certificado="senha",
    homologacao=False
)
```

---

## ⚠️ Importante

1. **O Token é ÚNICO por contribuinte**
   - Cada prestador tem seu próprio token
   - Não compartilhe o token

2. **Token NÃO expira** (geralmente)
   - Uma vez gerado, use sempre o mesmo
   - Só gere novo se perder ou se houver problema

3. **Token é DIFERENTE do certificado**
   - Token: Gerado no site da NFS-e
   - Certificado: Arquivo .pfx da certificadora

4. **Sem Token = Erro de Validação XSD**
   - O erro "Erro de validação do XSD: null" pode indicar falta de token
   - Sem token, o webservice rejeita a requisição

---

## 🔍 Como Saber se o Token Está Correto

1. **Tamanho:** Deve ter exatamente 32 caracteres
2. **Formato:** Geralmente alfanumérico (letras e números)
3. **Teste:** Execute `teste_consulta.py` - se funcionar, o token está correto

---

## 📞 Suporte

Se não encontrar onde gerar o token no site:

1. Entre em contato com SEMFAZ São Luís
2. Telefone/email do suporte técnico
3. Solicite orientação para gerar o "Token de Integração para Webservice"

**Endereço:**
```
Av. Guaxenduba, 1455
Bairro de Fátima
CEP 65060-360
São Luís - MA
```

---

## 📚 Referências

- **XSD:** `xsd_producao/ReqEnvioLoteRPS.xsd` (linha 23)
- **Tipo:** `Tipos.xsd` (linha 237-246)
- **Obrigatório:** Para usar webservice em produção

---

**⭐ IMPORTANTE:** Sem o TokenEnvio correto, o webservice sempre retornará erro de validação!

