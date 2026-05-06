"""
@author: Abraham Arteaga abraham.oohel@gmail.com
@date: 30/03/2026
"""

from odoo import fields, models

ESTADO_PAGO = [
    ('borrador', 'Borrador'),
    ('confirmado', 'Confirmado'),
    ('cancelado', 'Cancelado')
]


class LoanPayment(models.Model):
    """
    Modelo que representa un pago de un prestamo en concreto y almacena la información
    como el prestamo con el que esta relacionado, la fecha de pago, el monto y el estado del pago
    """
    _name = 'microbank.loan.payment'
    _description = 'Pago de prestamo'
    _rec_name = 'loan_id'

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id
    )
    loan_id = fields.Many2one(
        comodel_name='microbank.loan.application',
        string='Prestamo'
    )
    payment_date = fields.Datetime(
        string='Fecha de Pago'
    )
    amount = fields.Monetary(
        string='Monto pagado',
        currency_field="currency_id"
    )
    state = fields.Selection(
        string='Estado del pago',
        selection=ESTADO_PAGO,
        default='borrador'
    )

    def action_confirmar(self):
        """
        Cambia el estado del pago del prestamo de 'borrador' a 'confirmado'
        """
        for rec in self:
            rec.state = 'confirmado'

    def action_cancelar(self):
        """
        Cambia el estado del pago del prestamo de 'borrador' a 'cancelado'
        """
        for rec in self:
            rec.state = 'cancelado'
