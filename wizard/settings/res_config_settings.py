"""
@author: Abraham Arteaga abraham.oohel@gmail.com
@date: 30/03/2026
"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    Herencia de res.config.settings para hacer configurable el limite del monto de prestamos
    """
    _inherit = 'res.config.settings'

    loan_amount_limit = fields.Float(
        string="Loan amount Limit",
        config_parameter="microbank.loan_amount_limit",
        default=100000
    )
