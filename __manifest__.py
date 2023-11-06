# -*- coding: utf-8 -*-

{
    'name': 'Comex Impormontt',
    'version': '1.23',
    'category': 'General',
    'summary': '',
    'description': 'Modulo de importaciones',
    'author' : 'M.Gah',
    'website': '',
    'depends': ['stock','base','sale','product'],
    'external_dependencies': {
	'python': [
		'suds',
		'PIL',
		'urllib3',
		]
	},
    'data': [
            'security/groups.xml',
            'security/ir.model.access.csv',
            'views/comex.xml'
    ],
    'images': [
            'static/src/img/Insumar_nuble.jpeg'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
