# 📊 Comparação dos Sistemas de NFSe

## 🎯 Visão Geral

Três sistemas de emissão de NFSe implementados para o módulo `geracad_nfse`:

1. **PlugNotas** - API agregadora multi-municípios
2. **Focus NFSe** - API agregadora multi-municípios  
3. **ISS Digital São Luís** - Sistema específico da Prefeitura de São Luís/MA

## 📋 Tabela Comparativa

| Característica | PlugNotas | Focus NFSe | ISS Digital SLZ |
|----------------|-----------|------------|-----------------|
| **Protocolo** | REST/JSON | REST/JSON | SOAP/XML |
| **Facilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Documentação** | Excelente | Excelente | Básica (XSD) |
| **Municípios** | Múltiplos | Múltiplos | Só São Luís/MA |
| **Autenticação** | API Key header | Basic Auth token | CNPJ + IM no XML |
| **Identificador** | ID automático | Referência livre | RPS sequencial |
| **Sandbox** | ✅ Público | ✅ Público | ⚠️  Limitado |
| **Custo** | 💰 Pago | 💰 Pago | 🆓 Gratuito (direto) |
| **Certificado** | Enviado via painel | Enviado via painel | ✅ Assina no código (A1) |
| **Complexidade** | Baixa | Baixa | Alta (SOAP + Cert) |

## 🔧 Implementações

### 1. PlugNotas

**Arquivos:**
- `nfse_plugnotas/pyplugnotas.py`

**Uso:**
```python
from nfse_plugnotas import PlugNotasAPI

api = PlugNotasAPI(api_key="d17733...", homologation=False)
status, response = api.send_nfse(data)
nfse_id = response[0]["id"]  # ID gerado pela API
```

**Pontos Fortes:**
- ✅ Muito fácil de usar
- ✅ ID gerenciado pela API
- ✅ Sandbox público funcional
- ✅ Suporte a múltiplos municípios

**Pontos Fracos:**
- ❌ Precisa armazenar ID retornado
- ❌ Custo por nota emitida

### 2. Focus NFSe

**Arquivos:**
- `nfse_focusnfe/pyfocusnfse.py`
- `nfse_focusnfe/exemplo_oficial.py`
- `nfse_focusnfe/teste_debug.py`
- `nfse_focusnfe/README.md`
- `nfse_focusnfe/DEBUG.md`
- `nfse_focusnfe/ESTRUTURA_DADOS.md`
- `nfse_focusnfe/GUIA_RAPIDO.md`
- `nfse_focusnfe/COMPARACAO_APIS.md`

**Uso:**
```python
from nfse_focusnfe import FocusNFSeAPI

api = FocusNFSeAPI(homologacao=True)
status, response = api.send_nfse("NOTA_001", data, debug=True)
```

**Pontos Fortes:**
- ✅ Referência controlada por você
- ✅ Documentação excelente
- ✅ Debug detalhado
- ✅ Múltiplos municípios
- ✅ Estrutura de dados clara

**Pontos Fracos:**
- ❌ Empresa deve ser cadastrada via painel web
- ❌ Custo por nota emitida
- ❌ Campos devem estar em ordem exata

### 3. ISS Digital São Luís

**Arquivos:**
- `nfse_issdigital_slz/pyissdigital.py`
- `nfse_issdigital_slz/teste_issdigital.py`
- `nfse_issdigital_slz/README.md`
- `nfse_issdigital_slz/INDEX.md`

**Uso:**
```python
from nfse_issdigital_slz import ISSDigitalSLZ

api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    certificado_pfx="/caminho/certificado.pfx",  # ⚠️ OBRIGATÓRIO
    senha_certificado="SenhaCertificado",         # ⚠️ OBRIGATÓRIO
    homologacao=False
)
status, response = api.enviar_rps(dados_rps, debug=True)
protocolo = response['protocolo']
```

**Pontos Fortes:**
- ✅ Gratuito (direto com prefeitura)
- ✅ Sem intermediários
- ✅ Controle total
- ✅ Assina XML no código (certificado A1)
- ✅ Sem custos mensais

**Pontos Fracos:**
- ❌ Mais complexo (SOAP/XML)
- ❌ Apenas São Luís
- ❌ Documentação limitada
- ❌ Deve gerenciar numeração RPS
- ❌ Sandbox não disponível publicamente
- ❌ **Requer certificado digital A1** (~R$ 200/ano)

## 💰 Custo Comparativo

| Sistema | Custo de Implementação | Custo por Nota | Custo Total (100 notas/mês) |
|---------|------------------------|----------------|------------------------------|
| **PlugNotas** | Baixo | ~R$ 0,25 | ~R$ 25/mês |
| **Focus NFSe** | Baixo | ~R$ 0,35 | ~R$ 35/mês |
| **ISS Digital** | Alto | R$ 0 | R$ 0 |

*Valores aproximados, consulte os fornecedores para valores atualizados.

## 🎯 Quando Usar Cada Um?

### Use PlugNotas se:
- ✅ Quer simplicidade máxima
- ✅ Emite notas em vários municípios
- ✅ Prefere não gerenciar IDs
- ✅ Orçamento permite custos mensais
- ✅ Quer começar rápido

### Use Focus NFSe se:
- ✅ Quer controlar as referências
- ✅ Emite notas em vários municípios
- ✅ Precisa de debug detalhado
- ✅ Quer documentação completa
- ✅ Orçamento permite custos mensais

### Use ISS Digital se:
- ✅ Emite APENAS em São Luís/MA
- ✅ Quer economizar custos
- ✅ Tem conhecimento técnico (SOAP/XML)
- ✅ Pode gerenciar numeração RPS
- ✅ Prefere controle total

## 📊 Estrutura de Dados

### PlugNotas
```python
data = [{
    "prestador": {"cpfCnpj": "..."},
    "tomador": {"cpfCnpj": "...", "razaoSocial": "..."},
    "servico": {"codigo": "0801", "valor": {...}}
}]
```

### Focus NFSe
```python
nfse = {}
nfse["prestador"] = {}
nfse["servico"] = {}
nfse["tomador"] = {}
# Ordem importa!
nfse["data_emissao"] = "..."
nfse["prestador"]["cnpj"] = "..."
```

### ISS Digital
```python
dados_rps = {
    "numero_rps": "1",  # Sequencial!
    "servico": {"valor_servicos": "...", ...},
    "tomador": {"cnpj": "...", ...}
}
```

## 🔄 Fluxo de Emissão

### PlugNotas
```
1. send_nfse(data) → Recebe ID
2. get_nfse(id) → Status/Número NFSe
3. get_pdf_nfse(id) → PDF
```

### Focus NFSe
```
1. send_nfse("REF", data) → Processa
2. get_nfse("REF") → Status/Número NFSe
3. get_pdf_nfse("REF") → PDF
```

### ISS Digital
```
1. enviar_rps(data) → Recebe protocolo
2. consultar_lote(protocolo) → Número NFSe
3. consultar_nfse_por_rps() → Detalhes
```

## 🚀 Facilidade de Implementação

### Ranking (mais fácil → mais difícil):
1. 🥇 **PlugNotas** - Plug & Play, ID automático
2. 🥈 **Focus NFSe** - Simples, mas requer cadastro prévio
3. 🥉 **ISS Digital** - Complexo, SOAP/XML, gerenciar RPS

## 📖 Qualidade da Documentação

### Ranking (melhor → pior):
1. 🥇 **Focus NFSe** - Documentação completa, exemplos, debug
2. 🥈 **PlugNotas** - Boa documentação, exemplos claros
3. 🥉 **ISS Digital** - Apenas XSD, sem exemplos prontos

## 💡 Recomendação por Cenário

### Empresa Pequena (< 50 notas/mês)
**Recomendado:** PlugNotas ou Focus NFSe
- Custo baixo
- Implementação rápida
- Suporte disponível

### Empresa Média (50-500 notas/mês)
**Recomendado:** Focus NFSe
- Custo razoável
- Controle das referências
- Escalável

### Empresa Grande (> 500 notas/mês) em São Luís
**Recomendado:** ISS Digital
- Economia significativa
- Controle total
- Vale o investimento em desenvolvimento

### Multi-município (qualquer porte)
**Recomendado:** PlugNotas ou Focus NFSe
- ISS Digital não atende
- APIs agregadoras facilitam

## 🔐 Segurança

### PlugNotas
- 🔒 API Key no header
- 🔒 HTTPS obrigatório
- 🔒 Token rotacionável

### Focus NFSe
- 🔒 Basic Auth
- 🔒 HTTPS obrigatório
- 🔒 Token por empresa

### ISS Digital
- 🔒 CNPJ/IM no XML
- 🔒 HTTPS obrigatório
- 🔒 Pode assinar digitalmente

## 📞 Suporte

| Sistema | Suporte | Qualidade | Resposta |
|---------|---------|-----------|----------|
| **PlugNotas** | Email/Chat | ⭐⭐⭐⭐⭐ | Rápido |
| **Focus NFSe** | Email/Telefone | ⭐⭐⭐⭐⭐ | Rápido |
| **ISS Digital** | SEMFAZ | ⭐⭐⭐ | Lento |

## 🎓 Curva de Aprendizado

```
Tempo para implementar e dominar:

PlugNotas:    ████░░░░░░ (4 horas)
Focus NFSe:   ██████░░░░ (6 horas)
ISS Digital:  ██████████ (16 horas)
```

## 📦 Arquivos do Projeto

```
geracad_nfse/
├── nfse_plugnotas/
│   └── pyplugnotas.py
│
├── nfse_focusnfe/
│   ├── pyfocusnfse.py
│   ├── exemplo_oficial.py
│   ├── teste_debug.py
│   ├── README.md
│   ├── DEBUG.md
│   ├── ESTRUTURA_DADOS.md
│   ├── GUIA_RAPIDO.md
│   ├── COMPARACAO_APIS.md
│   └── INDEX.md
│
├── nfse_issdigital_slz/
│   ├── pyissdigital.py
│   ├── teste_issdigital.py
│   ├── README.md
│   └── INDEX.md
│
└── COMPARACAO_SISTEMAS.md (este arquivo)
```

## ✅ Checklist de Decisão

**Responda estas perguntas:**

- [ ] Emito notas em quantos municípios?
  - Um (São Luís) → Considere ISS Digital
  - Múltiplos → PlugNotas ou Focus NFSe

- [ ] Quantas notas por mês?
  - < 50 → Qualquer um
  - 50-500 → Focus NFSe
  - > 500 em SLZ → ISS Digital

- [ ] Tenho conhecimento técnico?
  - Básico → PlugNotas
  - Intermediário → Focus NFSe
  - Avançado → Qualquer um

- [ ] Orçamento para NFSe?
  - Limitado → ISS Digital (se SLZ)
  - Moderado → PlugNotas ou Focus
  - Flexível → Qualquer um

- [ ] Prioridade?
  - Rapidez → PlugNotas
  - Controle → Focus NFSe
  - Economia → ISS Digital

## 🎯 Conclusão

**Não existe "melhor" absoluto!** A escolha depende de:
- Volume de notas
- Municípios atendidos
- Orçamento disponível
- Conhecimento técnico
- Prioridades (rapidez vs economia vs controle)

**Nossa recomendação geral:**
1. **Comece com Focus NFSe** - Bom equilíbrio entre facilidade e controle
2. **Se precisa de mais simplicidade** - Migre para PlugNotas
3. **Se crescer muito em SLZ** - Migre para ISS Digital

---

**Versão:** 1.0.0  
**Data:** Outubro 2025  
**Autor:** Netcom Treinamentos e Soluções Tecnológicas

