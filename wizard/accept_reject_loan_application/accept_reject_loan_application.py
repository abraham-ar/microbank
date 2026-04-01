"""
@author: Abraham Arteaga abraham.oohel@gmail.com
@date: 30/03/2026
"""
from odoo import api, fields, models

class LoanApplication(models.TransientModel):
    """
    Modelo transitorio creado para aprobar o rechazar varias aplicaciones de prestamos a la vez
    """
    _name = 'microbank.loan.application.accept.reject'

    loan_ids = fields.Many2many(
        comodel_name='microbank.loan.application',
        relation='microbank_loan_app_accept_reject_rel',
        column1='wizard_id',
        column2='loan_application_id',
        string="Prestamos para aprobar o rechazar",
        default=lambda self: [(6, 0, self.env.context.get('active_ids', []))]
    )

    def action_aprobar(self):
        """
        Cambia el estado de las aplicaciones de prestamos seleccionadas de 'borrador' a 'aprobado'
        """
        for rec in self.loan_ids:
            rec.state = 'aprobado'

    def action_rechazar(self):
        """
        Cambia el estado de las aplicaciones de prestamos seleccionadas de 'borrador' a 'rechazado'
        """
        for rec in self.loan_ids:
            rec.state = 'rechazado'