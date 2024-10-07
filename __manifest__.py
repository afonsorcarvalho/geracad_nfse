# -*- coding: utf-8 -*-
{
    'name': "Gerenciador de Cursos - NFSE",

    'summary': """
        Modulo para emissão NFSE""",

    'description': """
        Modulo de emissão de NFSE do Geracad
    """,

    'author': "Netcom Treinamentos e Soluções Tecnológicas",
    'website': "http://www.netcom-ma.com.br",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Academico',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'geracad_curso', 
        
        ],

    # always loaded
    'data': [
        'security/geracad_nfse_security.xml',
        'security/ir.model.access.csv',
        #'data/sequence.xml',
        #'data/mail_template.xml',
        #'views/geracad',
        'views/geracad_curso_financeiro_parcelas_inherit_view.xml',
        'views/geracad_nfse_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
