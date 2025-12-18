# 🔧 Troubleshooting - ISS Digital São Luís

## ❌ Erro: "Erro de validação do XSD: null"

Este é um erro genérico retornado pelo webservice quando o XML não passa na validação do schema XSD.

### Causas Possíveis:

#### 1. **Contribuinte NÃO Credenciado** ⚠️ (Mais Provável)
**Código de Erro:** 1430  
**Mensagem:** "Contribuinte não credenciado. Faça o credenciamento no site da NFSe."

**Solução:**
- Acesse o site de homologação: `http://beta.stm.semfaz.saoluis.ma.gov.br/`
- OU site de produção: `http://stm.semfaz.saoluis.ma.gov.br/`
- Faça o credenciamento para o Regime Especial de entrega em lote
- Configure o CPF/CNPJ do responsável legal
- Autorize sub-usuários se necessário

**Conforme manual (linha 18):**
> "O contribuinte que esta no Regime Especial de entrega em lote deve se credenciar no site da NFSe para liberar a entrega em lote através do Web Service da prefeitura."

**Conforme manual (linha 2180-2181):**
> "Contribuinte não credenciado para o método de integração com a NFSe utilizado. O contribuinte de estar credenciado para emitir nota pelo regime especial."

#### 2. **CPF/CNPJ Sem Permissão** 
**Código de Erro:** 1103  
**Mensagem:** "O CPF/CNPJ do Remetente não possui permissão para o serviço solicitado."

**Solução:**
- Verifique se o CNPJ do remetente está correto
- Verifique se o certificado digital contém o CNPJ correto
- Verifique se o CPF/CNPJ está credenciado no ambiente correto (homologação vs produção)

#### 3. **Prestador Não Encontrado**
**Código de Erro:** 1202  
**Mensagem:** "Prestador de Serviços não encontrado no Cadastro Municipal (CCM)."

**Solução:**
- Verifique a Inscrição Municipal do prestador
- Verifique se está credenciado no ambiente correto
- Formato: 11 dígitos com zeros à esquerda (ex: "00048779000")

#### 4. **Erro na Assinatura Digital**
**Códigos de Erro:** 1050-1057, 1405, 1428  

**Solução:**
- Verifique se o certificado digital está válido
- Verifique se o certificado contém o CNPJ correto
- Em homologação, certificado é opcional (conforme manual linha 70)
- Em produção, certificado é OBRIGATÓRIO

#### 5. **Estrutura XML Incorreta**

**Solução:**
- Verifique se todos os campos obrigatórios estão preenchidos
- Verifique os formatos:
  - Inscrição Municipal: 11 dígitos
  - CPF: 11 dígitos
  - CNPJ: 14 dígitos
  - CEP: 8 dígitos sem hífen
  - Datas: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS
  - Código SIAFI: "0921" para São Luís

---

## 📋 Checklist de Verificação

Antes de enviar RPS, verifique:

- [ ] Prestador está credenciado no site da NFS-e
- [ ] Ambiente correto (homologação vs produção)
- [ ] CNPJ e Inscrição Municipal corretos
- [ ] Certificado digital válido (se produção)
- [ ] Código da atividade (CNAE) está vinculado ao prestador
- [ ] Alíquota de ISS está correta para a atividade
- [ ] Série de Prestação = "99" (Modelo único)
- [ ] Série RPS = "NF" (padrão)
- [ ] Dados do tomador completos
- [ ] Email do tomador válido (ou "-" se não tiver)
- [ ] CEP sem hífen

---

## 🔍 Como Debugar

1. **Ative o modo debug:**
```python
status, response = api.enviar_rps(dados_rps, debug=True)
```

2. **Verifique o XML gerado:**
   - Deve estar sem formatação (sem espaços, tabs, quebras de linha entre tags)
   - Deve ter todos os campos obrigatórios

3. **Verifique a resposta do servidor:**
   - Status HTTP 200 = Servidor respondeu
   - Sucesso='true' = Lote aceito
   - Sucesso='N' ou 'false' = Lote rejeitado

4. **Salve o XML para análise:**
```python
xml = api._gerar_xml_rps(dados_rps, lote_id='TESTE', debug=False)
with open('xml_debug.xml', 'w', encoding='utf-8') as f:
    f.write(xml)
```

---

## 🎯 Próximos Passos

1. **Credenciar no ambiente de homologação:**
   - Acesse: `http://beta.stm.semfaz.saoluis.ma.gov.br/`
   - Faça login ou cadastro
   - Habilite entrega em lote via webservice
   - Configure o CPF/CNPJ autorizado

2. **Testar novamente:**
   - Após credenciamento, execute o teste
   - Deve funcionar se todas as informações estiverem corretas

3. **Se persistir o erro:**
   - Entre em contato com o suporte da Prefeitura de São Luís
   - Solicite logs detalhados do erro de validação XSD
   - Verifique se há atualizações no manual/XSD

---

## 📚 Referências

- **Manual oficial:** `manual nfse são luis.txt`
- **Anexo 01:** Códigos de erro (linhas 1846-2305)
- **Anexo 02:** URLs do webservice (linhas 2306-2320)
- **Anexo 03:** Formatação de Inscrição Municipal (linhas 2312-2320)

---

## ⚠️ Observação Important

O erro **"Erro de validação do XSD: null"** geralmente indica que o contribuinte **NÃO está credenciado** no ambiente de homologação/produção.

**Conforme erro 1430 do manual (linha 2180):**
> "Contribuinte não credenciado. Faça o credenciamento no site da NFSe."

**E erro 1433 (linha 2189):**
> "Contribuinte não credenciado para o método de integração com a NFSe utilizado. O contribuinte de estar credenciado para emitir nota pelo regime especial."

