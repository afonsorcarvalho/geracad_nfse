# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoFinanceiroParcelasInherit(models.Model):
    #TODO
    # criar campo com many2one da nfse
    _inherit = "geracad.curso.financeiro.parcelas"
    
    nfse_id = fields.Many2one(
        'geracad.nfse',
        string='NFSe',
        )
    nfse_state = fields.Char(tracking=True)
    taxa_administrativa = fields.Float("Taxa Administrativa")
    valor_total = fields.Monetary(string='Valor Total', compute='_compute_valor_total', store=True)

    @api.depends('valor', 'taxa_administrativa')
    def _compute_valor_total(self):
        for rec in self:
            rec.valor_total = rec.valor

    def action_aplicar_taxa_administrativa(self):
        for rec in self:
            if rec.state != 'recebido':
                raise ValidationError('A Taxa Administrativa só pode ser aplicada a parcelas recebidas!')
            rec.write({
                'taxa_administrativa': rec.valor * 0.05  # Exemplo de 5% de taxa administrativa
            })

    
    def action_emitir_nfse(self):
        

        for rec in self:
            cnae = ""
            servico = ""
            descricao_nota_servico = ""
            if rec.state == 'recebido':
                # Verificar se a NFS-e já foi emitida
                if rec.nfse_id:
                    raise UserError(_("A NFS-e já foi emitida para esta parcela."))

                # # Aplicar taxa administrativa ao pagar a parcela
                # rec.action_aplicar_taxa_administrativa()
                if rec.curso_matricula_id.curso_turma_id.curso_id.type_curso.name in ['Técnico']:
                    cnae = '854140000'
                    servico = self.env['geracad.nfse.servico'].search([('codigo','=','0801')],limit=1)
                    descricao_nota_servico = 'SERVICO DE EDUCACAO PROFISSIONAL DE NIVEL TECNICO'

                if rec.curso_matricula_id.curso_turma_id.curso_id.type_curso.name in ['Superior']:
                    cnae = '853250000'
                    servico = self.env['geracad.nfse.servico'].search([('codigo','=','0801')],limit=1)
                    descricao_nota_servico = 'SERVICO DE EDUCACAO SUPERIOR - GRADUACAO E POS-GRADUACAO'

                if rec.curso_matricula_id.curso_turma_id.curso_id.type_curso.name in ['Preparatório','Qualificação']:
                    cnae = '859969900'
                    servico = self.env['geracad.nfse.servico'].search([('codigo','=','0802')],limit=1)
                    descricao_nota_servico = 'SERVICO DE ATIVIDADES DE ENSINO'


                # Criar um registro em geracad.nfse
                nfse_vals = {
                    'company_id': rec.company_id.id,
                    'name': _('NFS-e de %s') % rec.sacado.name,
                    'valor_servico': rec.valor_total,
                    'nfse_descricao_nota': _(f'{descricao_nota_servico} Aluno: {rec.aluno_id.name} Sacado: {rec.sacado.name} Parcela: {rec.numero_parcela} Curso: {rec.curso_nome}' ) , 
                    'nfse_descricao_servico':  descricao_nota_servico,
                    'nfse_serviço': servico[0].id,
                    'cliente_id': rec.sacado.id,
                    'aluno_id': rec.aluno_id.id,
                    'nfse_CNAE': cnae,
                    
                    'state':'draft',
                    'description': _(f'Aluno: {rec.aluno_id.name} Sacado: {rec.sacado.name} \n Parcela: {rec.numero_parcela}') , 
                    # Exemplo de código de serviço
                    # Outros campos necessários para geracad.nfse
                }
                nfse_id = self.env['geracad.nfse'].create(nfse_vals)
                
                # Associar a parcela com a NFS-e gerada
                rec.nfse_id = nfse_id.id
                rec.nfse_state = "Enviando"

                # Chamar o método para gerar a NFS-e
                #nfse_id.action_gerar_nfse()

    def action_go_nfse(self):

        _logger.info("action open nfse")
        
        return {
            'name': _('NFSe'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'form',
            'res_model': 'geracad.nfse',
            'res_id': self.nfse_id.id,
            'context': {
                'default_id': self.nfse_id.id,
     
            }
            
        }