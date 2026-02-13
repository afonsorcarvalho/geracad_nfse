# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class GeracadNfseCancelWizard(models.TransientModel):
    """
    Wizard para cancelamento de NFS-e.
    Solicita justificativa conforme exigência da FocusNFe (15 a 255 caracteres).
    """
    _name = 'geracad.nfse.cancel.wizard'
    _description = 'Wizard de Cancelamento de NFS-e'

    nfse_id = fields.Many2one(
        'geracad.nfse',
        string='NFS-e',
        required=True,
        readonly=True
    )
    referencia = fields.Char(
        string='Referência',
        readonly=True,
        help='Identificador da nota no provedor'
    )
    justificativa = fields.Text(
        string='Justificativa do Cancelamento',
        required=True,
        help='Justificativa do cancelamento (mínimo 15 caracteres, máximo 255 caracteres)'
    )

    @api.constrains('justificativa')
    def _check_justificativa(self):
        """Valida o tamanho da justificativa conforme exigência da FocusNFe."""
        for record in self:
            if record.justificativa:
                justificativa_limpa = record.justificativa.strip()
                if len(justificativa_limpa) < 15:
                    raise UserError(_('A justificativa deve ter no mínimo 15 caracteres.'))
                if len(justificativa_limpa) > 255:
                    raise UserError(_('A justificativa deve ter no máximo 255 caracteres.'))

    def action_confirmar_cancelamento(self):
        """
        Confirma o cancelamento da NFS-e.
        Chama o método de cancelamento no modelo geracad.nfse.
        """
        self.ensure_one()
        
        if not self.justificativa or len(self.justificativa.strip()) < 15:
            raise UserError(_('A justificativa deve ter no mínimo 15 caracteres.'))
        
        if not self.nfse_id:
            raise UserError(_('NFS-e não encontrada.'))
        
        # Chama o método de cancelamento
        try:
            self.nfse_id._cancelar_focus_nfse(self.referencia, self.justificativa)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sucesso'),
                    'message': _('NFS-e cancelada com sucesso!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except UserError:
            raise
        except Exception as e:
            _logger.error('Erro ao cancelar NFS-e: %s', e)
            raise UserError(_('Erro ao cancelar NFS-e: %s') % str(e))

