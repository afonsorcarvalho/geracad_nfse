import requests
import zipfile
import io

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
import logging
import base64
import re
import json
from urllib.parse import urljoin
from typing import Any, Dict

from odoo.addons.geracad_nfse.nfse_focusnfe import FocusNFSeAPI
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
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Gerar NFS-e via PlugNotas"

    
    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=1,
        tracking=True
    )
    plugnotas_id = fields.Char(string='ID Plugnotas', copy=False)
    nfse_provider = fields.Selection(
        [
            ('plugnotas', 'PlugNotas'),
            ('focusnfe', 'Focus NFSe')
        ],
        string='Provedor NFS-e',
        default='focusnfe',
        required=True,
        tracking=True,
        help='Seleciona o provedor de emissão conforme documentação oficial (PlugNotas ou Focus NFSe).'
    )
    nfse_provider_identifier = fields.Char(
        string='Identificador do Provedor',
        copy=False,
        help='Armazena o identificador externo retornado/gerado pela API escolhida.'
    )
    name = fields.Char("Número da NFS-e", copy=False, tracking=True)
    state = fields.Selection(
        [('draft', 'Rascunho'),('vigente', 'Vigente'), ('enviada', 'Enviada'), ('erro', 'Erro'),('em_processamento',"Em Processamento"), ('concluida','Emitida'), ('cancelada', 'Cancelada')],
        string="Status", default='draft', tracking=True,copy=False
    )
    nfse_emitida = fields.Boolean("NFSe emitida")
    nfse_protocolo = fields.Char(copy=False)
    nfse_descricao_nota = fields.Text("Descrição da Nota")
    nfse_CNAE = fields.Many2one(
        'geracad.nfse.cnae',
        string='CNAE',
        tracking=True,
        help='Código Nacional de Atividades Econômicas'
    )
    nfse_CNAE_codigo = fields.Char(
        string='Código CNAE',
        related='nfse_CNAE.codigo',
        store=True,
        readonly=True
    )
    nfse_serviço = fields.Many2one(
        "geracad.nfse.servico",
        string='Código de Serviço',
        related='nfse_CNAE.servico_id',
        store=True,
        readonly=True,
        help='Código de serviço conforme LC 116/2003, preenchido automaticamente pelo CNAE'
    )
    nfse_servico_codigo = fields.Char(
        string='Código',
        related='nfse_serviço.codigo',
        store=True,
        readonly=True
    )
    nfse_descricao_servico = fields.Char(string='Descrição do Serviço')
    nfse_pdf = fields.Binary(copy=False)
    nfse_pdf_url = fields.Char(copy=False)
    nfse_xml = fields.Binary(copy=False)
    nfse_xml_filename = fields.Char(string='Nome do Arquivo XML', compute='_compute_nfse_xml_filename', store=False)
    nfse_local_estado = fields.Many2one(
        'res.country.state',
        string='Estado',
        domain="[('country_id.code', '=', 'BR')]",
        help='Selecione o estado onde o serviço foi prestado'
    )
    nfse_local_cidade = fields.Many2one(
        'res.city',
        string='Cidade',
        domain="[('state_id', '=', nfse_local_estado)]",
        help='Selecione a cidade onde o serviço foi prestado (filtra pelo estado selecionado)'
    )
    nfse_retido = fields.Boolean("Retido")
    regime_especial_tributacao = fields.Selection(
        [
            ('0', 'Nenhum'),
            ('1', 'Ato Cooperado (Cooperativa)'),
            ('2', 'Estimativa'),
            ('3', 'Microempresa Municipal'),
            ('4', 'Notário ou Registrador'),
            ('5', 'Profissional Autônomo'),
            ('6', 'Sociedade de Profissionais')
        ],
        string='Regime Especial de Tributação',
        default='0',
        help='Tipos de Regimes Especiais de Tributação Municipal'
    )
    # nfse_id = fields.Many2one(
    #     'geracad.nfse',
    #     string='NFSe',
    #     )
    valor_servico = fields.Float("Valor do Serviço", required=True, tracking=True)
    item_ids = fields.One2many(
        'geracad.nfse.item',
        'nfse_id',
        string='Itens do Serviço',
        help='Detalhamento dos itens conforme exigência de municípios como São Luís/MA'
    )
    cliente_id = fields.Many2one('res.partner', string="Sacado", required=True, tracking=True)
    cliente_endereco = fields.Char(related='cliente_id.street')
    cliente_bairro = fields.Char(related='cliente_id.l10n_br_district')
    cliente_cep = fields.Char(related='cliente_id.zip')
    cliente_cidade = fields.Char(related='cliente_id.city_id.name')
    cliente_estado = fields.Char(related='cliente_id.state_id.name')
    aluno_id = fields.Many2one('res.partner', string="Aluno" )
    codigo_servico = fields.Char()
    data_emissao = fields.Date("Data de Emissão", readonly=True, copy=False, tracking=True)
    data_autorizacao = fields.Date("Data de autorizacao", readonly=True, copy=False, tracking=True)
    resposta_api_ids = fields.One2many('geracad.nfse.resposta', 'nfse_id', string="Respostas da API")
    description = fields.Char()

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Preenche automaticamente estado e cidade de prestação com dados do emitente quando empresa é selecionada."""
        if self.company_id and self.company_id.partner_id:
            # Preenche apenas se os campos estiverem vazios
            if not self.nfse_local_estado and self.company_id.partner_id.state_id:
                self.nfse_local_estado = self.company_id.partner_id.state_id
            
            if not self.nfse_local_cidade and self.company_id.partner_id.city_id:
                self.nfse_local_cidade = self.company_id.partner_id.city_id
    
    @api.onchange('nfse_local_estado')
    def _onchange_nfse_local_estado(self):
        """Limpa o campo cidade quando o estado for alterado para evitar inconsistências."""
        if self.nfse_local_estado:
            # Limpa a cidade para forçar o usuário a selecionar novamente
            self.nfse_local_cidade = False
    
    def _preencher_local_prestacao_do_emitente(self):
        """
        Preenche automaticamente o estado e cidade de prestação de serviço
        com os dados do endereço do emitente quando não estiverem preenchidos.
        """
        self.ensure_one()
        
        # Se não tiver estado ou cidade de prestação, usa os dados do emitente
        if not self.nfse_local_estado and self.company_id.partner_id.state_id:
            self.nfse_local_estado = self.company_id.partner_id.state_id
        
        if not self.nfse_local_cidade and self.company_id.partner_id.city_id:
            self.nfse_local_cidade = self.company_id.partner_id.city_id

    def unlink(self):
        """Valida se a NFS-e pode ser excluída baseado no status."""
        for rec in self:
            if rec.state in ['concluida', 'em_processamento', 'enviada']:
                raise UserError(
                    _('Não é possível excluir NFS-e com status "%s". '
                      'Apenas notas em rascunho ou com erro podem ser excluídas.') % rec.state)
            
        return super(GeracadNfse, self).unlink()
    
    @api.depends('nfse_xml', 'name')
    def _compute_nfse_xml_filename(self):
        """
        Gera o nome do arquivo XML para download.
        Formato: geracad.nfse-{numero_nfse}-nfse_xml.xml
        """
        for rec in self:
            if rec.nfse_xml:
                # Gera nome do arquivo: geracad.nfse-{numero_nfse}-nfse_xml.xml
                # Usa o número da NFSe se disponível, senão usa o ID
                numero_nfse = rec.name if rec.name else (rec.id if rec.id else 'temp')
                rec.nfse_xml_filename = f"geracad.nfse-{numero_nfse}-nfse_xml.xml"
            else:
                rec.nfse_xml_filename = False
    
    def action_get_nfse(self, id=""):
        """Consulta a NFSe no provedor configurado utilizando o identificador externo disponível."""
        for rec in self:
            if rec.nfse_provider == 'plugnotas':
                rec._fetch_plugnotas(id)
            elif rec.nfse_provider == 'focusnfe':
                referencia = id or rec.nfse_provider_identifier
                rec._fetch_focus_nfse(referencia)
            else:
                raise UserError(_('Selecione um provedor de NFS-e válido conforme documentação.'))

    def action_download_xml_zip(self):
        """
        Faz download dos XMLs das NFSe selecionadas em um arquivo ZIP.
        Retorna um action para download do arquivo ZIP.
        """
        # Filtra apenas registros que têm XML
        nfse_com_xml = self.filtered(lambda r: r.nfse_xml)
        
        if not nfse_com_xml:
            raise UserError(_('Nenhuma NFSe selecionada possui XML disponível para download.'))
        
        # Cria um arquivo ZIP em memória
        zip_buffer = io.BytesIO()
        
        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for nfse in nfse_com_xml:
                    # Decodifica o XML do base64
                    xml_content = base64.b64decode(nfse.nfse_xml)
                    
                    # Gera o nome do arquivo
                    if nfse.nfse_xml_filename:
                        filename = nfse.nfse_xml_filename
                    else:
                        # Fallback: gera nome baseado no número ou ID
                        numero_nfse = nfse.name if nfse.name else str(nfse.id)
                        filename = f"geracad.nfse-{numero_nfse}-nfse_xml.xml"
                    
                    # Adiciona o XML ao ZIP
                    zip_file.writestr(filename, xml_content)
                    _logger.info('XML adicionado ao ZIP: %s (NFSe ID: %s)', filename, nfse.id)
            
            # Prepara o conteúdo do ZIP em base64
            zip_buffer.seek(0)
            zip_content = zip_buffer.read()
            zip_base64 = base64.b64encode(zip_content)
            
            # Gera nome do arquivo ZIP com data/hora
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"nfse_xml_{timestamp}.zip"
            
            # Cria um attachment temporário para o download
            attachment = self.env['ir.attachment'].create({
                'name': zip_filename,
                'datas': zip_base64,
                'type': 'binary',
                'res_model': 'geracad.nfse',
                'mimetype': 'application/zip',
            })
            
            _logger.info('ZIP criado com sucesso: %s arquivos, tamanho: %s bytes', 
                        len(nfse_com_xml), len(zip_content))
            
            # Retorna action para download
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
            
        except Exception as e:
            _logger.error('Erro ao criar ZIP de XMLs: %s', str(e))
            raise UserError(_('Erro ao criar arquivo ZIP: %s') % str(e))
        finally:
            zip_buffer.close()

    def action_download_pdf_zip(self):
        """
        Faz download dos PDFs das NFSe selecionadas em um arquivo ZIP.
        Retorna um action para download do arquivo ZIP.
        """
        # Filtra apenas registros que têm PDF
        nfse_com_pdf = self.filtered(lambda r: r.nfse_pdf)
        
        if not nfse_com_pdf:
            raise UserError(_('Nenhuma NFSe selecionada possui PDF disponível para download.'))
        
        # Cria um arquivo ZIP em memória
        zip_buffer = io.BytesIO()
        
        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for nfse in nfse_com_pdf:
                    # Decodifica o PDF do base64
                    pdf_content = base64.b64decode(nfse.nfse_pdf)
                    
                    # Gera o nome do arquivo PDF
                    # Formato: geracad.nfse-{numero_nfse}-nfse.pdf
                    numero_nfse = nfse.name if nfse.name else str(nfse.id)
                    filename = f"geracad.nfse-{numero_nfse}-nfse.pdf"
                    
                    # Adiciona o PDF ao ZIP
                    zip_file.writestr(filename, pdf_content)
                    _logger.info('PDF adicionado ao ZIP: %s (NFSe ID: %s)', filename, nfse.id)
            
            # Prepara o conteúdo do ZIP em base64
            zip_buffer.seek(0)
            zip_content = zip_buffer.read()
            zip_base64 = base64.b64encode(zip_content)
            
            # Gera nome do arquivo ZIP com data/hora
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"nfse_pdf_{timestamp}.zip"
            
            # Cria um attachment temporário para o download
            attachment = self.env['ir.attachment'].create({
                'name': zip_filename,
                'datas': zip_base64,
                'type': 'binary',
                'res_model': 'geracad.nfse',
                'mimetype': 'application/zip',
            })
            
            _logger.info('ZIP de PDFs criado com sucesso: %s arquivos, tamanho: %s bytes', 
                        len(nfse_com_pdf), len(zip_content))
            
            # Retorna action para download
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
            
        except Exception as e:
            _logger.error('Erro ao criar ZIP de PDFs: %s', str(e))
            raise UserError(_('Erro ao criar arquivo ZIP: %s') % str(e))
        finally:
            zip_buffer.close()

    def _enviar_nfse_unica(self):
        """
        Envia uma única NFS-e para o provedor configurado.
        Método privado usado internamente por action_gerar_nfse.
        """
        self.ensure_one()
        
        # Valida se a nota pode ser enviada
        if self.state in ['concluida', 'em_processamento']:
            raise UserError(_('Esta NFS-e não pode ser enviada pois está com status "%s".') % self.state)
        
        # Envia conforme o provedor
        if self.nfse_provider == 'plugnotas':
            payload = self._prepare_plugnotas_payload()
            _logger.info("Payload PlugNotas preparado: %s", payload)
            self.envia_plugnotas(payload)
        elif self.nfse_provider == 'focusnfe':
            referencia, payload = self._prepare_focus_payload()
            _logger.info("Payload Focus NFSe preparado para referência %s: %s", referencia, payload)
            self._send_focus_nfse(referencia, payload)
        else:
            raise UserError(_('Selecione um provedor de NFS-e válido conforme documentação.'))
        
        _logger.info(f"NFS-e ID {self.id} enviada com sucesso")

    def action_gerar_nfse(self):
        """Envia a NFS-e para o provedor configurado conforme a documentação de cada API."""
        # Se for apenas um registro, envia diretamente
        if len(self) == 1:
            self._enviar_nfse_unica()
            return
        
        # Para múltiplos registros, faz contabilização e retorna feedback
        total = len(self)
        enviadas = 0
        puladas = 0
        erros = 0
        erros_lista = []
        
        for rec in self:
            # Valida se a nota pode ser enviada
            if rec.state in ['concluida', 'em_processamento']:
                puladas += 1
                _logger.warning(f"NFS-e ID {rec.id} não pode ser enviada: status '{rec.state}'")
                continue
            
            # Tenta enviar usando o método único
            try:
                rec._enviar_nfse_unica()
                enviadas += 1
            except Exception as e:
                erros += 1
                erro_msg = str(e)
                erros_lista.append(f"NFS-e {rec.name or rec.id}: {erro_msg[:80]}")
                _logger.error(f"Erro ao enviar NFS-e {rec.id}: {erro_msg}")
        
        # Monta mensagem de feedback
        mensagem_parts = [f"Total: {total}", f"✅ Enviadas: {enviadas}"]
        
        if puladas > 0:
            mensagem_parts.append(f"⏭️ Puladas: {puladas}")
        
        if erros > 0:
            mensagem_parts.append(f"❌ Erros: {erros}")
            for erro in erros_lista[:3]:  # Mostra até 3 erros
                mensagem_parts.append(f"  • {erro}")
            if len(erros_lista) > 3:
                mensagem_parts.append(f"  ... e mais {len(erros_lista) - 3}")
        
        mensagem = "\n".join(mensagem_parts)
        
        # Define tipo de notificação
        if erros == 0 and enviadas > 0:
            tipo = 'success'
            titulo = 'Envio Concluído!'
        elif erros > 0 and enviadas > 0:
            tipo = 'warning'
            titulo = 'Envio Parcial'
        elif erros > 0:
            tipo = 'danger'
            titulo = 'Erro no Envio'
        else:
            tipo = 'info'
            titulo = 'Nenhuma Enviada'
        
        # Usa o toast nativo do Odoo
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': titulo,
                'message': mensagem,
                'type': tipo,
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def _prepare_plugnotas_payload(self):
        """Monta a estrutura esperada pela API PlugNotas seguindo o manual oficial."""
        self.ensure_one()

        if not self.nfse_serviço:
            raise UserError(_('Informe o serviço para montar a NFS-e (campo obrigatório na PlugNotas).'))
        
        # Preenche automaticamente com dados do emitente se não estiverem preenchidos
        self._preencher_local_prestacao_do_emitente()
        
        if not self.nfse_local_estado or not self.nfse_local_cidade:
            raise UserError(_('Informe cidade e estado de prestação antes de enviar à PlugNotas. '
                            'Ou configure o endereço completo do emitente (empresa).'))

        descricao_nota = (self.nfse_descricao_nota or '').replace('\n', '  ')
        cliente = self.cliente_id

        payload = [{
                "prestador": {
                "cpfCnpj": re.sub(r'\D', '', self.company_id.l10n_br_cnpj_cpf or ''),
                },
                "tomador": {
                "cpfCnpj": re.sub(r'\D', '', cliente.l10n_br_cnpj_cpf or ''),
                "razaoSocial": cliente.l10n_br_legal_name or cliente.name,
                "email": cliente.email,
                'inscricaoMunicipal': cliente.l10n_br_inscr_mun or "",
                "endereco": {
                    "bairro": cliente.l10n_br_district,
                    "cep": re.sub(r'\D', '', cliente.zip or ''),
                    "estado": cliente.state_id.code,
                    "logradouro": cliente.street,
                    "numero": cliente.l10n_br_number,
                    "descricaoCidade": cliente.city_id.name,
                    "codigoCidade": (cliente.state_id.l10n_br_ibge_code or '') + (cliente.city_id.l10n_br_ibge_code or ''),
                }
            },
            "descricao": descricao_nota,
            "servico": {
                "codigo": self.nfse_serviço.codigo,
                "descricaoLC116": self.nfse_serviço.name,
                "discriminacao": self.nfse_descricao_servico,
                "cnae": self.nfse_CNAE,
                "codigoCidadeIncidencia": (self.nfse_local_estado.l10n_br_ibge_code or '') + (self.nfse_local_cidade.l10n_br_ibge_code or ''),
                "descricaoCidadeIncidencia": self.nfse_local_cidade.name,
                    "iss": {
                        "aliquota": 5,
                    "retido": self.nfse_retido,
                    },
                    "valor": {
                    "servico": self.valor_servico
                },
            },
            "cidadePrestacao": {
                "codigo": (self.nfse_local_estado.l10n_br_ibge_code or '') + (self.nfse_local_cidade.l10n_br_ibge_code or ''),
                "descricao": self.nfse_local_cidade.name,
                "estado": self.nfse_local_estado.code
            }
        }]
        return payload

    def _compose_ibge_municipio(self, state, city):
        """Retorna o código IBGE de 7 dígitos (UF + Município)."""
        self.ensure_one()
        state_code_raw = getattr(state, 'l10n_br_ibge_code', '') or ''
        city_code_raw = getattr(city, 'l10n_br_ibge_code', '') or ''
        state_code = re.sub(r'\D', '', str(state_code_raw))
        city_code = re.sub(r'\D', '', str(city_code_raw))

        if len(city_code) == 7:
            return city_code

        if not city_code:
            raise UserError(_('Código IBGE do município não informado.'))

        uf_code = state_code.zfill(2) if state_code else ''
        municipio_code = city_code.zfill(5)

        if not uf_code:
            raise UserError(_('Código IBGE do estado não informado.'))

        combined = f"{uf_code}{municipio_code}"
        if len(combined) != 7:
            raise UserError(_('Código IBGE inválido: %s') % combined)
        return combined

    def _sanitize_focus_text(self, text):
        """
        Remove caracteres de controle que a Focus NFSe não aceita.
        Remove: \n (quebra de linha), \r (retorno de carro), \t (tab) e outros caracteres de controle.
        Substitui múltiplos espaços por um único espaço.
        """
        if not text:
            return text
        
        # Remove quebras de linha, retornos de carro, tabs e outros caracteres de controle
        # Substitui por espaço para manter legibilidade
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Remove outros caracteres de controle (códigos ASCII 0-31 exceto espaço)
        text = ''.join(char if ord(char) >= 32 or char == ' ' else ' ' for char in text)
        
        # Substitui múltiplos espaços por um único espaço
        text = ' '.join(text.split())
        
        return text.strip()

    def _prepare_focus_payload(self):
        """
        Monta a estrutura esperada pela Focus NFSe Nacional.
        Conforme manual: https://focusnfe.com.br/doc/#nfse-nacional_campos
        Todos os campos devem estar na raiz do JSON, sem objetos aninhados.
        """
        self.ensure_one()

        company_partner = self.company_id.partner_id
        cliente = self.cliente_id

        prestador_cnpj = re.sub(r'\D', '', self.company_id.l10n_br_cnpj_cpf or '')
        tomador_doc = re.sub(r'\D', '', cliente.l10n_br_cnpj_cpf or '')

        if len(prestador_cnpj) != 14:
            raise UserError(_('CNPJ do prestador inválido para Focus NFSe.'))
        if len(tomador_doc) not in (11, 14):
            raise UserError(_('CPF/CNPJ do tomador inválido para Focus NFSe.'))
        if not company_partner.l10n_br_inscr_mun:
            raise UserError(_('Inscrição municipal do prestador é obrigatória na Focus NFSe.'))
        if not company_partner.state_id or not company_partner.state_id.l10n_br_ibge_code:
            raise UserError(_('Informe o código IBGE do estado do prestador.'))
        if not company_partner.city_id or not company_partner.city_id.l10n_br_ibge_code:
            raise UserError(_('Informe o código IBGE do município do prestador.'))
        if not cliente.state_id or not cliente.state_id.l10n_br_ibge_code:
            raise UserError(_('Informe o código IBGE do estado do tomador.'))
        if not cliente.city_id or not cliente.city_id.l10n_br_ibge_code:
            raise UserError(_('Informe o código IBGE do município do tomador.'))
        if not cliente.street or not cliente.l10n_br_number:
            raise UserError(_('Endereço completo do tomador é obrigatório para Focus NFSe.'))
        if not self.nfse_serviço:
            raise UserError(_('Informe o serviço LC 116 para montar o payload da Focus NFSe.'))
        
        # Preenche automaticamente com dados do emitente se não estiverem preenchidos
        self._preencher_local_prestacao_do_emitente()
        
        if not self.nfse_local_estado or not self.nfse_local_cidade:
            raise UserError(_('Informe o estado e cidade onde o serviço foi prestado (campos obrigatórios). '
                            'Ou configure o endereço completo do emitente (empresa).'))
        if not self.nfse_local_estado.l10n_br_ibge_code or not self.nfse_local_cidade.l10n_br_ibge_code:
            raise UserError(_('Informe o código IBGE do estado e cidade de prestação do serviço. '
                            'Ou configure o código IBGE no endereço do emitente (empresa).'))

        referencia = self.nfse_provider_identifier or f"FOCUS_{self.id or datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Data de emissão no formato ISO 8601
        data_emissao_dt = fields.Datetime.context_timestamp(self, datetime.utcnow())
        data_emissao = data_emissao_dt.isoformat() if data_emissao_dt else datetime.utcnow().isoformat()
        
        # Data de competência (mesmo dia da emissão)
        data_competencia = fields.Date.today().strftime('%Y-%m-%d')
        
        # Valores do serviço
        aliquota = 5.0
        valor_servico = self.valor_servico or 0.0

        # Código do serviço LC 116
        item_lista_servico = self.nfse_serviço.codigo or ''
        if item_lista_servico and len(item_lista_servico) == 4 and item_lista_servico.isdigit():
            item_lista_servico = f"{item_lista_servico[:2]}.{item_lista_servico[2:]}"

        # Códigos IBGE
        prestador_codigo_municipio = self._compose_ibge_municipio(company_partner.state_id, company_partner.city_id)
        tomador_codigo_municipio = self._compose_ibge_municipio(cliente.state_id, cliente.city_id)
        codigo_municipio_prestacao = self._compose_ibge_municipio(self.nfse_local_estado, self.nfse_local_cidade)

        # Sanitiza a discriminação/descrição do serviço
        descricao_servico = self._sanitize_focus_text(
            self.nfse_descricao_nota if self.nfse_descricao_nota else (self.nfse_descricao_servico or 'SERVICOS PRESTADOS')
        )

        # Código de opção do Simples Nacional
        # Valores aceitos: 1=Não Optante, 2=Optante MEI, 3=Optante ME/EPP
        # Não pode ser 0!
        optante_simples = getattr(self.company_id, 'l10n_br_tax_regime', None)
        if optante_simples in ("1", 1, 'Simples Nacional'):
            # Se for Simples Nacional, usar 3 (ME/EPP) como padrão
            # TODO: Verificar se há campo específico para MEI vs ME/EPP
            codigo_opcao_simples_nacional = 3
        else:
            # Não optante
            codigo_opcao_simples_nacional = 1

        # Código tributação nacional ISS (formato: código LC 116 sem ponto)
        # Deve ter exatamente 6 dígitos: [0-9]{6}
        # Formato: XX.XX.XX (6 dígitos) ou XX.XX (4 dígitos que vira XX.XX.00)
        # Conforme lista nacional do Sistema Nacional NFS-e
        # Exemplos: "08.01" → "080100", "8.01" → "080100", "08.01.02" → "080102"
        codigo_tributacao_nacional_iss = ''
        if item_lista_servico:
            # Normaliza o código: separa por pontos, normaliza cada parte para 2 dígitos
            partes = str(item_lista_servico).split('.')
            partes_normalizadas = []
            
            for parte in partes:
                # Remove caracteres não numéricos e normaliza para 2 dígitos
                parte_limpa = re.sub(r'\D', '', parte)
                if parte_limpa:
                    # Adiciona zero à esquerda se necessário (ex: "8" → "08")
                    partes_normalizadas.append(parte_limpa.zfill(2))
            
            # Monta o código de 6 dígitos
            if len(partes_normalizadas) >= 3:
                # Código completo de 6 dígitos (ex: 08.01.02 → 080102)
                codigo_tributacao_nacional_iss = ''.join(partes_normalizadas[:3])
            elif len(partes_normalizadas) >= 2:
                # Código de 4 dígitos, adiciona "00" (ex: 08.01 → 080100)
                codigo_tributacao_nacional_iss = ''.join(partes_normalizadas[:2]) + '00'
            elif len(partes_normalizadas) >= 1:
                # Código incompleto, preenche com zeros
                codigo_tributacao_nacional_iss = partes_normalizadas[0].zfill(2) + '0000'
            else:
                # Fallback: tenta extrair números do código original
                codigo_limpo = re.sub(r'\D', '', item_lista_servico)
                if len(codigo_limpo) >= 4:
                    codigo_tributacao_nacional_iss = codigo_limpo[:4] + '00'
                else:
                    codigo_tributacao_nacional_iss = codigo_limpo.zfill(4) + '00'
            
            # Garante que tenha exatamente 6 dígitos
            codigo_tributacao_nacional_iss = codigo_tributacao_nacional_iss[:6].zfill(6)
            
            # Log para debug: verifica o código gerado
            _logger.info('Código de tributação nacional gerado: %s (de: %s)', 
                        codigo_tributacao_nacional_iss, item_lista_servico)
        else:
            raise UserError(_('Código de serviço LC 116 não informado. É obrigatório para gerar o código de tributação nacional.'))

        # Tributação ISS: 1=Tributável, 2=Isento, 3=Imune, etc.
        tributacao_iss = 1  # Padrão: Tributável

        # Tipo de retenção ISS conforme schema XML (tpRetISSQN):
        # 1 = Não Retido
        # 2 = Retido pelo Tomador
        # 3 = Retido pelo Intermediário
        # Não pode ser 0!
        if self.nfse_retido:
            # Quando retido, assume retenção pelo tomador (caso mais comum)
            # TODO: Adicionar campo para distinguir retenção pelo tomador vs intermediário se necessário
            tipo_retencao_iss = 2  # Retido pelo Tomador
        else:
            tipo_retencao_iss = 1  # Não Retido

        # Monta o JSON conforme estrutura do manual NFSe Nacional (todos os campos na raiz)
        nfse = {
            # Dados gerais
            "data_emissao": data_emissao,
            "data_competencia": data_competencia,
            
            # Prestador (na raiz)
            "codigo_municipio_emissora": prestador_codigo_municipio,
            "cnpj_prestador": prestador_cnpj,
            "inscricao_municipal_prestador": re.sub(r'\D', '', company_partner.l10n_br_inscr_mun or ''),
            "codigo_opcao_simples_nacional": codigo_opcao_simples_nacional,
            
            # Regime especial de tributação (se informado)
            "regime_especial_tributacao": int(self.regime_especial_tributacao) if self.regime_especial_tributacao else 0,
            
            # Tomador (na raiz)
            "razao_social_tomador": cliente.l10n_br_legal_name or cliente.name,
            "codigo_municipio_tomador": tomador_codigo_municipio,
            "cep_tomador": re.sub(r'\D', '', cliente.zip or ''),
            "logradouro_tomador": cliente.street or '',
            "numero_tomador": cliente.l10n_br_number or '',
            "complemento_tomador": cliente.street2 or '',
            "bairro_tomador": cliente.l10n_br_district or '',
        }

        # CPF ou CNPJ do tomador
        if len(tomador_doc) == 14:
            nfse["cnpj_tomador"] = tomador_doc
        else:
            nfse["cpf_tomador"] = tomador_doc

        # Telefone do tomador (se disponível)
        if cliente.phone or cliente.mobile:
            telefone = cliente.phone or cliente.mobile
            telefone_limpo = re.sub(r'\D', '', telefone)
            if len(telefone_limpo) >= 10:
                nfse["telefone_tomador"] = telefone

        # Email do tomador
        if cliente.email:
            nfse["email_tomador"] = cliente.email

        # Serviço (todos os campos na raiz conforme manual)
        nfse["codigo_municipio_prestacao"] = codigo_municipio_prestacao
        nfse["codigo_tributacao_nacional_iss"] = codigo_tributacao_nacional_iss
        nfse["descricao_servico"] = descricao_servico
        nfse["valor_servico"] = valor_servico
        nfse["tributacao_iss"] = tributacao_iss
        nfse["tipo_retencao_iss"] = tipo_retencao_iss

        # Grupo do percentual aproximado dos tributos (obrigatório para evitar E0713)
        # Para Não Optante o suporte FocusNFE orienta enviar com valores zerados.
        # Documentação: campos.focusnfe.com.br/nfse_nacional/EmissaoDPSXml.html (pTotTribFed, pTotTribEst, pTotTribMun)
        nfse["percentual_total_tributos_federais"] = 0.00
        nfse["percentual_total_tributos_estaduais"] = 0.00
        nfse["percentual_total_tributos_municipais"] = 0.00

        return referencia, nfse

    def _focus_api_instance(self):
        """Retorna uma instância configurada do client Focus NFSe considerando o parâmetro `geracad_nfse.focus_homologacao`."""
        focus_param = self.env['ir.config_parameter'].sudo().get_param('geracad_nfse.focus_homologacao', 'false')
        focus_flag = str(focus_param).strip().lower()
        use_homologation = focus_flag in ('1', 'true', 'yes')
        return FocusNFSeAPI(homologacao=use_homologation)

    def _send_focus_nfse(self, referencia, payload):
        """Realiza o envio para a Focus NFSe e registra o retorno."""
        self.ensure_one()

        try:
            focus_api = self._focus_api_instance()
            status_code, response_data = focus_api.send_nfse(referencia, payload)
        except requests.exceptions.RequestException as exc:
            _logger.error('Erro de comunicação com Focus NFSe: %s', exc)
            self.write({
                'state': 'erro',
                'resposta_api_ids': [(0, 0, {
                    'state': 'erro',
                    'resposta': str(exc),
                    'data_resposta': fields.Datetime.now()
                })]
            })
            raise UserError(_('Falha na comunicação com a Focus NFSe: %s') % exc)

        if isinstance(response_data, dict):
            retorno_texto = json.dumps(response_data, ensure_ascii=False)
        else:
            retorno_texto = str(response_data)
        sucesso_http = status_code in (200, 201, 202)
        status_api = (response_data or {}).get('status') if isinstance(response_data, dict) else None

        valores_write: Dict[str, Any] = {
            'nfse_provider_identifier': referencia,
            'data_emissao': fields.Datetime.now(),
            'resposta_api_ids': [(0, 0, {
                'state': 'sucesso' if sucesso_http else 'erro',
                'resposta': retorno_texto,
                'data_resposta': fields.Datetime.now()
            })]
        }

        if sucesso_http:
            if status_api and status_api.lower() in ('autorizado', 'autorizada', 'emitido', 'emitida'):
                valores_write['state'] = 'concluida'
                valores_write['name'] = (response_data.get('numero_nfse')
                                         or response_data.get('numero')
                                         or self.name)
                valores_write['nfse_protocolo'] = response_data.get('codigo_verificacao') or response_data.get('protocolo')
            else:
                valores_write['state'] = 'em_processamento'
        else:
            valores_write['state'] = 'erro'

        self.write(valores_write)

    def _fetch_focus_nfse(self, referencia):
        """Consulta a Focus NFSe pela referência configurada e atualiza os dados locais."""
        self.ensure_one()

        if not referencia:
            raise UserError(_('Informe a referência da NFSe para consulta na Focus NFSe.'))

        try:
            focus_api = self._focus_api_instance()
            status_code, response_data = focus_api.get_nfse(referencia)
        except requests.exceptions.RequestException as exc:
            _logger.error('Erro de comunicação ao consultar Focus NFSe: %s', exc)
            raise UserError(_('Falha ao consultar Focus NFSe: %s') % exc)

        log_payload = response_data if isinstance(response_data, (dict, list)) else {'raw': str(response_data)}
        retorno_texto = json.dumps(log_payload, ensure_ascii=False)

        valores_write: Dict[str, Any] = {
            'nfse_provider_identifier': referencia,
            'resposta_api_ids': [(0, 0, {
                'state': 'sucesso' if status_code == 200 else 'erro',
                'resposta': retorno_texto,
                'data_resposta': fields.Datetime.now()
            })]
        }

        if status_code == 200 and isinstance(response_data, dict):
            status_api = (response_data.get('status') or '').lower()
            status_map = {
                'autorizado': 'concluida',
                'autorizada': 'concluida',
                'emitido': 'concluida',
                'emitida': 'concluida',
                'concluido': 'concluida',
                'concluida': 'concluida',
                'processando_autorizacao': 'em_processamento',
                'processando': 'em_processamento',
                'em_processamento': 'em_processamento',
                'erro_autorizacao': 'erro',
                'erro': 'erro',
                'rejeitado': 'erro',
                'rejeitada': 'erro',
                'cancelado': 'cancelada',
                'cancelada': 'cancelada',
                'substituido': 'concluida',
            }
            valores_write['state'] = status_map.get(status_api, 'erro')
            valores_write['description'] = response_data.get('mensagem') or response_data.get('descricao') or response_data.get('status')

            numero_nfse = response_data.get('numero_nfse') or response_data.get('numero')
            if numero_nfse:
                valores_write['name'] = numero_nfse

            numero_rps = response_data.get('numero_rps')
            serie_rps = response_data.get('serie_rps')
            if numero_rps:
                valores_write['codigo_servico'] = f"RPS {serie_rps or ''}/{numero_rps}".strip('/ ')

            codigo_verificacao = response_data.get('codigo_verificacao') or response_data.get('protocolo')
            if codigo_verificacao:
                valores_write['nfse_protocolo'] = codigo_verificacao

            data_emissao = response_data.get('data_emissao') or response_data.get('data_emissao_nfse')
            if data_emissao:
                try:
                    valores_write['data_emissao'] = fields.Datetime.from_string(data_emissao)
                except Exception:
                    _logger.warning('Não foi possível converter data_emissao Focus NFSe: %s', data_emissao)

            # Tenta baixar PDF/XML sempre que houver resposta válida da API
            # O método _fetch_focus_files já trata casos onde o PDF não está disponível
            try:
                _logger.info('Tentando baixar PDF/XML da Focus NFSe com status: %s', status_api)
                self._fetch_focus_files(focus_api, referencia, response_data, valores_write)
            except Exception as exc:
                _logger.warning('Não foi possível baixar PDF/XML da Focus NFSe: %s', exc)
        else:
            valores_write['state'] = 'erro'

        self.write(valores_write)

    def action_cancelar_nfse(self):
        """
        Abre wizard para solicitar justificativa de cancelamento.
        Conforme documentação FocusNFe: https://focusnfe.com.br/doc/?python#nfse
        """
        self.ensure_one()
        
        # Validações
        if self.state != 'concluida':
            raise UserError(_('Apenas notas emitidas podem ser canceladas.'))
        
        if self.nfse_provider != 'focusnfe':
            raise UserError(_('Cancelamento disponível apenas para notas emitidas via Focus NFSe.'))
        
        if not self.nfse_provider_identifier:
            raise UserError(_('Não foi possível identificar a referência da nota para cancelamento.'))
        
        # Abre wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cancelar NFS-e'),
            'res_model': 'geracad.nfse.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_nfse_id': self.id,
                'default_referencia': self.nfse_provider_identifier,
            }
        }

    def _cancelar_focus_nfse(self, referencia, justificativa):
        """
        Cancela uma NFSe na Focus NFSe.
        
        Args:
            referencia (str): Identificador único da nota usado no envio
            justificativa (str): Justificativa do cancelamento (15 a 255 caracteres)
            
        Returns:
            tuple: (status_code, response_json)
        """
        self.ensure_one()
        
        # Valida justificativa
        if not justificativa or len(justificativa.strip()) < 15:
            raise UserError(_('A justificativa deve ter no mínimo 15 caracteres.'))
        
        if len(justificativa) > 255:
            raise UserError(_('A justificativa deve ter no máximo 255 caracteres.'))
        
        try:
            focus_api = self._focus_api_instance()
            status_code, response_data = focus_api.cancel_nfse(referencia, justificativa.strip())
        except requests.exceptions.RequestException as exc:
            _logger.error('Erro de comunicação ao cancelar NFSe na Focus: %s', exc)
            raise UserError(_('Falha na comunicação com a Focus NFSe: %s') % exc)
        
        # Registra resposta
        if isinstance(response_data, dict):
            retorno_texto = json.dumps(response_data, ensure_ascii=False)
        else:
            retorno_texto = str(response_data)
        
        sucesso_http = status_code in (200, 201, 202)
        status_api = (response_data or {}).get('status') if isinstance(response_data, dict) else None
        
        valores_write: Dict[str, Any] = {
            'resposta_api_ids': [(0, 0, {
                'state': 'sucesso' if sucesso_http else 'erro',
                'resposta': retorno_texto,
                'data_resposta': fields.Datetime.now()
            })]
        }
        
        if sucesso_http:
            if status_api and status_api.lower() in ('cancelado', 'cancelada'):
                valores_write['state'] = 'cancelada'
                valores_write['description'] = response_data.get('mensagem') or 'Nota cancelada com sucesso.'
            else:
                # Pode estar processando o cancelamento
                valores_write['state'] = 'em_processamento'
                valores_write['description'] = response_data.get('mensagem') or 'Cancelamento em processamento.'
        else:
            # Erro no cancelamento
            mensagem_erro = response_data.get('mensagem') or response_data.get('erro') or 'Erro ao cancelar nota.'
            valores_write['description'] = mensagem_erro
            raise UserError(_('Erro ao cancelar nota: %s') % mensagem_erro)
        
        self.write(valores_write)
        return status_code, response_data

    def _fetch_focus_files(self, focus_api, referencia, payload, valores_write):
        """
        Baixa PDF/XML conforme retorno da Focus NFSe para disponibilizar ao usuário.
        Conforme documentação oficial: https://focusnfe.com.br/doc/?python#nfse
        """
        base_host = focus_api.base_url.rstrip('/')
        auth = (focus_api.api_token, "")
        
        # Log dos dados retornados pela API para debug
        _logger.info('=== Dados retornados pela Focus NFSe para download de arquivos ===')
        _logger.info('Campos disponíveis no payload: %s', list(payload.keys()) if isinstance(payload, dict) else 'N/A')
        _logger.info('url: %s', payload.get('url'))
        _logger.info('url_xml: %s', payload.get('url_xml'))
        _logger.info('caminho_xml_nota_fiscal: %s', payload.get('caminho_xml_nota_fiscal'))
        _logger.info('url_danfse: %s', payload.get('url_danfse'))

        # === DOWNLOAD DO PDF ===
        # Conforme documentação oficial, o PDF está no campo 'url_danfse'
        # Essa URL aponta para o DANFSE (Documento Auxiliar da NFSe) em PDF
        # Pode ser uma URL da AWS S3 ou do servidor Focus
        
        pdf_candidates = []
        # Prioridade 1: URL do DANFSE (campo específico da documentação)
        if payload.get('url_danfse'):
            pdf_candidates.append(payload.get('url_danfse'))
        # Prioridade 2: URL padrão da API Focus NFSe (fallback)
        pdf_candidates.append(f"{base_host}/v2/nfse/{referencia}.pdf")
        
        pdf_baixado = False
        for pdf_url in pdf_candidates:
            if not pdf_url:
                continue
            try:
                _logger.info('Tentando baixar PDF de: %s', pdf_url)
                
                # URLs da AWS S3 não precisam de autenticação, URLs da API Focus precisam
                if 'amazonaws.com' in pdf_url or 's3.' in pdf_url:
                    # URL pública da AWS S3 - não precisa de auth
                    pdf_response = requests.get(pdf_url, timeout=30)
                else:
                    # URL da API Focus NFSe - precisa de auth
                    pdf_response = requests.get(pdf_url, auth=auth, timeout=30)
                
                _logger.info('Resposta PDF - Status: %s, Content-Type: %s, Tamanho: %s bytes', 
                            pdf_response.status_code, 
                            pdf_response.headers.get('content-type'),
                            len(pdf_response.content) if pdf_response.content else 0)
                
                if pdf_response.status_code == 200 and pdf_response.content:
                    # Verifica se o conteúdo é realmente um PDF
                    if pdf_response.content.startswith(b'%PDF'):
                        valores_write['nfse_pdf'] = base64.b64encode(pdf_response.content)
                        valores_write['nfse_pdf_url'] = pdf_url  # Salva a URL do PDF para referência
                        _logger.info('✅ PDF da Focus NFSe baixado com sucesso de %s: %s bytes', pdf_url, len(pdf_response.content))
                        pdf_baixado = True
                        break
                    else:
                        _logger.warning('⚠️ Conteúdo baixado não é um PDF válido (não começa com %%PDF): %s', pdf_url)
                        _logger.warning('Primeiros 50 bytes: %s', pdf_response.content[:50])
            except requests.exceptions.RequestException as exc:
                _logger.warning('❌ Falha ao baixar PDF da Focus NFSe de %s: %s', pdf_url, exc)
        
        if not pdf_baixado:
            _logger.warning('⚠️ Nenhum PDF foi baixado com sucesso da Focus NFSe')

        # === DOWNLOAD DO XML ===
        # Conforme documentação: pode vir em 'url_xml' ou 'caminho_xml_nota_fiscal'
        xml_url = payload.get('url_xml') or payload.get('caminho_xml_nota_fiscal')
        
        if xml_url:
            # Se a URL não for completa, monta com base_host
            if not xml_url.startswith('http'):
                # Caminho relativo - monta URL completa
                # Remove barra inicial se houver para evitar duplicação
                xml_path = xml_url.lstrip('/')
                xml_url = f"{base_host}/{xml_path}"
            
            try:
                _logger.info('Tentando baixar XML de: %s', xml_url)
                
                # URLs da AWS S3 não precisam de autenticação, URLs da API Focus precisam
                if 'amazonaws.com' in xml_url or 's3.' in xml_url:
                    # URL pública da AWS S3 - não precisa de auth
                    xml_response = requests.get(xml_url, timeout=30)
                else:
                    # URL da API Focus NFSe - precisa de auth
                    xml_response = requests.get(xml_url, auth=auth, timeout=30)
                
                _logger.info('Resposta XML - Status: %s, Content-Type: %s, Tamanho: %s bytes',
                            xml_response.status_code,
                            xml_response.headers.get('content-type'),
                            len(xml_response.content) if xml_response.content else 0)
                
                if xml_response.status_code == 200 and xml_response.content:
                    valores_write['nfse_xml'] = base64.b64encode(xml_response.content)
                    # Define o nome do arquivo com extensão .xml incluindo o número da NFSe
                    numero_nfse = self.name if self.name else (self.id if self.id else 'temp')
                    valores_write['nfse_xml_filename'] = f"geracad.nfse-{numero_nfse}-nfse_xml.xml"
                    _logger.info('✅ XML da Focus NFSe baixado com sucesso: %s bytes', len(xml_response.content))
            except requests.exceptions.RequestException as exc:
                _logger.warning('❌ Falha ao baixar XML da Focus NFSe de %s: %s', xml_url, exc)
        else:
            _logger.warning('⚠️ Nenhuma URL de XML encontrada no payload da Focus NFSe')

    def _fetch_plugnotas(self, identificador=None):
        """Consulta o status na PlugNotas e atualiza os dados locais."""
        self.ensure_one()

        if self.nfse_provider != 'plugnotas':
            raise UserError(_('Consulta PlugNotas solicitada para um registro configurado com Focus NFSe.'))

        document_id = identificador or self.nfse_provider_identifier or self.plugnotas_id
        if not document_id:
            raise UserError(_('Defina o identificador PlugNotas antes de consultar.'))

        headers = {
            "Content-Type": content_type,
            "x-api-key": api_key
        }

        try:
            response = requests.get(f"{url}/consultar/{document_id}", headers=headers)
            try:
                response_data = response.json()
            except ValueError:
                response_data = {}
        except requests.exceptions.RequestException as exc:
            _logger.error('Erro de comunicação ao consultar PlugNotas: %s', exc)
            self.write({
                'state': 'erro',
                'resposta_api_ids': [(0, 0, {
                    'state': 'erro',
                    'resposta': str(exc),
                    'data_resposta': fields.Datetime.now()
                })]
            })
            raise UserError(_('Falha ao consultar PlugNotas: %s') % exc)

        registros = []
        if isinstance(response_data, list):
            registros = response_data
        elif response_data:
            registros = [response_data]

        write_vals: Dict[str, Any] = {
            'nfse_provider_identifier': document_id,
        }
        log_entries = []
        novo_estado = None

        def _append_log(status, mensagem):
            log_entries.append((0, 0, {
                'state': status,
                'resposta': mensagem,
                'data_resposta': fields.Datetime.now()
            }))

        if response.status_code == 200 and registros:
            for registro in registros:
                situacao = (registro.get('situacao') or '').upper()
                mensagem = registro.get('mensagem') or registro.get('message') or json.dumps(registro, ensure_ascii=False)

                if situacao == 'PROCESSANDO':
                    _append_log('processando', mensagem)
                    if novo_estado not in ('concluida', 'erro', 'cancelada'):
                        novo_estado = 'em_processamento'
                elif situacao == 'REJEITADO':
                    _append_log('erro', mensagem)
                    novo_estado = 'erro'
                elif situacao in ('CANCELADO', 'CANCELADA'):
                    _append_log('sucesso', mensagem)
                    novo_estado = 'cancelada'
                elif situacao == 'CONCLUIDO':
                    _append_log('sucesso', json.dumps(registro, ensure_ascii=False))
                    novo_estado = 'concluida'
                    write_vals['name'] = registro.get('numeroNfse') or self.name
                    write_vals['nfse_protocolo'] = registro.get('protocoloPrefeitura') or registro.get('protocolo')
                    write_vals['plugnotas_id'] = registro.get('id') or document_id

                    emissao = registro.get('emissao')
                    if emissao:
                        try:
                            write_vals['data_emissao'] = datetime.strptime(emissao, '%d/%m/%Y')
                        except ValueError:
                            _logger.warning('Formato de data inesperado retornado pela PlugNotas: %s', emissao)

                    pdf_url = registro.get('pdf')
                    if pdf_url:
                        try:
                            pdf_headers = {
                                "Content-Type": 'application/pdf',
                                "x-api-key": api_key
                            }
                            pdf_response = requests.get(pdf_url, headers=pdf_headers, stream=True)
                            if pdf_response.status_code == 200:
                                write_vals['nfse_pdf'] = base64.b64encode(pdf_response.content)
                        except requests.exceptions.RequestException as exc:
                            _logger.warning('Falha ao baixar PDF da PlugNotas (%s): %s', pdf_url, exc)

                    xml_url = registro.get('xml')
                    if xml_url:
                        try:
                            xml_headers = {
                                "Content-Type": 'application/xml',
                                "x-api-key": api_key
                            }
                            xml_response = requests.get(xml_url, headers=xml_headers, stream=True)
                            if xml_response.status_code == 200:
                                write_vals['nfse_xml'] = base64.b64encode(xml_response.content)
                                # Define o nome do arquivo com extensão .xml incluindo o número da NFSe
                                numero_nfse = self.name if self.name else (self.id if self.id else 'temp')
                                write_vals['nfse_xml_filename'] = f"geracad.nfse-{numero_nfse}-nfse_xml.xml"
                        except requests.exceptions.RequestException as exc:
                            _logger.warning('Falha ao baixar XML da PlugNotas (%s): %s', xml_url, exc)

            if not novo_estado:
                novo_estado = self.state
        else:
            mensagem_erro = ''
            if isinstance(response_data, dict):
                erro = response_data.get('error') or response_data
                if isinstance(erro, dict):
                    mensagem_erro = erro.get('message') or json.dumps(erro, ensure_ascii=False)
                else:
                    mensagem_erro = str(erro)
            else:
                mensagem_erro = str(response_data or response.text)

            _append_log('erro', mensagem_erro)
            novo_estado = 'erro'

        if log_entries:
            write_vals.setdefault('resposta_api_ids', [])
            write_vals['resposta_api_ids'].extend(log_entries)

        if novo_estado:
            write_vals['state'] = novo_estado

        self.write(write_vals)
        return response.status_code, response_data

    def get_nfse_plugnotas(self, nfse_id):
        self.ensure_one()
        headers = {
                "Content-Type": content_type,
                "x-api-key": api_key 
            }
        response = requests.get(url+"/"+nfse_id, headers=headers)
        return response.status_code, response.json()
    
    def get_consulta_nfse_plugnotas(self, id=False):
        self.ensure_one()
        return self._fetch_plugnotas(id)

    
    def get_pdf_nfse_plugnotas(self, nfse_id):
        headers = {
                "Content-Type": "application/pdf",
                "x-api-key": api_key 
            }

        response = requests.get(url+"/pdf/"+nfse_id, headers=headers)
        return response
    
    def envia_plugnotas(self, payload, tipo='POST', id=""):
            self.ensure_one()
            headers = {
                "Content-Type": content_type,
                "x-api-key": api_key 
            }
            try:
                response = None
                if tipo == 'POST':
                    response = requests.post(url, json=payload, headers=headers)
                elif tipo == 'GET':
                    response = requests.get(url=url+"/"+id,  headers=headers)
                else:
                    raise UserError(_('Tipo de requisição PlugNotas inválido.'))
                if response is None:
                    raise UserError(_('Nenhuma resposta foi retornada pela PlugNotas.'))
              #  response.raise_for_status()
                response_data = response.json()
                _logger.info(response_data)
                resposta = response_data.get('message', str(response_data))
                if response.status_code == 200 :

                    documents = response_data.get('documents')
                    for doc in documents:
                        self.write({
                            'plugnotas_id': doc.get('id'),
                            'nfse_provider_identifier': doc.get('id'),
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
                    erro = response_data.get('error') if isinstance(response_data, dict) else {}
                    message = erro.get('message') if isinstance(erro, dict) else resposta
                    self.write({
                            'resposta_api_ids':[(0,0,
                                {
                                'state': 'erro',
                                'resposta':message, 
                                'data_resposta': fields.Datetime.now()
                                }
                            )
                            ],
                            'state': 'erro'
                        })
                    
            except requests.exceptions.RequestException as e:
                _logger.error("Erro ao comunicar com a API PlugNotas: %s", e)
                self.env['geracad.nfse.resposta'].create({
                    'nfse_id': self.id,
                    'resposta': str(e),
                    'state': 'erro'
                })
                self.write({'state': 'erro'})
                raise UserError(_("Erro ao comunicar com a API PlugNotas: %s") % str(e))
            
            
class GeracadNfseItem(models.Model):
    """Modelo para itens detalhados da NFS-e, conforme exigência de municípios como São Luís/MA."""
    _name = "geracad.nfse.item"
    _description = "Itens do Serviço da NFS-e"
    _order = "sequence, id"

    nfse_id = fields.Many2one(
        'geracad.nfse',
        string='NFS-e',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequência', default=10)
    discriminacao = fields.Char(
        string='Discriminação',
        required=True,
        help='Descrição detalhada do item'
    )
    quantidade = fields.Float(
        string='Quantidade',
        default=1.0,
        digits=(12, 2),
        help='Quantidade do item'
    )
    valor_unitario = fields.Float(
        string='Valor Unitário',
        digits=(12, 2),
        help='Valor unitário do item'
    )
    valor_total = fields.Float(
        string='Valor Total',
        compute='_compute_valor_total',
        store=True,
        digits=(12, 2),
        help='Valor total = quantidade x valor unitário'
    )
    tributavel = fields.Boolean(
        string='Tributável',
        default=True,
        help='Se o item é tributável ou não'
    )

    @api.depends('quantidade', 'valor_unitario')
    def _compute_valor_total(self):
        """Calcula o valor total do item."""
        for item in self:
            item.valor_total = item.quantidade * item.valor_unitario


class GeracadNFSEResposta(models.Model):
    _name = "geracad.nfse.resposta"
    _description = "Respostas da API para NFS-e"

    nfse_id = fields.Many2one('geracad.nfse', string="NFS-e", required=False, ondelete='cascade')
    data_resposta = fields.Datetime("Data da Resposta", default=fields.Datetime.now)
    resposta = fields.Text("Resposta da API")
    state = fields.Selection(
        [('sucesso', 'Sucesso'), ('erro', 'Erro'),('processando', 'Processando')],
        string="Status"
    )

    @api.model
    def _auto_init(self):
        """Garante que registros órfãos não impeçam a criação da foreign key."""
        res = super()._auto_init()
        cr = self.env.cr
        cr.execute(
            """
            UPDATE {table} r
               SET nfse_id = NULL
             WHERE nfse_id IS NOT NULL
               AND NOT EXISTS (
                   SELECT 1 FROM geracad_nfse n WHERE n.id = r.nfse_id
               )
            """.format(table=self._table)
        )
        return res
class GeracadNFSEServico(models.Model):
    """Modelo para armazenar os códigos de serviço (conforme lista anexa à LC 116/2003)"""
    _name = "geracad.nfse.servico"
    _description = "Código de Serviço para NFS-e"
    _order = "codigo"

    codigo = fields.Char("Código do Serviço", required=True, help="Código conforme lista de serviços (ex: 8.01, 8.02, 31.01)")
    name = fields.Char("Descrição do Serviço", required=True)
    aliquota = fields.Float("Alíquota (%)", default=5.0, help="Alíquota de ISS em %")
    
    _sql_constraints = [
        ('codigo_unique', 'unique(codigo)', 'O código de serviço deve ser único!')
    ]


class GeracadNFSECNAE(models.Model):
    """Modelo para armazenar os códigos CNAE e relacioná-los aos códigos de serviço"""
    _name = "geracad.nfse.cnae"
    _description = "Códigos CNAE para NFS-e"
    _order = "codigo"

    codigo = fields.Char("Código CNAE", required=True, size=9, help="Código CNAE com 7 dígitos")
    name = fields.Char("Descrição da Atividade", required=True)
    servico_id = fields.Many2one(
        'geracad.nfse.servico',
        string='Código de Serviço',
        required=True,
        help='Código de serviço (conforme lista LC 116/2003) relacionado a este CNAE'
    )
    servico_codigo = fields.Char(
        string='Código',
        related='servico_id.codigo',
        store=True,
        readonly=True
    )
    
    _sql_constraints = [
        ('codigo_unique', 'unique(codigo)', 'O código CNAE deve ser único!')
    ]
   