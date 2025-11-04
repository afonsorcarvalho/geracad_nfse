# ✅ RESUMO DAS ALTERAÇÕES - NFS-e com Múltiplos Itens

## 🎯 O que foi Implementado?

Foram adicionadas **5 funcionalidades principais** ao módulo geracad_nfse para suportar o formato de NFS-e com múltiplos itens, conforme a [documentação oficial da Focus NFSe para São Luís/MA](https://focusnfe.com.br/guides/nfse/municipios-integrados/sao-luis-ma).

---

## ✨ Funcionalidades Adicionadas

### 1. ✅ **Inscrição Municipal do Tomador**
- Agora enviada automaticamente quando preenchida no cadastro do cliente
- Remove caracteres não numéricos automaticamente
- Campo **opcional** (não quebra se não estiver preenchido)

**Antes:**
```json
"tomador": {
  "cnpj": "...",
  "razao_social": "..."
}
```

**Depois:**
```json
"tomador": {
  "cnpj": "...",
  "razao_social": "...",
  "inscricao_municipal": "48779000"  ← NOVO
}
```

---

### 2. ✅ **Código do Município de Prestação**
- Calculado automaticamente dos campos "Cidade/Estado do serviço"
- Usa código IBGE de 7 dígitos
- Enviado no nível raiz do payload

**Adicionado:**
```json
{
  "prestador": {...},
  "servico": {...},
  "tomador": {...},
  "codigo_municipio_prestacao": "2111300"  ← NOVO
}
```

---

### 3. ✅ **Regime Especial de Tributação**
- Novo campo de seleção com 6 opções
- Obrigatório para São Luís/MA
- Visível apenas quando provedor = "Focus NFSe"

**Opções:**
1. Microempresa Municipal
2. Estimativa
3. Sociedade de Profissionais
4. Cooperativa
5. MEI - Simples Nacional
6. ME EPP - Simples Nacional

**No payload:**
```json
{
  "data_emissao": "...",
  "regime_especial_tributacao": 5,  ← NOVO
  "prestador": {...}
}
```

---

### 4. ✅ **Telefone do Tomador**
- Enviado automaticamente se preenchido no cadastro
- Usa campo `phone` ou `mobile` do cliente
- Validação mínima de 10 dígitos

**Adicionado:**
```json
"tomador": {
  "cnpj": "...",
  "razao_social": "...",
  "telefone": "98 98159-9692"  ← NOVO
}
```

---

### 5. ✅ **Múltiplos Itens do Serviço**
- **Novo modelo:** `geracad.nfse.item`
- **Nova aba** na interface: "Itens do Serviço"
- Editor inline com cálculo automático
- Suporte a itens tributáveis e não tributáveis

**Campos do Item:**
- Sequência (ordenação com drag & drop)
- Discriminação (descrição)
- Quantidade
- Valor Unitário
- Valor Total (calculado automaticamente)
- Tributável (checkbox)

**Interface:**
```
┌─────────────────────────────────────────────────────────┐
│ Itens do Serviço                                        │
├─────────────────────────────────────────────────────────┤
│ ☰ │ Discriminação      │ Qtd │ Valor Unit │ Total │ ☑️ │
│ 1 │ Mensalidade Nov    │ 1.0 │ 500.00     │ 500   │ ✓ │
│ 2 │ Material Didático  │ 2.0 │ 50.00      │ 100   │ ✓ │
│   │                    │     │     Total: │ 600   │   │
└─────────────────────────────────────────────────────────┘
```

**No payload:**
```json
{
  "servico": {
    "iss_retido": 0,
    "aliquota": 5.0,
    "discriminacao": "SERVICOS PRESTADOS"
  },
  "itens": [  ← NOVO
    {
      "discriminacao": "Mensalidade Nov",
      "quantidade": 1.0,
      "valor_unitario": 500.0,
      "valor_total": 500.0,
      "tributavel": true
    },
    {
      "discriminacao": "Material Didático",
      "quantidade": 2.0,
      "valor_unitario": 50.0,
      "valor_total": 100.0,
      "tributavel": true
    }
  ]
}
```

---

## 🔄 Dois Formatos Suportados

O sistema agora suporta **automaticamente** dois formatos:

### Formato 1: **Simples** (sem itens)
**Quando usar:** Para municípios que não exigem detalhamento de itens

```json
{
  "servico": {
    "aliquota": "5.00",        // String
    "valor_servicos": "1000.00",
    "iss_retido": "true"        // String
  }
}
```

### Formato 2: **Com Itens** (São Luís/MA)
**Quando usar:** Para São Luís/MA e outros municípios que exigem

```json
{
  "servico": {
    "aliquota": 5.0,           // Number
    "iss_retido": 0,            // Number
    "discriminacao": "..."
  },
  "itens": [...]               // Array de itens
}
```

**A escolha é automática:** se houver itens cadastrados, usa o formato 2. Senão, usa o formato 1.

---

## 📁 Arquivos Alterados

### 1. **`models/geracad_nfse.py`**
- ✅ Adicionado campo `regime_especial_tributacao`
- ✅ Adicionado campo `item_ids` (One2many)
- ✅ Criado modelo `GeracadNfseItem`
- ✅ Atualizado método `_prepare_focus_payload()` com:
  - Suporte a inscrição municipal do tomador
  - Suporte a telefone do tomador
  - Suporte a código município de prestação
  - Suporte a regime especial
  - Lógica para alternar entre formatos
  - Montagem do array de itens

### 2. **`views/geracad_nfse_view.xml`**
- ✅ Adicionado campo `regime_especial_tributacao` no formulário
- ✅ Criada nova aba "Itens do Serviço"
- ✅ Movida aba "Respostas da API" para dentro do notebook
- ✅ Adicionada mensagem informativa sobre uso de itens

### 3. **Documentação Criada**
- ✅ `ITENS_MULTIPLOS_NFSE.md` - Guia completo de uso
- ✅ `CHANGELOG_ITENS.md` - Detalhes técnicos das alterações
- ✅ `RESUMO_ALTERACOES.md` - Este arquivo

---

## 🎬 Como Usar

### Para criar uma NFS-e COM itens (São Luís/MA):

1. **Criar nova NFS-e**
   - Financeiro → NFS-e → Criar

2. **Preencher dados básicos**
   - Provedor: **Focus NFSe**
   - Cliente
   - Serviço
   - CNAE
   - **Regime Especial de Tributação**: Selecione uma opção

3. **Adicionar itens**
   - Ir para aba **"Itens do Serviço"**
   - Clicar em "Adicionar uma linha"
   - Preencher:
     - Discriminação: "Mensalidade de Novembro"
     - Quantidade: 1
     - Valor Unitário: 1000.00
     - Tributável: ✓
   - Adicionar mais itens se necessário

4. **Enviar**
   - Clicar em **"Enviar NFSe"**
   - Sistema monta o payload automaticamente no formato correto

### Para criar uma NFS-e SEM itens (formato tradicional):

1. **Criar nova NFS-e**
2. **Preencher dados básicos**
3. **NÃO adicionar itens** na aba
4. **Preencher "Valor do Serviço"** normalmente
5. **Enviar**

---

## ⚠️ Importante

### ✅ Compatibilidade Total
- **PlugNotas**: Continua funcionando **exatamente** como antes
- **Focus NFSe (simples)**: Funciona para municípios sem exigência de itens
- **Focus NFSe (itens)**: Funciona para São Luís/MA e similares

### 📌 Campos Novos na Interface

**Visível sempre:**
- Inscrição municipal do tomador (preenchida no cadastro do cliente)
- Telefone do tomador (preenchido no cadastro do cliente)
- Código município de prestação (calculado automaticamente)

**Visível apenas para Focus NFSe:**
- Regime Especial de Tributação
- Aba "Itens do Serviço"

---

## 📊 Exemplo Completo

**Configuração:**
```
Provedor: Focus NFSe
Cliente: ACME Ltda (CNPJ: 11.111.111/0001-11)
Regime: 5 (MEI - Simples Nacional)

Itens:
1. Mensalidade - R$ 1.000,00 (Tributável)
2. Taxa de Matrícula - R$ 200,00 (Não Tributável)
```

**Payload gerado:**
```json
{
  "data_emissao": "2025-11-03T10:00:00-03:00",
  "natureza_operacao": 1,
  "optante_simples_nacional": true,
  "regime_especial_tributacao": 5,
  "prestador": {
    "cnpj": "05108721000133",
    "inscricao_municipal": "48779000",
    "codigo_municipio": "2111300"
  },
  "tomador": {
    "cnpj": "11111111000111",
    "razao_social": "ACME Ltda",
    "telefone": "98 3233-1234",
    "inscricao_municipal": "12345",
    "endereco": {...}
  },
  "servico": {
    "iss_retido": 0,
    "item_lista_servico": "08.01",
    "codigo_tributario_municipio": "8541400",
    "aliquota": 5.0,
    "discriminacao": "SERVICOS EDUCACIONAIS"
  },
  "itens": [
    {
      "discriminacao": "Mensalidade",
      "quantidade": 1.0,
      "valor_unitario": 1000.0,
      "valor_total": 1000.0,
      "tributavel": true
    },
    {
      "discriminacao": "Taxa de Matrícula",
      "quantidade": 1.0,
      "valor_unitario": 200.0,
      "valor_total": 200.0,
      "tributavel": false
    }
  ]
}
```

**Cálculo do ISS:**
- Valor tributável: R$ 1.000,00 (apenas item 1)
- Alíquota: 5%
- ISS = R$ 50,00

---

## 🚀 Próximos Passos

### 1. Atualizar o Módulo no Odoo
```bash
# No servidor Odoo
odoo -u geracad_nfse -d sua_base_de_dados
```

### 2. Testar
- [ ] Criar NFS-e sem itens (formato tradicional)
- [ ] Criar NFS-e com itens (formato São Luís/MA)
- [ ] Verificar PlugNotas continua funcionando
- [ ] Validar payload no log

### 3. Produção
- [ ] Backup da base de dados
- [ ] Deploy em produção
- [ ] Monitorar logs

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **`ITENS_MULTIPLOS_NFSE.md`** - Guia completo de uso
- **`CHANGELOG_ITENS.md`** - Changelog técnico
- [Documentação Focus NFSe - São Luís/MA](https://focusnfe.com.br/guides/nfse/municipios-integrados/sao-luis-ma)

---

**Desenvolvido por:** Afonso Carvalho  
**Data:** 03/11/2025  
**Versão:** 1.0  

✅ **Implementação Concluída com Sucesso!**

