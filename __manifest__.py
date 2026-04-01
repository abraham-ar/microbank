{
    'name': 'MicroBank',
    'version': '19.0.1.0',
    'summary': 'Módulo de gestión prestamos',
    'author': 'Oohel Technologies S.A. de C.V.',
    'maintainer': 'Abraham Arteaga <abraham.oohel@gmail.com>',
    'contributors': [
        'Abraham Arteaga <abraham.oohel@gmail.com>',
    ],
    'category': 'Gestion de prestamos',
    'description':
        """
        MicroBank es un módulo para Odoo que permite gestionar préstamos y registrar los pagos asociados. 
        Facilita la creación y administración de solicitudes de préstamo, el seguimiento de los montos otorgados y el control 
        de los abonos realizados por los clientes, permitiendo monitorear el saldo pendiente hasta la liquidación del préstamo.
        """,
    'depends': [
        'base',
        'mail'
    ],
    'data': [
        'security/microbank_groups.xml',
        'security/microbank_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_loan_application_number.xml',
        'data/mail_template_loan_application_approved.xml',
        'data/mail_template_loan_application_rejected.xml',
        'wizard/accept_reject_loan_application/accept_reject_loan_application_views.xml',
        'report/loan_application_contract/loan_application_contract_templates.xml',
        'report/loan_application_contract/loan_application_contract_report.xml',
        'views/res_partner_views.xml',
        'views/microbank_loan_application_views.xml',
        'views/microbank_loan_payment_views.xml',
        'views/microbank_menus.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,  # True solo cuando el modulo es un modulo completo
}
