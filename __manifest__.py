# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Installment',
    'version': '17.0',
    'category': 'Finance/Installments',
    'summary': 'Customer Installment and Payment Management',
    'description': """
    This module provides features for managing customer installments and payments,
     including invoice generation, payment tracking, and reporting.
      It allows for efficient handling of installment plans, partial and full payments,
       and provides insights through advanced analytics.
    """,
    'depends': ['base', 'mail', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/installment_view.xml',
        'views/sale_order.xml',
        'views/purchase_request_view.xml',
        'views/approval_request_view.xml',

        'wizard/installment_payment_wizard.xml',
        'wizard/purchase_quotation_wizard.xml',


        'report/purchase_request_report.xml',

    ],
    'demo': [],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,

}
