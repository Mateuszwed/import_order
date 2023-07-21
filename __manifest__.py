{
    "name" : "Import Order from CSV file",
    "author" : "Mateusz Szwed",
    "website": "mateusz-szwed.pl",
    "support": "support@softhealer.com",
    "category": "Sales",
    "description": """Import zamówień z pliku CSV """,
    "version": "15.0.2",
    "depends": [
        "sale_management",
        "order_message",
    ],
    "application": True,
    "data": [
        'security/import_order_security.xml',
        'security/ir.model.access.csv',
        'wizard/import_order_wizard.xml',
        'views/sale_view.xml',
    ],
    'external_dependencies': {
        'python': ['xlrd'],
    },
    "license": "OPL-1",
    "auto_install": False,
    "installable": True,
}
