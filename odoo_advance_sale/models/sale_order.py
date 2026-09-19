from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    advance_delivery_id = fields.Many2one(
        'stock.picking', string='Advance Delivery', readonly=True,
        copy=False, ondelete='restrict', check_company=True,
    )
    _sql_constraints = [
        ('advance_delivery_unique', 'UNIQUE(advance_delivery_id)',
         'An Advance Delivery can only generate one sale order.'),
    ]

    @api.constrains('advance_delivery_id', 'is_advance_sale', 'partner_id', 'partner_shipping_id', 'company_id')
    def _check_advance_delivery(self):
        for order in self.filtered('advance_delivery_id'):
            delivery = order.advance_delivery_id
            if (not order.is_advance_sale or not delivery.is_advance_delivery
                    or delivery.state != 'done' or delivery.partner_id != order.partner_shipping_id
                    or delivery.partner_id.commercial_partner_id != order.partner_id.commercial_partner_id
                    or delivery.company_id != order.company_id):
                raise ValidationError(_('The sale must remain linked to its validated Advance Delivery and customer.'))

    def write(self, vals):
        if 'advance_delivery_id' in vals:
            raise ValidationError(_('The source Advance Delivery cannot be changed.'))
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_advance_delivery(self):
        if self.filtered('advance_delivery_id'):
            raise ValidationError(_('A sale generated from a completed delivery cannot be deleted.'))

    is_advance_sale = fields.Boolean(
        string='Advance Sale', default=False, tracking=True, index=True,
        help='Identifies orders handled through the Advance Sales entry point.',
    )

    def action_convert_to_advance_sale(self):
        self.ensure_one()
        if self.state not in ('draft', 'sent') or self.locked:
            raise ValidationError(_(
                'Only unlocked draft or sent quotations can be converted to Advance Sale.'
            ))
        self.write({'is_advance_sale': True})
        return True
