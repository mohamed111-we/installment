from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class Installment(models.Model):
    _name = "installment.installment"
    _description = 'Customer Installments'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference = fields.Char(string='Reference', copy=False, readonly=True, default=lambda x: _('New'))
    name = fields.Char(string='Name')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
    ], string='Status', required=True, default='draft')
    date = fields.Date(string='Date', default=fields.Date.today())
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    months = fields.Integer()
    account_id = fields.Many2one('account.account', string="Account")
    amount = fields.Float(string='Amount', required=True)
    notes = fields.Text(string='Notes')
    payment_ids = fields.One2many('installment.payment', 'installment_id', string='Payments')

    @api.constrains('amount')
    def check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("The amount must be a positive value."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals['reference'] == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('installment.installment') or _('New')
        return super(Installment, self).create(vals_list)

    def action_draft(self):
        self.state = 'open'
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': self.date,
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'quantity': 1.0,
                'price_unit': self.amount,
            })]
        })
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_installment_line(self):
        if self.months == 0:
            raise ValidationError("The number of months must be greater than zero.")
        for x in range(self.months):
            value = self.amount / self.months
            self.env['installment.payment'].create({
                'date': fields.Date.today() + relativedelta(months=x),
                'amount': value,
                'installment_id': self.id
            })




class InstallmentPayment(models.Model):
    _name = 'installment.payment'
    _description = 'Installment Payments'

    installment_id = fields.Many2one('installment.installment', string="Installment")
    date = fields.Date(string="Payment Date", default=fields.Date.today(), required=True)
    amount = fields.Float(string="Amount", required=True)
    amount_paid = fields.Float(string="Amount Paid")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid_in_full', 'Paid in full'),
        ('partial_payment', 'Partial payment'),
    ], string="State", default='draft')

    def action_paid_in_full(self):
        for rec in self:
            if rec.amount >= rec.amount_paid:
                rec.state = 'paid_in_full'
                rec.amount_paid = rec.amount

    def action_partial_payment(self):
        return {
            'name': 'Partial Payment',
            'view_mode': 'form',
            'res_model': 'installment.payment.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'default_name': self.installment_id.name,
                'default_customer_id': self.installment_id.customer_id.id,
                'default_amount': self.amount
            }
        }

