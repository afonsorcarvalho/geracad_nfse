import requests

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import date, datetime, timedelta
import logging
import base64
import re
_logger = logging.getLogger(__name__)


# produção
url = "https://api.plugnotas.com.br/nfse" 
api_key = 'd17733293ad43d4054204a1d73a811a6' # valendo

# sandbox
#url = "https://api.sandbox.plugnotas.com.br/nfse" 
#api_key = '2da392a6-79d2-4304-a8b7-959572c7e44d'# sandbox
content_type = "application/json"


class GeracadNfse(models.Model):
    _name = "geracad.nfse"

    _description = "Gerar NFS-e via PlugNotas"

    
    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        
    )
    plugnotas_id = fields.Char(string='ID Plugnotas',copy=False)
    name = fields.Char("Número da NFS-e", copy=False)
    state = fields.Selection(
        [('draft', 'Rascunho'),('vigente', 'Vigente'), ('enviada', 'Enviada'), ('erro', 'Erro'),('em_processamento',"Em Processamento"), ('concluida','Emitida')],
        string="Status", default='draft', tracking=True,copy=False
    )
    nfse_emitida = fields.Boolean("NFSe emitida")
    nfse_protocolo = fields.Char()
    nfse_descricao_nota = fields.Text("Descrição da Nota")
    nfse_serviço = fields.Many2one(
         "geracad.nfse.servico",
        string='Serviço',
        )
    nfse_descricao_servico =  fields.Char(string='Descrição do Serviço')
    nfse_CNAE =  fields.Char(string='CNAE')
    nfse_pdf = fields.Binary()
    nfse_xml = fields.Binary()
    # nfse_id = fields.Many2one(
    #     'geracad.nfse',
    #     string='NFSe',
    #     )
    valor_servico = fields.Float("Valor do Serviço", required=True)
    cliente_id = fields.Many2one('res.partner', string="Sacado", required=True)
    aluno_id = fields.Many2one('res.partner', string="Aluno" )
    codigo_servico = fields.Char()
    data_emissao = fields.Date("Data de Emissão", readonly=True,copy=False)
    data_autorizacao = fields.Date("Data de autorizacao", readonly=True,copy=False)
    resposta_api_ids = fields.One2many('geracad.nfse.resposta', 'nfse_id', string="Respostas da API")
    description = fields.Char()

    def unlink(self):
        for rec in self:
            if rec.state in ['concluida', 'em_processamento','enviada']:
                raise UserError(
                    _('Não é possível excluir NFSe %s.') % (
                    rec.state,))
            
        return super(GeracadNfse, self).unlink()
    
    def action_get_nfse(self,id="",):
      
        
        payload=[
               
            ]
        self.envia_plugnotas(payload,id='6702f13a72ffd16e793bae6d',tipo="GET")

    def action_gerar_nfse(self):
        for rec in self:
          
            payload = [{
                #"idIntegracao": str(rec.id),
                
                "prestador": {
                    "cpfCnpj": re.sub(r'\D', '', rec.company_id.l10n_br_cnpj_cpf), #cnpj
                    
                },
                "tomador": {
                    "cpfCnpj": re.sub(r'\D', '',rec.cliente_id.l10n_br_cnpj_cpf),
                    "razaoSocial": rec.cliente_id.name,
                    #"email": rec.cliente_id.email,
                    "endereco":{
                        "bairro": rec.cliente_id.l10n_br_district,
                        "cep": re.sub(r'\D', '',rec.cliente_id.zip),
                        "estado": rec.cliente_id.state_id.code,
                        "logradouro": rec.cliente_id.street,
                        "numero": rec.cliente_id.l10n_br_number,
                        "descricaoCidade": rec.cliente_id.city_id.name,
                        "codigoCidade":  rec.cliente_id.state_id.l10n_br_ibge_code+rec.cliente_id.city_id.l10n_br_ibge_code,
                        
                    }

                },
                "descricao": rec.nfse_descricao_nota,
                "servico":{
                    "codigo": rec.nfse_serviço.codigo,
                    "descricaoLC116": rec.nfse_serviço.name,
                    "discriminacao": rec.nfse_descricao_servico,
                    "cnae": rec.nfse_CNAE,
             #       "codigoTributacao": "4115200",
             #       "codigoCidadeIncidencia": "2111300",
                    "descricaoCidadeIncidencia": "São Luís",
                    "iss": {
                        "aliquota": 5,
                        "tipoTributacao": 6
                    },
                    "valor": {
                        "servico": rec.valor_servico
                    }
                },
               
               
            }]
            _logger.info(payload)
            self.envia_plugnotas(payload)

    def get_nfse_plugnotas(self, nfse_id):
        headers = {
                "Content-Type": content_type,
                "x-api-key": api_key 
            }
        response = requests.get(url+"/"+nfse_id, headers=headers)
        return response.status_code, response.json()
    
    def get_consulta_nfse_plugnotas(self,id=False):
        id = id if id else self.plugnotas_id
        headers = {
                "Content-Type": content_type,
                "x-api-key": api_key 
            }
        response = requests.get(url+"/consultar/"+str(id),headers=headers)
        response_data = response.json()
        _logger.info(response.status_code)
        _logger.info(response_data)
        if response.status_code == [400,404] :
            erro = response_data.get('error')
            message = erro.get('message')
            self.write({
                'resposta_api_ids':[(0,0,
                    {
                        'state': 'erro',
                        'resposta':message, 
                        'data_resposta': fields.Datetime.now()
                    }
                )]
            })
        else:
            
            #pegando pdf
            content = 'application/pdf'
            headers = {
                "Content-Type": 'application/pdf',
                "x-api-key": api_key 
            }      
            for resp in response_data:
                if resp.get('situacao') == 'PROCESSANDO':
                    self.write({
                        
                        
                        'resposta_api_ids':[(0,0,
                            {
                                'state': 'processando',
                                'resposta':resp.get('mensagem'), 
                                'data_resposta': fields.Datetime.now()
                            }
                        )]
                })
                if resp.get('situacao') == 'REJEITADO':
                    self.write({
                        
                       
                        
                       
                        'resposta_api_ids':[(0,0,
                            {
                                'state': 'erro',
                                'resposta':resp.get('mensagem'), 
                                'data_resposta': fields.Datetime.now()
                            }
                        )]
                })
                if resp.get('situacao') == 'CONCLUIDO':

                    response_pdf = requests.get(resp.get('pdf'), headers=headers,stream=True)      
                    content = 'application/xml'
                    headers = {
                        "Content-Type": content,
                        "x-api-key": api_key 
                    }      
                    response_xml = requests.get(resp.get('xml'), headers=headers,stream=True) 
                    self.write({
                        'name':resp.get('numeroNfse'),
                        'nfse_protocolo':resp.get('protocoloPrefeitura'),
                        'nfse_pdf': base64.b64encode(response_pdf.content),
                        'nfse_xml': base64.b64encode(response_xml.content),
                        'data_emissao': datetime.strptime(resp.get('emissao'),'%d/%m/%Y'),
                        'state':'concluida',
                        'resposta_api_ids':[(0,0,
                            {
                                'state': 'sucesso',
                                'resposta':resp, 
                                'data_resposta': fields.Datetime.now()
                            }
                        )]
                    })


        return response.status_code, response.json()

    
    def get_pdf_nfse_plugnotas(self, nfse_id):
        headers = {
                "Content-Type": "application/pdf",
                "x-api-key": api_key 
            }

        response = requests.get(url+"/pdf/"+nfse_id, header=headers)
        return response
    
    def envia_plugnotas(self,payload,tipo='POST',id=""):
            headers = {
                "Content-Type": content_type,
                "x-api-key": api_key 
            }
            try:
                if tipo == 'POST':
                    response = requests.post(url, json=payload, headers=headers)
                if tipo == 'GET':
                    response = requests.get(url=url+"/"+id,  headers=headers)
              #  response.raise_for_status()
                response_data = response.json()
                _logger.info(response_data)
                resposta_status = 'sucesso' if response_data.get('sucesso') else 'erro'
                resposta = response_data.get('message', str(response_data))
                if response.status_code == 200 :

                    documents = response_data.get('documents')
                    for doc in documents:
                        self.write({
                            'plugnotas_id': doc.get('id'),
                            'state': 'em_processamento',
                            'data_emissao': fields.Datetime.now(),
                            'resposta_api_ids':[(0,0,
                                {
                                'state': 'sucesso',
                                'resposta': response_data.get('message'), 
                                'data_resposta': fields.Datetime.now()
                                }
                            )
                            ]
                        })
                else:
                    _logger.info('ERRO NO REGISTRO DA NFSE ')
                    erro = response_data.get('error')
                    message = erro.get('message')
                    self.write({
                            'resposta_api_ids':[(0,0,
                                {
                                'state': 'erro',
                                'resposta':message, 
                                'data_resposta': fields.Datetime.now()
                                }
                            )
                            ]
                        })
                    self.state = 'erro'
                    
            except requests.exceptions.RequestException as e:
                _logger.error("Erro ao comunicar com a API Tecnospeed: %s", e)
                self.env['geracad.nfse.resposta'].create({
                    'nfse_id': self.id,
                    'resposta': str(e),
                    'state': 'erro'
                })
                self.write({'state': 'erro'})
                raise UserError(_("Erro ao comunicar com a API Tecnospeed: %s") % str(e))
            
            
class GeracadNFSEResposta(models.Model):
    _name = "geracad.nfse.resposta"
    _description = "Respostas da API para NFS-e"

    nfse_id = fields.Many2one('geracad.curso.nfse', string="NFS-e", required=True, ondelete='cascade')
    data_resposta = fields.Datetime("Data da Resposta", default=fields.Datetime.now)
    resposta = fields.Text("Resposta da API")
    state = fields.Selection(
        [('sucesso', 'Sucesso'), ('erro', 'Erro'),('processando', 'Processando')],
        string="Status"
    )
class GeracadNFSEServico(models.Model):
    _name = "geracad.nfse.servico"
    _description = "Servico API para NFS-e"

    
    codigo = fields.Char("Codigo serviço")
    name = fields.Char("Nome")
   
   