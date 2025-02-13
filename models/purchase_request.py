from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _name = 'purchase.purchase'
    _description = 'Purchase Request'
    _rec_name = 'employee_id'

    reference = fields.Char(string='Reference', copy=False, readonly=True, required=True, default=lambda x: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', )
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False,
                                 default=lambda self: self.env.company)
    date = fields.Date(string="Date ", required=True)
    manager_id = fields.Many2one('res.users', string=" Department Manager")
    responsible_id = fields.Many2one('res.users', string="Responsible")
    deadline = fields.Date(string="Deadline", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('department_approval', 'To Department Approval'),
        ('hr_approval', 'To HR Approval'),
        ('approved', 'Approved')
    ], string='Status', default='draft')
    department_approval_by = fields.Many2one('res.users', string="Department Approval By")
    department_approval_on = fields.Datetime(string="Department Approval On")
    hr_approval_by = fields.Many2one('res.users', string="Hr Approval By")
    hr_approval_on = fields.Datetime(string="Hr Approval On")
    product_ids = fields.One2many('purchase.product', 'purchase_id', string='Product')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals['reference'] == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('purchase.purchase') or _('New')
        return super(PurchaseRequest, self).create(vals_list)

    @api.constrains('deadline')
    def _check_deadline(self):
        for rec in self:
            if rec.deadline and rec.deadline < rec.date:
                raise ValidationError("Deadline must be greater than the selected date.")

    def action_department_approval(self):
        for rec in self:
            rec.state = 'department_approval'
            rec.department_approval_by = rec.env.user
            rec.department_approval_on = fields.Datetime.now()

    def action_hr_approval(self):
        for rec in self:
            rec.state = 'hr_approval'
            rec.hr_approval_by = rec.env.user
            rec.hr_approval_on = fields.Datetime.now()

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'

    def action_request_smart_button(self):
        return {
            'name': 'Requests for Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {'default_purchase_id': self.id},
            'domain': [('purchase_id', '=', self.id)],
        }

    def action_create_request_for_quotation(self):
        self.ensure_one()
        return {
            'name': 'Create Request For Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.quotation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_ids': [(0, 0, {
                    'product_id': rec.product_id.id,
                    'description': rec.description,
                    'quantity': rec.quantity,
                    'uom_id': rec.uom_id.id,
                }) for rec in self.product_ids]
            },
        }

class PurchaseProduct(models.Model):
    _name = 'purchase.product'
    _description = 'Purchase Product'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='UOM', required=True, )
    purchase_id = fields.Many2one('purchase.purchase', string='Purchase Request', required=True)
