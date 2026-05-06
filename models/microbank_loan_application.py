"""
@author: Abraham Arteaga abraham.oohel@gmail.com
@date: 30/03/2026
"""

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

ESTADO_PRESTAMO = [
    ('borrador', 'Borrador'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'Rechazado'),
    ('pagado', 'Pagado')
]


class LoanApplication(models.Model):
    """
    Modelo que representa una solicitud de préstamo y almacena la información
    relacionada con el cliente, el monto y el estado del préstamo, entre otros campos.
    """
    _name = 'microbank.loan.application'
    _description = 'Solicitud de prestamo'
    _rec_name = 'name'

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id
    )
    name = fields.Char(
        string='Numero de solicitud',
        default="New"
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Cliente"
    )
    loan_amount = fields.Monetary(
        string='Monto del préstamo',
        currency_field="currency_id"
    )
    interest_rate = fields.Float(
        string='Tasa de interés anual'
    )
    term_months = fields.Integer(
        string='Plazo en meses'
    )
    state = fields.Selection(
        string='Estado del prestamo',
        selection=ESTADO_PRESTAMO,
        default='borrador'
    )
    monthly_payment = fields.Monetary(
        string='Pago mensual',
        currency_field="currency_id",
        compute="_compute_monthly_payment",
        store=True
    )
    total_to_pay = fields.Monetary(
        string='Total a pagar',
        currency_field="currency_id",
        compute="_compute_total_to_pay",
        store=True
    )
    approval_date = fields.Date(
        string='Fecha de aprobacion'
    )
    next_payment_date = fields.Date(
        string='Fecha del próximo pago'
    )
    loan_payment_ids = fields.One2many(
        comodel_name='microbank.loan.payment',
        inverse_name='loan_id',
        string='Pagos del prestamo'
    )
    progress = fields.Integer(
        string="Progreso de pago",
        compute="_compute_progress"
    )

    @api.depends('loan_amount', 'term_months', 'interest_rate', 'currency_id')
    def _compute_monthly_payment(self):
        """
        Calcula el pago mensual que se debera de pagar por el prestamo
        """
        for rec in self:
            if not rec.term_months or not rec.loan_amount:
                rec.monthly_payment = 0
            else:
                monthly_interest_rate = rec.interest_rate / 12 / 100
                term_months = rec.term_months
                loan_amount = rec.loan_amount

                if monthly_interest_rate == 0:
                    rec.monthly_payment = loan_amount / term_months
                else:
                    rec.monthly_payment = (loan_amount * (
                            monthly_interest_rate * (1 + monthly_interest_rate) ** term_months)) / (
                                                  (1 + monthly_interest_rate) ** term_months - 1)

    @api.depends('monthly_payment', 'term_months')
    def _compute_total_to_pay(self):
        """
        Calcula el monto total a pagar por el prestamo considerando los intereses
        """
        for rec in self:
            rec.total_to_pay = rec.monthly_payment * rec.term_months

    @api.depends('total_to_pay', 'loan_payment_ids.amount')
    def _compute_progress(self):
        """
        Calcula el progreso de pago del prestamo
        """
        for rec in self:
            sum_payment = sum(rec.loan_payment_ids.mapped('amount'))
            if not rec.total_to_pay:
                rec.progress = 0
            else:
                progress = sum_payment * 100 / rec.total_to_pay
                rec.progress = progress

    @api.constrains('loan_amount')
    def _check_description(self):
        """
        Verifica que el monto del prestamo no exceda el limite permitido
        """
        loan_limit = float(
            self.env['ir.config_parameter']
            .sudo()
            .get_param('microbank.loan_amount_limit', default=10000)
        )
        for record in self:
            if record.loan_amount > loan_limit or record.loan_amount < 0:
                raise ValidationError(f"El monto del prestamo no debe de ser superior a {loan_limit}")

    @api.onchange('approval_date')
    def _onchange_approval_date(self):
        """
        Actualiza next_payment_date cuando aproval_date cambia.
        La fecha del proximo pago es definida como un mes despues de la fecha de aprobacion
        """
        for rec in self:
            if rec.approval_date:
                rec.next_payment_date = rec.approval_date + relativedelta(months=1)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobreescribe al método create para:
            - Generar la secuencia que se usara para el campo 'name' del prestamo

        :param dict vals_list: Campos a crear
        :return: Registros creados de la clase
        :rtype: microbank.loan.application
        """
        for vals in vals_list:
            vals['name'] = self._generate_name(vals)
        return super().create(vals_list)

    def write(self, vals):
        """
            Sobreescribe al método write para:
                - Enviar un correo al cliente cuando su prestamo sea aprobado o rechazado

            :param dict vals: Campos a modificar para todos los registros
            :return: True para indicar que la actualizacion de los registros fue un exito
            :rtype: bool
            """
        old_states = {rec.id: rec.state for rec in self}
        res = super().write(vals)
        if 'state' in vals:
            for rec in self:
                self._send_email(rec, old_states[rec.id])
        return res

    def action_aprobar(self):
        """
        Cambia el estado del prestamo de 'borrador' a 'aprobado' y descarga el contrato de prestamo asociado
        """
        for rec in self:
            rec.state = 'aprobado'
            return self.env.ref('microbank.action_report_loan_application_contract').report_action(self)

    def action_pagar(self):
        """
        Cambia el estado del prestamo de 'aprobado' a 'pagado'
        """
        for rec in self:
            rec.state = 'pagado'

    def action_rechazar(self):
        """
        Cambia el estado del prestamo de 'borrador' a 'rechazado'
        """
        for rec in self:
            rec.state = 'rechazado'

    def _generate_name(self, vals):
        if not vals.get('name') or vals['name'] == 'New':
            return self.env['ir.sequence'].next_by_code('loan.application')
        return vals.get('name')

    def _send_email(self, rec, old_state):
        if old_state != rec.state:
            if rec.state == 'aprobado':
                template = self.env.ref(
                    'microbank.mail_template_loan_application_approved'
                )
                template.send_mail(rec.id, force_send=True)
            elif rec.state == 'rechazado':
                template = self.env.ref(
                    'microbank.mail_template_loan_application_rejected'
                )
                template.send_mail(rec.id, force_send=True)
