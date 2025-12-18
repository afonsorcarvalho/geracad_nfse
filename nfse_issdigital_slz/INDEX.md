# 📚 Índice - ISS Digital São Luís

## 📂 Estrutura de Arquivos

```
nfse_issdigital_slz/
├── __init__.py                 # Módulo Python
├── pyissdigital.py             # Biblioteca principal (WebService SOAP)
├── teste_issdigital.py         # Script de teste completo
├── verificar_certificado.py    # ✅ Script para validar certificado digital
├── requirements.txt            # Dependências Python
├── README.md                   # Documentação completa
├── CERTIFICADO_DIGITAL.md      # Guia completo sobre certificado digital
└── INDEX.md                    # Este arquivo
```

## 🎯 Por Onde Começar?

### 1. Se você quer ENTENDER o sistema
👉 **Leia:** [`README.md`](README.md)
- Como usar a biblioteca
- Estrutura de dados
- Campos obrigatórios
- Exemplos de código

### 2. Se você quer TESTAR rapidamente
👉 **Execute:** `teste_issdigital.py`
```bash
cd /home/afonso/docker/odoo_geracad/addons/geracad_nfse/nfse_issdigital_slz
python teste_issdigital.py
```

### 3. Se você precisa VERIFICAR seu CERTIFICADO DIGITAL
👉 **Execute:** `verificar_certificado.py`
```bash
python verificar_certificado.py
```
- ✅ Valida se o certificado está correto
- 📅 Verifica prazo de validade
- 🔑 Testa senha
- 📋 Mostra informações do titular

### 4. Se você precisa configurar CERTIFICADO DIGITAL
👉 **Leia:** [`CERTIFICADO_DIGITAL.md`](CERTIFICADO_DIGITAL.md)
- **OBRIGATÓRIO** para produção!
- Como obter certificado A1
- Como configurar no código
- Verificação e troubleshooting

### 5. Se você quer VER O CÓDIGO
👉 **Leia:** [`pyissdigital.py`](pyissdigital.py)
- Código fonte documentado
- Geração de XML SOAP
- Assinatura digital
- Parse de respostas
- Exemplos no final do arquivo

## 🚀 Início Rápido (5 minutos)

### Passo 1: Importe a biblioteca
```python
from nfse_issdigital_slz import ISSDigitalSLZ
```

### Passo 2: Configure (COM Certificado Digital)
```python
api = ISSDigitalSLZ(
    inscricao_prestador="48779000",
    cnpj_prestador="05108721000133",
    certificado_pfx="/caminho/para/certificado.pfx",  # ⚠️ OBRIGATÓRIO
    senha_certificado="SenhaDoCertificado",            # ⚠️ OBRIGATÓRIO
    homologacao=False
)
```

**⚠️ IMPORTANTE:** O certificado digital A1 é **OBRIGATÓRIO** para produção!  
Veja [`CERTIFICADO_DIGITAL.md`](CERTIFICADO_DIGITAL.md) para mais detalhes.

### Passo 3: Envie um RPS
```python
dados_rps = {
    "numero_rps": "1",
    "serie_rps": "1",
    "servico": {
        "valor_servicos": "100.00",
        "aliquota": "5.00",
        "item_lista_servico": "0801",
        "discriminacao": "Serviço de ensino"
    },
    "tomador": {
        "cnpj": "12345678000195",
        "razao_social": "Cliente Exemplo",
        "endereco": {
            "logradouro": "Rua Exemplo",
            "numero": "123",
            "bairro": "Centro",
            "codigo_municipio": "2111300",
            "uf": "MA",
            "cep": "65000000"
        }
    }
}

status, response = api.enviar_rps(dados_rps, debug=True)
```

## 📋 Métodos Disponíveis

| Método | Descrição |
|--------|-----------|
| `enviar_rps(dados, debug=False)` | Envia RPS para gerar NFSe |
| `consultar_lote(protocolo, debug=False)` | Consulta resultado do lote |
| `consultar_nfse_por_rps(numero, serie, tipo, debug=False)` | Consulta NFSe pelo RPS |

## 🔗 Diferenças entre APIs

| Aspecto | Focus NFSe | ISS Digital SLZ |
|---------|------------|-----------------|
| **Protocolo** | REST/JSON | SOAP/XML |
| **Autenticação** | Token via Basic Auth | CNPJ + Inscrição no XML |
| **Formato** | JSON | XML |
| **Envio** | Individual por nota | Lote de RPS |
| **Identificador** | Referência livre | Número RPS sequencial |

## 🆘 Problemas Comuns

| Erro | Possível Causa | Solução |
|------|----------------|---------|
| Timeout | Webservice lento/fora | Tente novamente |
| Prestador não encontrado | CNPJ/IM incorretos | Verifique cadastro SEMFAZ |
| RPS já utilizado | Número duplicado | Use sequência única |
| Serviço não encontrado | Código inválido | Veja LC 116/2003 |

## 📖 Documentação Técnica

### XSD de Produção

Baixe os schemas XML em:
https://www.semfaz.saoluis.ma.gov.br/fckeditor/userfiles/xsd_producao.rar

Contém:
- `ConsultaSeqRps.xsd` - Consulta sequencial de RPS
- `ReqCancelamentoNFSe.xsd` - Cancelamento de NFSe
- `ReqConsultaLote.xsd` - Consulta de lote
- `ReqConsultaNFSeRPS.xsd` - Consulta NFSe por RPS
- Arquivos XML de retorno

### URLs do WebService

**Produção:**
- WSDL: `https://www.semfaz.saoluis.ma.gov.br/nfse/NfseService.svc?wsdl`
- Endpoint: `https://www.semfaz.saoluis.ma.gov.br/nfse/NfseService.svc`

**Homologação:**
- WSDL: `https://www.semfaz.saoluis.ma.gov.br/nfse_homologacao/NfseService.svc?wsdl`
- Endpoint: `https://www.semfaz.saoluis.ma.gov.br/nfse_homologacao/NfseService.svc`

## 🎯 Fluxo de Emissão

```
1. Preparar dados do RPS
         ↓
2. api.enviar_rps(dados) → Recebe protocolo
         ↓
3. api.consultar_lote(protocolo) → Recebe número NFSe
         ↓
4. Guardar número e código de verificação
```

## 📊 Códigos Importantes

### Tipo de RPS
- `1` = RPS (padrão)
- `2` = Nota Fiscal Conjugada
- `3` = Cupom

### ISS Retido
- `1` = Sim (retido na fonte)
- `2` = Não (recolhido pelo prestador)

### Natureza da Operação
- `1` = Tributação no município
- `2` = Tributação fora do município
- `3` = Isenção
- `4` = Imune
- `5` = Exigibilidade suspensa por decisão judicial
- `6` = Exigibilidade suspensa por procedimento administrativo

### Item Lista de Serviço (LC 116)
Exemplos para educação:
- `0801` - Ensino regular pré-escolar, fundamental, médio e superior
- `0802` - Instrução, treinamento, orientação pedagógica

[Consulte a lista completa](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp116.htm)

## 🧪 Testando

### Teste Completo
```bash
python teste_issdigital.py
```

### Teste Individual (no arquivo principal)
```bash
python pyissdigital.py
```

## 💡 Dicas Importantes

1. **Numeração de RPS**
   - Deve ser sequencial
   - Sem "buracos" na numeração
   - Controle no seu sistema

2. **Código do Município**
   - São Luís: `2111300` (IBGE)
   - Use para serviços em SLZ

3. **Certificado Digital**
   - Pode ser necessário
   - Assinar XML antes de enviar
   - Consulte SEMFAZ

4. **Modo Debug**
   - Use `debug=True` para ver XMLs
   - Ajuda na resolução de problemas
   - Não use em produção

## 🔧 Integração com Odoo

Para integrar com o módulo Odoo `geracad_nfse`:

```python
# No modelo Odoo
from odoo.addons.geracad_nfse.nfse_issdigital_slz import ISSDigitalSLZ

class GeracadNfse(models.Model):
    _name = "geracad.nfse"
    
    def enviar_issdigital(self):
        api = ISSDigitalSLZ(
            inscricao_prestador=self.company_id.inscricao_municipal,
            cnpj_prestador=self.company_id.cnpj,
            homologacao=False
        )
        
        dados_rps = self._preparar_dados_rps()
        status, response = api.enviar_rps(dados_rps)
        
        if 'protocolo' in response:
            self.protocolo_issdigital = response['protocolo']
            # Consultar depois...
```

## 📞 Suporte

- **SEMFAZ São Luís:** https://www.semfaz.saoluis.ma.gov.br/
- **Telefone:** (98) 3214-8900
- **Email:** Consulte no portal da SEMFAZ

## 🔗 Links Úteis

- [Portal SEMFAZ São Luís](https://www.semfaz.saoluis.ma.gov.br/)
- [LC 116/2003 - Lista de Serviços](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp116.htm)
- [Códigos IBGE](https://www.ibge.gov.br/explica/codigos-dos-municipios.php)
- [CNAE](https://cnae.ibge.gov.br/)

## ✅ Checklist de Implementação

- [ ] Li o README.md
- [ ] Configurei CNPJ e Inscrição Municipal
- [ ] Testei com teste_issdigital.py
- [ ] Entendi o fluxo de envio → protocolo → consulta
- [ ] Implementei controle de numeração de RPS
- [ ] Testei envio de RPS
- [ ] Testei consulta de lote
- [ ] Guardei número da NFSe e código de verificação
- [ ] Implementei tratamento de erros

## 🎓 Comparação com Focus NFSe

Se você já usa Focus NFSe e quer entender as diferenças:

| Característica | Focus NFSe | ISS Digital |
|----------------|------------|-------------|
| Facilidade | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Documentação | Excelente | Básica (XSD) |
| Controle | API gerencia | Você gerencia RPS |
| Flexibilidade | Referência livre | RPS sequencial |
| Formato | JSON (simples) | XML SOAP (complexo) |
| Uso | Múltiplos municípios | Só São Luís |

**Recomendação:**
- Use **Focus NFSe** se possível (mais simples)
- Use **ISS Digital** se obrigatório pela prefeitura

---

**Versão:** 1.0.0  
**Autor:** Netcom Treinamentos e Soluções Tecnológicas  
**Data:** Outubro 2025  
**Baseado em:** XSD Produção SEMFAZ São Luís

