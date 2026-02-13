# -*- coding: utf-8 -*-
"""
Controller para receber webhooks da Focus NFSe
Documentação: https://focusnfe.com.br/doc/
"""

import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class FocusNFSeWebhookController(http.Controller):
    """
    Controller para processar webhooks da Focus NFSe.
    
    A Focus NFSe envia notificações automáticas quando:
    - Uma NFS-e é autorizada
    - Uma NFS-e é rejeitada
    - Uma NFS-e sofre alteração de status
    
    URL do webhook: /focusnfe/webhook
    Método: POST
    Content-Type: application/json
    """

    @http.route('/focusnfe/webhook', type='json', auth='none', methods=['POST'], csrf=False)
    def receive_webhook(self, **kwargs):
        """
        Recebe e processa webhooks da Focus NFSe.
        
        Payload esperado (exemplo):
        {
            "cnpj": "51916585000125",
            "ref": "12345",
            "status": "autorizado",
            "codigo_verificacao": "ABC123",
            "numero": "123",
            "codigo_cancelamento": null,
            "motivo_cancelamento": null
        }
        
        Possíveis status:
        - processando_autorizacao: NFS-e em processamento
        - autorizado: NFS-e autorizada com sucesso
        - erro_autorizacao: Erro na autorização
        - cancelado: NFS-e cancelada
        """
        try:
            # Obtém os dados JSON do webhook
            data = request.jsonrequest
            
            _logger.info(f"Webhook recebido da Focus NFSe: {json.dumps(data, indent=2)}")
            
            # Valida se os dados necessários estão presentes
            if not data or 'ref' not in data:
                _logger.error("Webhook sem dados ou sem campo 'ref'")
                return self._response_error("Campo 'ref' é obrigatório")
            
            ref = data.get('ref')
            status = data.get('status')
            
            # Busca a NFS-e pelo identificador do provedor (ref)
            nfse = request.env['geracad.nfse'].sudo().search([
                ('nfse_provider_identifier', '=', ref),
                ('nfse_provider', '=', 'focusnfe')
            ], limit=1)
            
            if not nfse:
                _logger.warning(f"NFS-e não encontrada para ref: {ref}")
                return self._response_error(f"NFS-e não encontrada para ref: {ref}")
            
            # Processa o webhook baseado no status
            result = self._process_webhook_status(nfse, data)
            
            _logger.info(f"Webhook processado com sucesso para NFS-e {nfse.id} (ref: {ref})")
            
            return self._response_success(result)
            
        except Exception as e:
            _logger.exception(f"Erro ao processar webhook da Focus NFSe: {str(e)}")
            return self._response_error(f"Erro interno: {str(e)}")

    def _process_webhook_status(self, nfse, data):
        """
        Processa o webhook baseado no status recebido.
        
        :param nfse: Registro da NFS-e
        :param data: Dados do webhook
        :return: Dicionário com resultado do processamento
        """
        status = data.get('status')
        numero = data.get('numero')
        codigo_verificacao = data.get('codigo_verificacao')
        
        _logger.info(f"Processando webhook - NFS-e ID: {nfse.id}, Status: {status}")
        
        # Registra a resposta da API
        # O campo data_resposta tem default=fields.Datetime.now, será preenchido automaticamente
        nfse.resposta_api_ids.create({
            'nfse_id': nfse.id,
            'resposta': json.dumps(data, indent=2, ensure_ascii=False),
            'state': self._map_status_to_state(status)
        })
        
        # Processa baseado no status
        if status == 'autorizado':
            return self._process_authorized(nfse, data)
        elif status == 'processando_autorizacao':
            return self._process_processing(nfse, data)
        elif status == 'erro_autorizacao':
            return self._process_error(nfse, data)
        elif status == 'cancelado':
            return self._process_cancelled(nfse, data)
        else:
            _logger.warning(f"Status desconhecido recebido no webhook: {status}")
            return {'message': f'Status {status} processado'}

    def _process_authorized(self, nfse, data):
        """
        Processa webhook de NFS-e autorizada.
        Atualiza o registro e faz a consulta completa da nota.
        """
        numero = data.get('numero')
        codigo_verificacao = data.get('codigo_verificacao')
        
        _logger.info(f"NFS-e {nfse.id} autorizada. Número: {numero}")
        
        # Atualiza os dados básicos
        vals = {
            'state': 'em_processamento',
        }
        
        if numero:
            vals['name'] = str(numero)
        
        nfse.write(vals)
        
        # Faz a consulta completa da NFS-e para obter PDF e XML
        try:
            _logger.info(f"Consultando NFS-e {nfse.id} após autorização via webhook")
            nfse.action_get_nfse()
            return {
                'message': 'NFS-e autorizada e consultada com sucesso',
                'numero': numero,
                'codigo_verificacao': codigo_verificacao
            }
        except Exception as e:
            _logger.error(f"Erro ao consultar NFS-e após webhook: {str(e)}")
            return {
                'message': 'NFS-e autorizada, mas erro na consulta',
                'error': str(e)
            }

    def _process_processing(self, nfse, data):
        """Processa webhook de NFS-e em processamento"""
        _logger.info(f"NFS-e {nfse.id} em processamento")
        
        nfse.write({
            'state': 'em_processamento'
        })
        
        return {'message': 'NFS-e em processamento'}

    def _process_error(self, nfse, data):
        """Processa webhook de erro na autorização"""
        mensagem_erro = data.get('mensagem_sefaz') or data.get('mensagem') or 'Erro desconhecido'
        
        _logger.error(f"Erro na autorização da NFS-e {nfse.id}: {mensagem_erro}")
        
        nfse.write({
            'state': 'erro'
        })
        
        return {
            'message': 'Erro na autorização da NFS-e',
            'error': mensagem_erro
        }

    def _process_cancelled(self, nfse, data):
        """Processa webhook de NFS-e cancelada"""
        motivo = data.get('motivo_cancelamento', 'Não informado')
        
        _logger.info(f"NFS-e {nfse.id} cancelada. Motivo: {motivo}")
        
        # Nota: Você pode adicionar um campo para cancelamento se necessário
        # Por enquanto, vamos registrar apenas no log
        
        return {
            'message': 'NFS-e cancelada',
            'motivo': motivo
        }

    def _map_status_to_state(self, status):
        """
        Mapeia o status do webhook para o estado da resposta da API
        """
        mapping = {
            'autorizado': 'sucesso',
            'processando_autorizacao': 'processando',
            'erro_autorizacao': 'erro',
            'cancelado': 'sucesso'
        }
        return mapping.get(status, 'processando')

    def _response_success(self, data=None):
        """Retorna resposta de sucesso para o webhook"""
        return {
            'status': 'success',
            'data': data or {}
        }

    def _response_error(self, message):
        """Retorna resposta de erro para o webhook"""
        return {
            'status': 'error',
            'message': message
        }


    @http.route('/focusnfe/webhook/test', type='http', auth='none', methods=['GET'], csrf=False)
    def test_webhook(self, **kwargs):
        """
        Endpoint de teste para verificar se o webhook está acessível.
        URL: /focusnfe/webhook/test
        """
        return Response(
            json.dumps({
                'status': 'ok',
                'message': 'Webhook da Focus NFSe está funcionando',
                'version': '1.0.0'
            }),
            content_type='application/json',
            status=200
        )

