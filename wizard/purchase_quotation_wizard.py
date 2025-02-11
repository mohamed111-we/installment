from odoo import models, fields, api

class PurchaseQuotationWizard(models.TransientModel):
    _name = 'purchase.quotation.wizard'
    _description = 'Create RFQ from Purchase Request'

    product_ids = fields.One2many('purchase.quotation.product.wizard', 'wizard_id', string='Products')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)

    def action_create_rfq(self):
        self.ensure_one()
        order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'partner_ref': "Vendor Reference 001",
        })
        for line in self.product_ids:
            self.env['purchase.order.line'].create({
                'order_id': order.id,
                'product_id': line.product_id.id,
                'name': line.description,
                'product_qty': line.quantity,
                'product_uom': line.uom_id.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': order.id,
            'target': 'current',
        }


class PurchaseQuotationProductWizard(models.TransientModel):
    _name = 'purchase.quotation.product.wizard'
    _description = 'Purchase Quotation Product Wizard'

    wizard_id = fields.Many2one('purchase.quotation.wizard', string='Wizard Reference', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='UOM', required=True)

