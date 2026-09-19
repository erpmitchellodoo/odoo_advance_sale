from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    advance_move_id = fields.Many2one(
        'stock.move', string='Advance Delivery Line', readonly=True,
        copy=False, ondelete='restrict', check_company=True,
    )
    _sql_constraints = [
        ('advance_move_unique', 'UNIQUE(advance_move_id)',
         'A delivery line can only generate one sale line.'),
    ]

    @api.constrains('advance_move_id', 'order_id', 'product_id', 'product_uom', 'product_uom_qty')
    def _check_advance_move(self):
        for line in self.filtered('advance_move_id'):
            move = line.advance_move_id
            if (move.state != 'done' or not move.picking_id.is_advance_delivery
                    or move.picking_id != line.order_id.advance_delivery_id
                    or move.product_id != line.product_id
                    or move.product_uom != line.product_uom
                    or float_compare(move.quantity, line.product_uom_qty,
                                     precision_rounding=move.product_uom.rounding)):
                raise ValidationError(_('Generated sale lines must match their validated delivery lines.'))

    def write(self, vals):
        if 'product_uom_qty' in vals:
            for line in self.filtered('advance_move_id'):
                if float_compare(
                    vals['product_uom_qty'], line.product_uom_qty,
                    precision_rounding=line.product_uom.rounding,
                ):
                    raise ValidationError(_(
                        'The quantity of a delivery-generated line cannot be changed. '
                        'Add a new sale line for additional items.'
                    ))
        if 'advance_move_id' in vals and any(
            line.advance_move_id.id != (vals['advance_move_id'] or False) for line in self
        ):
            raise ValidationError(_('The source delivery link cannot be changed.'))
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_advance_delivery(self):
        if self.filtered('advance_move_id'):
            raise ValidationError(_('Delivery-generated lines cannot be deleted. Use a stock return to correct a delivery.'))

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Manual delivery moves have no procurement rule. Exclude their source
        # lines explicitly instead of generating another delivery on confirmation.
        return super(SaleOrderLine, self.filtered(lambda line: not line.advance_move_id))._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty,
        )
