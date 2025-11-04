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
        """
        Emite NFS-e a partir de uma parcela recebida.
        Atualizado para usar o novo modelo de CNAE (Many2one).
        """
        for rec in self:
            if rec.state == 'recebido':
                # Verificar se a NFS-e já foi emitida
                if rec.nfse_id:
                    raise UserError(_("A NFS-e já foi emitida para esta parcela."))

                # Determinar o CNAE e descrição baseado no tipo de curso
                cnae_codigo = None
                descricao_nota_servico = ""
                
                type_curso = rec.curso_matricula_id.curso_turma_id.curso_id.type_curso.name
                
                # Mapear tipo de curso para código CNAE
                if type_curso in ['Técnico']:
                    cnae_codigo = '8541400'  # Educação profissional de nível técnico
                    descricao_nota_servico = 'SERVIÇO DE EDUCAÇÃO PROFISSIONAL DE NÍVEL TÉCNICO'
                    
                elif type_curso in ['Superior']:
                    cnae_codigo = '8532500'  # Educação superior - graduação e pós-graduação
                    descricao_nota_servico = 'SERVIÇO DE EDUCAÇÃO SUPERIOR - GRADUAÇÃO E PÓS-GRADUAÇÃO'
                    
                elif type_curso in ['Preparatório', 'Qualificação']:
                    cnae_codigo = '8599603'  # Treinamento em informática / outras atividades de ensino
                    descricao_nota_servico = 'SERVIÇO DE TREINAMENTO E INSTRUÇÃO'
                    
                else:
                    # CNAE genérico para outros tipos de ensino
                    cnae_codigo = '8599603'
                    descricao_nota_servico = 'SERVIÇO DE ATIVIDADES DE ENSINO'
                    _logger.warning(f"Tipo de curso '{type_curso}' não mapeado. Usando CNAE genérico.")
                
                # Buscar o CNAE no banco de dados
                cnae_record = self.env['geracad.nfse.cnae'].search([
                    ('codigo', '=', cnae_codigo)
                ], limit=1)
                
                if not cnae_record:
                    raise UserError(_(
                        f"CNAE {cnae_codigo} não encontrado no sistema.\n"
                        f"Por favor, cadastre o CNAE em: NFS-e → Configuração → CNAEs"
                    ))
                
                # Formatar data de pagamento
                data_pagamento_str = ''
                if rec.data_pagamento:
                    data_pagamento_str = rec.data_pagamento.strftime('%d/%m/%Y')
                
                # Criar um registro de NFS-e
                # O campo nfse_serviço será preenchido automaticamente pelo CNAE (related field)
                nfse_vals = {
                    'company_id': rec.company_id.id,
                    'name': _('NFS-e de %s') % rec.sacado.name,
                    'valor_servico': rec.valor_total,
                    'nfse_descricao_nota': _(
                        f'{descricao_nota_servico}\n'
                        f'Aluno: {rec.aluno_id.name}\n'
                        f'Sacado: {rec.sacado.name}\n'
                        f'Parcela: {rec.numero_parcela}\n'
                        f'Curso: {rec.curso_nome}\n'
                        f'Data de Pagamento: {data_pagamento_str}'
                    ),
                    'nfse_descricao_servico': descricao_nota_servico,
                    'nfse_CNAE': cnae_record.id,  # Agora é Many2one, não string
                    # nfse_serviço será preenchido automaticamente pelo related field
                    'cliente_id': rec.sacado.id,
                    'aluno_id': rec.aluno_id.id,
                    'state': 'draft',
                }
                
                try:
                    nfse_id = self.env['geracad.nfse'].create(nfse_vals)
                    
                    # Associar a parcela com a NFS-e gerada
                    rec.write({
                        'nfse_id': nfse_id.id,
                        'nfse_state': 'Rascunho'
                    })
                    
                    _logger.info(
                        f"NFS-e {nfse_id.id} criada para parcela {rec.id}. "
                        f"CNAE: {cnae_codigo} - {cnae_record.name}"
                    )
                    
                except Exception as e:
                    _logger.error(f"Erro ao criar NFS-e para parcela {rec.id}: {str(e)}")
                    raise UserError(_(f"Erro ao criar NFS-e: {str(e)}"))

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