from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError


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
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
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
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You can only open installments in the draft state."))

            if not record.name:
                record.name = self.env['ir.sequence'].next_by_code('installment.name') or _('New')

            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': record.customer_id.id,
                'invoice_date': record.date,
                'invoice_line_ids': [(0, 0, {
                    'name': record.name,
                    # 'account_id': record.account_id.id,
                    'quantity': 1.0,
                    'price_unit': record.amount,
                })]
            }
            invoice = self.env['account.move'].create(invoice_vals)
            record.state = 'open'
            return {
                'name': _('Customer Invoice'),
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }


class InstallmentPayment(models.Model):
    _name = 'installment.payment'
    _description = 'Installment Payments'

    installment_id = fields.Many2one('installment.installment', string="Installment", required=True)
    date = fields.Date(string="Payment Date", default=fields.Date.today(), required=True)
    amount = fields.Float(string="Amount Paid", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ],string="State",default='draft')