from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class InstallmentPaymentWizard(models.TransientModel):
    _name = 'installment.payment.wizard'
    _description = 'Installment Payment Wizard'

    name = fields.Char(string='Name')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    amount = fields.Float(string="Amount", required=True)
    amount_paid = fields.Float(string="Amount Paid")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid_in_full', 'Paid in full'),
        ('partial_payment', 'Partial payment'),
    ], string="State", default='draft')

    def action_confirm_partial_payment(self):
        payment_line = self.env['installment.payment'].browse(self._context.get('active_id'))  # for wizard
        payments_lines = self.env['installment.payment'].search([
            ('installment_id', '=', payment_line.installment_id.id),
            ('state', '!=', 'paid_in_full'),
        ], order="date asc")  # order="id asc"
        for x in payments_lines:
            result = x.amount - x.amount_paid
            if self.amount_paid >= result:
                x.amount_paid = x.amount
                self.amount_paid = self.amount_paid - result
                x.state = 'paid_in_full'
            else:
                x.amount_paid = x.amount_paid + self.amount_paid
                x.state = 'partial_payment'
                self.amount_paid = 0

            if self.amount_paid <= 0:
                break
