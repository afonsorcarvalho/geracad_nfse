# 📦 Suporte a Múltiplos Itens na NFS-e

## 📋 Visão Geral

O módulo **geracad_nfse** agora suporta o envio de NFS-e com múltiplos itens detalhados, conforme exigência de municípios como **São Luís/MA**.

Esta funcionalidade está disponível apenas para o provedor **Focus NFSe** e segue a [documentação oficial da Focus NFSe para São Luís/MA](https://focusnfe.com.br/guides/nfse/municipios-integrados/sao-luis-ma).

## 🆕 Novos Campos Adicionados

### 1. Regime Especial de Tributação

Campo opcional que permite selecionar o regime especial de tributação:

- **1** - Microempresa Municipal
- **2** - Estimativa
- **3** - Sociedade de Profissionais
- **4** - Cooperativa
- **5** - MEI - Simples Nacional
- **6** - ME EPP - Simples Nacional

**Obrigatório para:** São Luís/MA e outros municípios que exigem este campo.

### 2. Inscrição Municipal do Tomador

Agora o sistema envia automaticamente a inscrição municipal do tomador quando este campo estiver preenchido no cadastro do cliente (`res.partner`).

**Campo:** `l10n_br_inscr_mun` no cadastro do cliente.

### 3. Telefone do Tomador

O sistema envia automaticamente o telefone do tomador quando disponível nos campos `phone` ou `mobile` do cadastro do cliente.

### 4. Código do Município de Prestação

Quando os campos "Cidade do serviço" e "Estado do serviço" estiverem preenchidos, o sistema adiciona automaticamente o código IBGE do município de prestação no payload.

### 5. Itens do Serviço (One2many)

Novo modelo `geracad.nfse.item` que permite cadastrar múltiplos itens para a NFS-e.

**Campos do item:**
- **Sequência**: Ordem de exibição
- **Discriminação**: Descrição detalhada do item (obrigatório)
- **Quantidade**: Quantidade do item (padrão: 1.0)
- **Valor Unitário**: Preço unitário do item
- **Valor Total**: Calculado automaticamente (quantidade × valor unitário)
- **Tributável**: Se o item é tributável ou não (padrão: Sim)

## 🚀 Como Usar

### Formato Simples (Sem Itens)

Se você **não cadastrar itens**, a NFS-e será enviada no formato tradicional:

```json
{
  "data_emissao": "2025-11-03T10:00:00",
  "prestador": { ... },
  "servico": {
    "aliquota": "5.00",
    "valor_servicos": "1000.00",
    "discriminacao": "Serviços prestados",
    ...
  },
  "tomador": { ... }
}
```

### Formato com Múltiplos Itens

Se você **cadastrar itens** na aba "Itens do Serviço", o payload será montado no formato com array de itens:

```json
{
  "data_emissao": "2025-11-03T10:00:00",
  "regime_especial_tributacao": 5,
  "prestador": { ... },
  "servico": {
    "iss_retido": 0,
    "item_lista_servico": "08.01",
    "codigo_tributario_municipio": "8541400",
    "aliquota": 5.0,
    "discriminacao": "SERVICOS PRESTADOS"
  },
  "tomador": {
    "cnpj": "...",
    "razao_social": "...",
    "telefone": "98 98159-9692",
    "inscricao_municipal": "12345",
    ...
  },
  "itens": [
    {
      "discriminacao": "Item 1",
      "quantidade": 1.0,
      "valor_unitario": 500.0,
      "valor_total": 500.0,
      "tributavel": true
    },
    {
      "discriminacao": "Item 2",
      "quantidade": 2.0,
      "valor_unitario": 250.0,
      "valor_total": 500.0,
      "tributavel": true
    }
  ]
}
```

## 📝 Passo a Passo

### 1. Criar uma NFS-e com Itens

1. Acesse: **Financeiro → NFS-e → Notas Fiscais de Serviço**
2. Clique em **Criar**
3. Preencha os dados básicos:
   - Provedor: **Focus NFSe**
   - Cliente (Sacado)
   - Serviço (LC 116)
   - Descrição do Serviço
   - CNAE
   - **Regime Especial de Tributação** (se necessário)
   - Cidade/Estado do serviço
4. Vá para a aba **Itens do Serviço**
5. Adicione os itens clicando em "Adicionar uma linha":
   - Discriminação: "Mensalidade de Novembro"
   - Quantidade: 1
   - Valor Unitário: 1000.00
   - Tributável: ✓ (marcado)
6. Clique em **Enviar NFSe**

### 2. Verificar o Payload Gerado

O sistema gera automaticamente o payload correto baseado na presença ou ausência de itens.

Para debug, você pode verificar os logs do Odoo:
```bash
grep "Payload Focus NFSe preparado" /var/log/odoo/odoo.log
```

## ⚙️ Diferenças Entre os Formatos

| Campo | Formato Simples | Formato com Itens |
|-------|----------------|-------------------|
| `servico.aliquota` | String ("5.00") | Number (5.0) |
| `servico.iss_retido` | String ("true"/"false") | Number (0/1) |
| `servico.valor_servicos` | String ("1000.00") | ❌ Não enviado |
| `servico.valor_iss` | String ("50.00") | ❌ Não enviado |
| `servico.valor_liquido` | String ("950.00") | ❌ Não enviado |
| `tomador.telefone` | ✅ Sempre enviado se disponível | ✅ Sempre enviado se disponível |
| `tomador.inscricao_municipal` | ✅ Sempre enviado se disponível | ✅ Sempre enviado se disponível |
| `itens[]` | ❌ Não enviado | ✅ Array de itens |

## 🎯 Municípios que Exigem Itens

### São Luís/MA
- **Provedor:** DSF
- **Itens:** Obrigatório
- **Regime Especial:** Obrigatório
- **Código Tributário Município:** Obrigatório (versão estendida do CNAE - 9 dígitos)

Consulte a [lista completa de códigos tributários de São Luís/MA](https://focusnfe.com.br/guides/nfse/municipios-integrados/sao-luis-ma).

## 🔧 Modelo de Dados

### geracad.nfse (Principal)
```python
item_ids = fields.One2many('geracad.nfse.item', 'nfse_id')
regime_especial_tributacao = fields.Selection([...])
```

### geracad.nfse.item (Itens)
```python
nfse_id = fields.Many2one('geracad.nfse', required=True, ondelete='cascade')
sequence = fields.Integer(default=10)
discriminacao = fields.Char(required=True)
quantidade = fields.Float(default=1.0)
valor_unitario = fields.Float()
valor_total = fields.Float(compute='_compute_valor_total', store=True)
tributavel = fields.Boolean(default=True)
```

## 📚 Referências

- [Documentação Focus NFSe - São Luís/MA](https://focusnfe.com.br/guides/nfse/municipios-integrados/sao-luis-ma)
- [Exemplo oficial no código](./nfse_focusnfe/exemplo_oficial.py)
- [Estrutura de dados completa](./nfse_focusnfe/ESTRUTURA_DADOS.md)

## ✅ Compatibilidade

Esta implementação é **totalmente compatível** com:
- ✅ PlugNotas (continua funcionando normalmente)
- ✅ Focus NFSe (formato simples)
- ✅ Focus NFSe (formato com itens - São Luís/MA)
- ✅ Outros municípios que não exigem itens

## 🐛 Troubleshooting

### Erro: "Expected is ( RazaoSocialTomador )"
**Solução:** Verifique se o campo `razao_social` está preenchido no cadastro do cliente.

### Erro: Valores não somando corretamente
**Solução:** Verifique se os itens estão marcados como "Tributável" corretamente. Apenas itens tributáveis entram no cálculo do ISS.

### Itens não aparecem na interface
**Solução:** Verifique se o provedor selecionado é "Focus NFSe". A aba de itens só aparece para este provedor.

## 💡 Dicas

1. Use a sequência dos itens para ordenar como deseja que apareçam na nota
2. Marque apenas como "Não Tributável" itens isentos de ISS
3. O valor total é calculado automaticamente, não é necessário preencher
4. Quando houver itens, o campo "Valor do Serviço" principal não é usado no cálculo

---

**Desenvolvido por:** Afonso Carvalho  
**Data:** 03/11/2025  
**Versão:** 1.0

