{
    'name': 'Catastro Contribuyentes',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Módulo para la gestión del padrón de contribuyentes de catastro',
    'description': "Extensión del modelo res.partner para Catastro",
    'depends': ['base', 'contacts'],
    'data': [
        'data/sequence.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
