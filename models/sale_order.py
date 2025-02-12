from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    user = fields.Char(string="Confirmed By", readonly=True)
    user_ids = fields.Many2many('res.users', string="Users")
    is_boolean_field = fields.Boolean(compute="_compute_is_boolean_field")
    new_products_ids = fields.One2many("sale.order.line", "order_id", string="New Products",
                                       compute="_compute_new_products_ids")

    @api.depends("order_line.product_id.purchase_ok")
    def _compute_new_products_ids(self):
        for rec in self:
            rec.new_products_ids = rec.order_line.filtered(lambda a: a.product_id.purchase_ok)
            # rec.new_products_ids = rec.order_line.filtered('product_id.purchase_ok') without lambda

    def _compute_is_boolean_field(self):
        for rec in self:
            rec.is_boolean_field = not rec.env.user.has_group("installment.user_have_confirm")

    # def action_confirm(self):
    #     for rec in self:
    #         rec.user = rec.env.user.name
    #         if rec.env.user not in rec.user_ids:
    #             raise ValidationError("Only assigned users can confirm.")

    # def action_confirm(self):
    #     super(SaleOrder, self).action_confirm()
    #     # إنشاء فاتورة مرتبطة بأمر البيع
    #     invoice = self._create_invoices()
    #     # تأكيد الفاتورة (نشرها)
    #     invoice.action_post()
    #
    #     # تسجيل دفعة الدفع تلقائيًا
    #     payment_register = self.env['account.payment.register'].with_context(
    #         active_model='account.move', active_ids=invoice.ids
    #     ).create({
    #         'payment_date': invoice.date,
    #     })._create_payments()
    #
    #     return {
    #         'name': _('Customer Invoice'),
    #         'view_mode': 'form',
    #         'res_model': 'account.payment',
    #         'res_id': payment_register.id,
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #     }

# -----------------------------------------------------------------------------------------------------------------------
# print(rec.env.user)                             # res.users(2,)
# print(rec.env.user.name)                        # Mitchell Admin
# print(rec.env.user.id)                          # 2
# print(rec.env.user.login)                       # room
# print(rec.env.user.company_id)                  # res.company(1,)
# print(rec.env.user.email)                       # admin@yourcompany.example.com
# print(rec.env.user.lang )                       # en_US

# self.env.user                                     ==>>   سجل المستخدم الحالي
# self.env.user.name                                                ==>>   اسم المستخدم.
# self.env.user.id = self.env.user.id                               ==>>      ID المستخدم.
# self.env.user.login                                               ==>>  اسم تسجيل الدخول للمستخدم.
# self.env.user.company_id                                          ==>>    الشركة المرتبطة بالمستخدم
# self.env.user.email                                               ==>>   ايميل المستخدم.
# self.env.user.lang                                                ==>>   لغة المستخدم .

# -----------------------------------------------------------------------------------------------------------------------
# عند اختيار المستخدم تلقائي يتحدد الشركه الخاصه بيه وبناءا ع الشركه بتحدد العمله الخاصه بالشركه ويظهر شكل العمله قبل المبلغ
# user_id = fields.Many2one('res.users')
# company_id = fields.Many2one('res.company', string='Company',related='lawyer_id.company_id')
# currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
# price = fields.Monetary(currency_field='currency_id')
#                                               EX
# user_id = Mitchell Admin
# company_id = YourCompany
# currency_id =  EGP
# price =   LE 150
# -----------------------------------------------------------------------------------------------------------------------
# إنشاء فاتورة مرتبطة بأمر البيع
# invoice = self._create_invoices()
## تأكيد الفاتورة (نشرها)
#invoice.action_post()
#
#     # تسجيل دفعة الدفع تلقائيًا
#     payment_register = self.env['account.payment.register'].with_context(
#         active_model='account.move', active_ids=invoice.ids
#     ).create({
#         'payment_date': invoice.date,
#     })._create_payments()
