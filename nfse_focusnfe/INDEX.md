# 📚 Índice - Integração Focus NFSe

## 📂 Estrutura de Arquivos

```
nfse_focusnfe/
├── __init__.py              # Módulo Python
├── pyfocusnfse.py          # Biblioteca principal da API
├── exemplo_oficial.py      # Exemplo seguindo 100% a documentação oficial
├── teste_debug.py          # Script de teste com debug ativado
├── README.md               # Documentação completa
├── GUIA_RAPIDO.md          # Guia para resolver erros 404 e 422
├── DEBUG.md                # Como usar o modo debug
├── COMPARACAO_APIS.md      # PlugNotas vs Focus NFSe
└── INDEX.md                # Este arquivo
```

## 🎯 Por Onde Começar?

### 1. Se você está com ERRO 404 ou 422
👉 **Leia:** [`GUIA_RAPIDO.md`](GUIA_RAPIDO.md)
- Solução passo a passo
- Como cadastrar empresa via painel web
- Checklist antes de emitir NFSe

### 2. Se você quer DOCUMENTAÇÃO COMPLETA
👉 **Leia:** [`README.md`](README.md)
- Como usar a biblioteca
- Todos os métodos disponíveis
- Exemplos de código
- Resolução de problemas

### 3. Se você usa PLUGNOTAS e quer COMPARAR
👉 **Leia:** [`COMPARACAO_APIS.md`](COMPARACAO_APIS.md)
- Diferenças entre as APIs
- Mapeamento de campos
- Vantagens e desvantagens
- Como migrar

### 4. Se você quer DEBUGAR e ver o que está sendo enviado
👉 **Leia:** [`DEBUG.md`](DEBUG.md)
- Como ativar o modo debug
- O que é mostrado
- Como interpretar os resultados
- Script de teste pronto: `teste_debug.py`

### 5. Se você quer VER O CÓDIGO
👉 **Leia:** [`pyfocusnfse.py`](pyfocusnfse.py)
- Código fonte comentado
- Exemplos de uso no final do arquivo

## 🧪 Testando Rapidamente

### Opção A: Teste com Debug (Recomendado)
```bash
cd /home/afonso/docker/odoo_geracad/addons/geracad_nfse/nfse_focusnfe
python teste_debug.py
```

Este script mostra **tudo** o que está sendo enviado e recebido da API!

### Opção B: Exemplo Oficial
```bash
python exemplo_oficial.py
```

### Opção C: Script Principal
```bash
python pyfocusnfse.py
```

## 🚀 Início Rápido (5 minutos)

### Passo 1: Importe a biblioteca
```python
from nfse_focusnfe import FocusNFSeAPI

# Ou importe diretamente
from nfse_focusnfe.pyfocusnfse import FocusNFSeAPI
```

### Passo 2: Cadastre sua empresa
⚠️ **IMPORTANTE:** Cadastre via painel web primeiro!
1. Acesse: https://homologacao.focusnfe.com.br
2. Cadastre a empresa
3. Envie o certificado digital (.pfx)

### Passo 3: Use a API
```python
# Inicializar
api = FocusNFSeAPI(
    api_token="seu_token_aqui",
    homologacao=True
)

# Emitir NFSe
data_nfse = {
    "data_emissao": "2025-10-20T10:00:00",
    "prestador": {
        "cnpj": "05108721000133",
        "inscricao_municipal": "48779000",
        "codigo_municipio": "2111300"
    },
    "tomador": {
        "cnpj": "12345678901234",
        "razao_social": "CLIENTE TESTE",
        "email": "cliente@teste.com.br",
        "endereco": {
            "logradouro": "Rua Teste",
            "numero": "123",
            "bairro": "Centro",
            "codigo_municipio": "2111300",
            "uf": "MA",
            "cep": "65000000"
        }
    },
    "servico": {
        "aliquota": 5.00,
        "discriminacao": "Serviço de teste",
        "iss_retido": "false",
        "item_lista_servico": "01.01",
        "valor_servicos": 100.00,
        "valor_iss": 5.00,
        "valor_liquido": 95.00,
    }
}

# Enviar
referencia = "NOTA_001"
status, response = api.send_nfse(referencia, data_nfse)
print(f"Status: {status}")
print(f"Response: {response}")

# Consultar
status, nfse = api.get_nfse(referencia)
print(f"NFSe: {nfse}")

# Baixar PDF
status, pdf = api.get_pdf_nfse(referencia, "nota.pdf")
print(f"PDF salvo: nota.pdf")
```

## 🆘 Problemas Comuns

| Erro | Arquivo de Ajuda | Ação Rápida |
|------|------------------|-------------|
| 404: "Endpoint não encontrado" | [`GUIA_RAPIDO.md`](GUIA_RAPIDO.md) | Cadastre via painel web |
| 422: "CNPJ não autorizado" | [`GUIA_RAPIDO.md`](GUIA_RAPIDO.md) | Cadastre empresa + certificado |
| 400: "Dados inválidos" | [`DEBUG.md`](DEBUG.md) | Use `debug=True` para ver JSON |
| 401: "Não autorizado" | [`README.md`](README.md#resolucao-de-problemas) | Verifique o token |
| Não sei o que está errado | [`DEBUG.md`](DEBUG.md) | Execute `teste_debug.py` |
| Diferenças com PlugNotas | [`COMPARACAO_APIS.md`](COMPARACAO_APIS.md) | Compare as APIs |

## 📋 Métodos Disponíveis

### NFSe
- `send_nfse(referencia, data)` - Enviar NFSe
- `get_nfse(referencia)` - Consultar NFSe
- `get_pdf_nfse(referencia, arquivo)` - Baixar PDF
- `cancel_nfse(referencia, justificativa)` - Cancelar NFSe
- `resend_email(referencia, emails)` - Reenviar email

### Empresas (Disponível em Produção)
- `create_empresa(data)` - Cadastrar empresa
- `get_empresa(cnpj)` - Consultar empresa
- `update_empresa(cnpj, data)` - Atualizar empresa
- `delete_empresa(cnpj)` - Excluir empresa
- `list_empresas()` - Listar empresas

## 🔗 Links Úteis

- **Painel Web Homologação:** https://homologacao.focusnfe.com.br
- **Painel Web Produção:** https://app.focusnfe.com.br
- **Documentação Oficial:** https://focusnfe.com.br/doc/?python#nfse
- **Suporte:** suporte@focusnfe.com.br
- **Telefone:** (41) 3508-2525

## 📞 Precisa de Ajuda?

1. **Leia os guias** (começe pelo GUIA_RAPIDO.md)
2. **Verifique os exemplos** no final do pyfocusnfse.py
3. **Consulte a documentação oficial** do Focus NFSe
4. **Entre em contato com o suporte** se persistir o problema

## ✅ Checklist de Implementação

- [ ] Li o GUIA_RAPIDO.md
- [ ] Cadastrei a empresa via painel web
- [ ] Enviei o certificado digital
- [ ] Habilitei NFSe para a empresa
- [ ] Testei a emissão de uma nota
- [ ] Consegui baixar o PDF
- [ ] Entendi o sistema de referências
- [ ] Li a COMPARACAO_APIS.md (se vim do PlugNotas)

## 🎯 Próximos Passos

1. **Desenvolvimento:**
   - Integre a biblioteca no seu sistema Odoo
   - Crie uma model para armazenar as referências
   - Implemente tratamento de erros adequado

2. **Testes:**
   - Teste todas as funcionalidades em homologação
   - Valide os XMLs e PDFs gerados
   - Teste cenários de erro

3. **Produção:**
   - Cadastre as empresas reais
   - Configure os certificados de produção
   - Migre o token para produção
   - Monitore as primeiras emissões

## 📝 Notas Importantes

⚠️ **ATENÇÃO:**
- O endpoint `/v2/empresas` NÃO funciona em homologação
- Certificado digital deve ser enviado via painel web
- Referências devem ser únicas (não reutilize)
- Aguarde alguns minutos após cadastrar a empresa

✅ **BOAS PRÁTICAS:**
- Use referências significativas (ex: PEDIDO_12345)
- Armazene as referências no banco de dados
- Implemente retry para erros temporários
- Valide os dados antes de enviar
- Mantenha backup dos XMLs retornados

---

**Versão:** 1.0.0  
**Autor:** Netcom Treinamentos e Soluções Tecnológicas  
**Data:** Outubro 2025

