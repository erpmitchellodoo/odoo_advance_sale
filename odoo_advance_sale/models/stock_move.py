from odoo import models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        if 'sale_line_id' in vals and any(
            move.sale_line_id.advance_move_id == move
            and vals['sale_line_id'] != move.sale_line_id.id for move in self
        ):
            raise ValidationError(_('An Advance Delivery move cannot be disconnected from its generated sale line.'))
        return super().write(vals)
