# 🚀 Guia Rápido - Como Resolver o Erro 422 e 404

## ❌ Erros Comuns

### Erro 404: "Endpoint não encontrado"
```json
{
  "codigo": "nao_encontrado",
  "mensagem": "Endpoint não encontrado, verifique a documentação..."
}
```

### Erro 422: "CNPJ do emitente não autorizado"
```json
{
  "codigo": "permissao_negada",
  "mensagem": "CNPJ do emitente não autorizado."
}
```

## ✅ SOLUÇÃO PASSO A PASSO

### PASSO 1: Entenda o Problema

O ambiente de **homologação** do Focus NFSe tem limitações:
- ❌ Endpoint `/v2/empresas` NÃO está disponível
- ❌ Não dá para cadastrar empresa via API
- ✅ Precisa cadastrar via PAINEL WEB

### PASSO 2: Cadastre a Empresa via Painel Web

#### 2.1 - Acesse o Painel de Homologação
- URL: https://homologacao.focusnfe.com.br
- Faça login com suas credenciais

#### 2.2 - Cadastre a Empresa
1. Vá em **"Empresas"** no menu
2. Clique em **"Adicionar Empresa"**
3. Preencha os dados:
   ```
   CNPJ: 05108721000133
   Razão Social: NETCOM TREINAMENTOS E SOLUCOES TECNOLOGICAS LTDA
   Nome Fantasia: NETCOM
   Inscrição Municipal: 48779000
   Email: financeiro@netcom-ma.com.br
   Telefone: (98) 98159-9692
   CEP: 65066-190
   Endereço: Rua Boa Esperanca, 102, Sala 01, Turu
   Cidade: São Luis - MA
   ```

#### 2.3 - Envie o Certificado Digital
1. Na mesma tela da empresa, localize **"Certificado Digital"**
2. Faça upload do arquivo `.pfx` (certificado e-CNPJ ou e-CPF)
3. Informe a **senha do certificado**
4. Clique em **"Salvar"**
5. **Aguarde a validação** (pode levar alguns minutos)

#### 2.4 - Habilite NFSe
1. Marque a opção **"Habilitar NFSe"**
2. Configure o código do município (se necessário)
3. Salve as alterações

### PASSO 3: Teste a Emissão de NFSe

Agora sim você pode testar a emissão via API:

```python
from pyfocusnfse import FocusNFSeAPI

# Inicializar
api = FocusNFSeAPI("S0IxodlsyUAF5E2bunyvdHZYdUgbPpgc", homologacao=True)

# Dados da nota
data_nfse = {
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
        "codigo_tributario_municipio": "2111300",
        "valor_servicos": 100.00,
        "valor_deducoes": 0.00,
        "valor_iss": 5.00,
        "valor_liquido": 95.00,
        "codigo_cnae": "8541400"
    }
}

# Enviar NFSe
referencia = "TESTE_001"
status, response = api.send_nfse(referencia, data_nfse)
print(f"Status: {status}")
print(f"Response: {response}")

# Consultar NFSe
status, response = api.get_nfse(referencia)
print(f"Status: {status}")
print(f"Response: {response}")

# Baixar PDF
if status == 200:
    status_pdf, pdf = api.get_pdf_nfse(referencia, "nfse_teste.pdf")
    print(f"PDF salvo com status: {status_pdf}")
```

## 📋 Checklist Antes de Emitir

Antes de tentar emitir uma NFSe, verifique:

- [ ] Empresa cadastrada no painel web do Focus NFSe
- [ ] Certificado digital (.pfx) enviado e validado
- [ ] Senha do certificado está correta
- [ ] NFSe está habilitada para a empresa
- [ ] Token de API está correto e ativo
- [ ] Código do município está correto (IBGE)
- [ ] Inscrição municipal está correta
- [ ] Dados do tomador estão completos

## 🔍 Como Verificar se Está Tudo OK

### Via Painel Web
1. Acesse https://homologacao.focusnfe.com.br
2. Vá em "Empresas"
3. Verifique se aparece:
   - ✅ Status: Ativa
   - ✅ Certificado: Válido
   - ✅ NFSe: Habilitado

### Via API Python
```python
# Tente enviar uma nota de teste de R$ 0,10
referencia = f"TESTE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
# ... (use o código acima)
```

## ⚠️ Importante

- **Homologação:** Endpoint de empresas NÃO funciona via API
- **Produção:** Endpoint de empresas pode funcionar via API
- **Certificado:** SEMPRE deve ser enviado via painel web
- **Validação:** Aguarde alguns minutos após cadastrar

## 📞 Precisa de Ajuda?

- Suporte Focus NFSe: suporte@focusnfe.com.br
- Documentação: https://focusnfe.com.br/doc/?python#nfse
- Telefone: (41) 3508-2525

## 🎯 Resumo da Solução

1. ✅ Esqueça a API para cadastrar empresa em homologação
2. ✅ Use o painel web: https://homologacao.focusnfe.com.br
3. ✅ Cadastre a empresa manualmente
4. ✅ Envie o certificado digital (.pfx)
5. ✅ Habilite NFSe para a empresa
6. ✅ Agora sim, use a API para emitir notas!

**Pronto! Agora você pode emitir NFSe sem o erro 422! 🎉**

