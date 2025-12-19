# -*- coding: utf-8 -*-
"""
Herança do modelo res.partner para adicionar busca automática de endereço via CEP
usando a API da FocusNFE.

Documentação FocusNFE CEP: https://doc.focusnfe.com.br/reference/consultarceps
"""

import re
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.addons.geracad_nfse.nfse_focusnfe import FocusNFSeAPI

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """
    Herança do res.partner para adicionar busca automática de endereço
    através do CEP usando a API da FocusNFE.
    """
    _inherit = 'res.partner'

    @api.onchange('zip')
    def _onchange_zip(self):
        """
        Busca automaticamente o endereço através do CEP usando a API da FocusNFE.
        Este método é executado quando o campo CEP perde o foco.
        
        Primeiro tenta buscar via API da FocusNFE. Se não encontrar ou houver erro,
        usa o método padrão do l10n_br_base_address como fallback.
        
        Documentação FocusNFE: https://doc.focusnfe.com.br/reference/consultarceps
        """
        # Remove formatação do CEP (mantém apenas números)
        cep = re.sub(r'[^0-9]', '', self.zip or '')
        
        # Valida se o CEP tem 8 dígitos
        if not cep or len(cep) != 8:
            if cep and len(cep) > 0:
                return {
                    'warning': {
                        'title': _('CEP Inválido'),
                        'message': _('O CEP deve conter 8 dígitos. Exemplo: 01001000 ou 01001-000')
                    }
                }
            return
        
        try:
            # Inicializa a API da FocusNFE
            # Usa produção por padrão, mas pode ser configurado via parâmetros do sistema
            focus_api = FocusNFSeAPI(homologacao=False)
            
            # Consulta o CEP na API da FocusNFE
            status_code, response = focus_api.consultar_cep(cep)
            
            # Log da resposta da API para debug
            _logger.info(f'Resposta da API FocusNFE para CEP {cep}: Status={status_code}, Response={response}')
            
            if status_code == 200 and response and not response.get('erro'):
                # Mapeia os dados retornados pela API para os campos do Odoo
                endereco_data = self._mapear_dados_endereco_focusnfe(response, cep)
                
                # Log para debug
                _logger.info(f'Dados mapeados para CEP {cep}: {endereco_data}')
                
                # Atualiza os campos do endereço usando update() do Odoo
                if endereco_data:
                    self.update(endereco_data)
                    
                    # Log após atualização para verificar
                    _logger.info(f'Endereço atualizado via FocusNFE para CEP {cep}: street={self.street}, city={self.city}, city_id={self.city_id}, state_id={self.state_id}')
                    return  # Sucesso, não precisa chamar o método padrão
                else:
                    _logger.warning(f'Nenhum dado de endereço mapeado para CEP {cep}')
            
            # Se não encontrou ou houve erro, tenta usar o método padrão do l10n_br_base_address
            _logger.warning(f'CEP {cep} não encontrado na FocusNFE. Status: {status_code}, Response: {response}')
            
        except Exception as e:
            _logger.error(f'Erro ao consultar CEP {cep} na FocusNFE: {str(e)}', exc_info=True)
        
        # Fallback: chama o método padrão do l10n_br_base_address
        # Verifica se o método existe antes de chamar
        if hasattr(super(ResPartner, self), '_onchange_zip'):
            super(ResPartner, self)._onchange_zip()
    
    def _mapear_dados_endereco_focusnfe(self, response_api, cep):
        """
        Mapeia os dados retornados pela API da FocusNFE para os campos do Odoo.
        
        Estrutura real da resposta da API FocusNFE (conforme logs):
        {
            "cep": "65066190",
            "tipo": "logradouro",
            "nome": "",
            "uf": "MA",
            "nome_localidade": "São Luís",
            "codigo_ibge": "2111300",
            "tipo_logradouro": "Rua",
            "nome_logradouro": "Boa Esperança",
            "bairro": "Turu",
            "descricao": "Rua Boa Esperança, Turu, São Luís, MA"
        }
        
        Args:
            response_api (dict): Resposta da API da FocusNFE
            cep (str): CEP consultado (apenas números)
            
        Returns:
            dict: Dicionário com os campos do endereço mapeados para o Odoo
        """
        # Formata o CEP com hífen (ex: 65066-190)
        cep_formatado = f"{cep[:5]}-{cep[5:]}" if len(cep) == 8 else cep
        
        # Busca o estado pelo código UF
        state = False
        if response_api.get('uf'):
            state = self.env['res.country.state'].search([
                ('country_id.code', '=', 'BR'),
                ('code', '=', response_api.get('uf'))
            ], limit=1)
            if not state:
                _logger.warning(f'Estado não encontrado para UF: {response_api.get("uf")}')
            else:
                _logger.info(f'Estado encontrado: {state.name} (ID: {state.id})')
        
        # Busca a cidade pelo código IBGE ou nome
        city = False
        if state:
            # Tenta buscar pelo código IBGE primeiro (campo correto: codigo_ibge)
            if response_api.get('codigo_ibge'):
                codigo_ibge = str(response_api.get('codigo_ibge'))
                _logger.info(f'Buscando cidade pelo código IBGE: {codigo_ibge}')
                city = self.env['res.city'].search([
                    ('l10n_br_ibge_code', '=', codigo_ibge),
                    ('state_id', '=', state.id)
                ], limit=1)
                if city:
                    _logger.info(f'Cidade encontrada pelo IBGE: {city.name} (ID: {city.id})')
            
            # Se não encontrou pelo código IBGE, busca pelo nome (nome_localidade)
            if not city and response_api.get('nome_localidade'):
                nome_localidade = response_api.get('nome_localidade')
                _logger.info(f'Buscando cidade pelo nome: {nome_localidade} no estado {state.name}')
                city = self.env['res.city'].search([
                    ('name', '=ilike', nome_localidade),
                    ('state_id', '=', state.id)
                ], limit=1)
                if city:
                    _logger.info(f'Cidade encontrada pelo nome: {city.name} (ID: {city.id})')
                else:
                    _logger.warning(f'Cidade não encontrada pelo nome: {nome_localidade} no estado {state.name}')
        else:
            _logger.warning('Estado não encontrado, não é possível buscar a cidade')
        
        # Monta o dicionário com os dados do endereço
        endereco_data = {}
        
        # CEP formatado
        if cep_formatado:
            endereco_data['zip'] = cep_formatado
        
        # Logradouro (street) - monta com tipo_logradouro + nome_logradouro
        nome_logradouro = response_api.get('nome_logradouro') or ''
        tipo_logradouro = response_api.get('tipo_logradouro') or ''
        
        if nome_logradouro:
            # Monta o logradouro completo: "Rua Boa Esperança" ou apenas "Boa Esperança"
            if tipo_logradouro:
                street = f"{tipo_logradouro} {nome_logradouro}".strip()
            else:
                street = nome_logradouro
            endereco_data['street'] = street
            _logger.info(f'Logradouro montado: {street}')
        
        # Bairro
        if response_api.get('bairro'):
            endereco_data['l10n_br_district'] = response_api.get('bairro')
        
        # País (sempre Brasil quando há estado)
        if state and state.country_id:
            endereco_data['country_id'] = state.country_id.id
        
        # Estado
        if state:
            endereco_data['state_id'] = state.id
        
        # Cidade
        if city:
            endereco_data['city_id'] = city.id
            # Atualiza também o campo city (texto) quando city_id é definido
            # Isso é necessário para compatibilidade com o módulo base_address_city
            endereco_data['city'] = city.name
        elif response_api.get('nome_localidade'):
            # Se não encontrou a cidade no banco, pelo menos preenche o campo texto
            endereco_data['city'] = response_api.get('nome_localidade')
            _logger.warning(f'Cidade não encontrada no banco, usando nome da API: {response_api.get("nome_localidade")}')
        
        return endereco_data
