# 🔔 Webhooks da Focus NFSe

## 📝 Visão Geral

Os webhooks permitem que a Focus NFSe notifique automaticamente o sistema Odoo quando uma NFS-e muda de status, eliminando a necessidade de consultas manuais repetidas.

## 🎯 Funcionamento

### Fluxo Automático

```
1. Odoo envia NFS-e para Focus NFSe
2. Focus processa a nota
3. Focus envia webhook para Odoo ← AUTOMÁTICO
4. Odoo atualiza o registro
5. Odoo consulta e baixa PDF/XML ← AUTOMÁTICO
```

## 🔧 Configuração

### 1. URL do Webhook

A URL do webhook será:
```
https://seu-dominio.com/focusnfe/webhook
```

### 2. Configurar na Focus NFSe

1. Acesse: https://homologacao.acrasnfe.com.br/
2. Vá em **Configurações → Webhooks**
3. Adicione a URL acima
4. Selecione os eventos:
   - ✅ NFS-e Autorizada (`autorizado`)
   - ✅ NFS-e com Erro (`erro_autorizacao`)
   - ✅ NFS-e em Processamento (`processando_autorizacao`)
   - ✅ NFS-e Cancelada (`cancelado`)

### 3. Testar Webhook

Acesse no navegador:
```
https://seu-dominio.com/focusnfe/webhook/test
```

Se ver `{"status": "ok", ...}`, o webhook está funcionando!

## 📦 Payload do Webhook

### Exemplo de Payload (NFS-e Autorizada)

```json
{
  "cnpj": "51916585000125",
  "ref": "12345",
  "status": "autorizado",
  "codigo_verificacao": "ABC123",
  "numero": "123",
  "codigo_cancelamento": null,
  "motivo_cancelamento": null
}
```

### Possíveis Status

| Status | Descrição | Ação do Sistema |
|--------|-----------|-----------------|
| `processando_autorizacao` | NFS-e em processamento | Atualiza status para "Em Processamento" |
| `autorizado` | NFS-e autorizada | Consulta NFS-e e baixa PDF/XML |
| `erro_autorizacao` | Erro na autorização | Registra erro e atualiza status |
| `cancelado` | NFS-e cancelada | Registra cancelamento |

## 🔍 Como o Sistema Processa

### 1. Recepção do Webhook
- Controller: `/focusnfe/webhook`
- Método: `POST`
- Tipo: `JSON`
- Auth: `none` (público)

### 2. Validação
- Verifica se o campo `ref` existe
- Busca a NFS-e pelo `nfse_provider_identifier`
- Valida se é da Focus NFSe

### 3. Processamento

```python
# Baseado no status recebido:

if status == 'autorizado':
    # Atualiza registro
    # Chama action_get_nfse() automaticamente
    # Baixa PDF e XML

elif status == 'erro_autorizacao':
    # Registra erro
    # Atualiza status para 'erro'

elif status == 'processando_autorizacao':
    # Atualiza status para 'em_processamento'
```

### 4. Registro da Resposta
Todas as respostas do webhook são registradas na aba **"Respostas da API"** da NFS-e.

## 🚀 Benefícios

### ✅ Sem Webhooks (Manual)
1. Envia NFS-e
2. Espera alguns minutos
3. Clica em "Consultar NFSe"
4. Baixa PDF/XML manualmente
5. Repete se não estiver pronta

### ✅ Com Webhooks (Automático)
1. Envia NFS-e
2. ☕ Relaxa...
3. Sistema atualiza automaticamente!

## 🔐 Segurança

### Considerações

1. **Endpoint Público**: O webhook não requer autenticação (auth='none')
   - ✅ Necessário para a Focus enviar notificações
   - ✅ Valida o `ref` para garantir que a NFS-e existe
   - ✅ Usa `sudo()` para garantir permissões

2. **CSRF Desabilitado**: csrf=False
   - ✅ Requerido para endpoints de webhook externos

3. **Logs Completos**: Todas as requisições são registradas
   - ✅ Facilita auditoria e troubleshooting

### Recomendações

- Configure firewall para aceitar apenas IPs da Focus NFSe
- Monitore os logs regularmente
- Valide os dados recebidos

## 🧪 Testando

### Teste 1: Endpoint Ativo
```bash
curl https://seu-dominio.com/focusnfe/webhook/test
```

Resposta esperada:
```json
{
  "status": "ok",
  "message": "Webhook da Focus NFSe está funcionando",
  "version": "1.0.0"
}
```

### Teste 2: Simular Webhook (Desenvolvimento)
```bash
curl -X POST https://seu-dominio.com/focusnfe/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "12345",
    "status": "autorizado",
    "numero": "123",
    "codigo_verificacao": "ABC123"
  }'
```

## 📊 Monitoramento

### Verificar Logs

```bash
# No container do Odoo
tail -f /var/log/odoo/odoo.log | grep -i webhook
```

### Exemplos de Logs

```
INFO Webhook recebido da Focus NFSe: {...}
INFO Processando webhook - NFS-e ID: 42, Status: autorizado
INFO NFS-e 42 autorizada. Número: 123
INFO Consultando NFS-e 42 após autorização via webhook
INFO Webhook processado com sucesso para NFS-e 42 (ref: 12345)
```

## 🐛 Troubleshooting

### Problema: Webhook não está sendo recebido

**Soluções:**
1. Verifique se a URL está correta na Focus
2. Teste o endpoint: `/focusnfe/webhook/test`
3. Verifique firewall/proxy
4. Confira os logs do Odoo

### Problema: NFS-e não é encontrada

**Causa:** O campo `ref` não corresponde ao `nfse_provider_identifier`

**Solução:**
- Verifique se o `ref` usado no envio é o mesmo retornado no webhook
- Confira o campo `nfse_provider_identifier` no registro da NFS-e

### Problema: Erro ao consultar NFS-e

**Causa:** Credenciais ou configuração da Focus

**Solução:**
- Verifique as credenciais da Focus NFSe
- Confira se a nota realmente foi autorizada
- Veja os logs para mais detalhes

## 📚 Referências

- **Documentação Focus NFSe**: https://focusnfe.com.br/doc/
- **Controller**: `addons/geracad_nfse/controllers/webhook_controller.py`
- **Configuração no Odoo**: NFS-e → Configuração → Configuração de Webhooks

## 🎓 Suporte

Para dúvidas sobre webhooks:
1. Consulte esta documentação
2. Veja os logs do sistema
3. Contate o suporte da Focus NFSe
4. Entre em contato com a equipe de desenvolvimento

