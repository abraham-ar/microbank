"""
@author: Abraham Arteaga abraham.oohel@gmail.com
@date: 30/03/2026
"""
from odoo import api, fields, models

class ResPartner(models.Model):
    """
    Extiende el modelo res.partner para agregar información
    relacionada con los préstamos de los clientes.
    """
    _inherit = 'res.partner'

    loan_count = fields.Integer(
        string='Numero de prestamos',
        compute="_compute_loan_amount",
        store=True
    )
    total_loan_amount = fields.Float(
        string='Monto total de prestamos',
        compute="_compute_total_loan_amount",
        store=True
    )
    loan_ids = fields.One2many(
        comodel_name='microbank.loan.application',
        inverse_name='partner_id',
        string='Prestamos'
    )

    @api.depends('loan_ids')
    def _compute_loan_count(self):
        """
        Calcula el numero total de prestamos asociados al cliente
        """
        for rec in self:
            rec.loan_count = len(rec.loan_ids)

    @api.depends('loan_ids.loan_amount')
    def _compute_total_loan_amount(self):
        """
        Calcula el monto total que representan los prestamos asociados al cliente
        """
        for rec in self:
            rec.total_loan_amount = sum(rec.loan_ids.mapped('loan_amount'))


