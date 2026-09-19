from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_advance_delivery = fields.Boolean(string='Advance Delivery', default=False, index=True)

    @api.constrains('is_advance_delivery', 'picking_type_id', 'location_dest_id')
    def _check_advance_delivery_type(self):
        for picking in self.filtered('is_advance_delivery'):
            if picking.picking_type_code != 'outgoing' or picking.location_dest_id.usage != 'customer':
                raise ValidationError(_('Advance Deliveries must be outgoing transfers to a customer.'))

    def write(self, vals):
        if 'partner_id' in vals and any(
            p.is_advance_delivery and p.sale_id and p.partner_id.id != vals['partner_id'] for p in self
        ):
            raise ValidationError(_('The customer of a delivery linked to an Advance Sale cannot change.'))
        if 'is_advance_delivery' in vals and any(
            p.state == 'done' and p.is_advance_delivery != bool(vals['is_advance_delivery']) for p in self
        ):
            raise ValidationError(_('The Advance Delivery classification cannot change after validation.'))
        return super().write(vals)

    def copy_data(self, default=None):
        default = dict(default or {})
        if default.get('return_id'):
            default['is_advance_delivery'] = False
        return super().copy_data(default)

    @api.model
    def action_open_advance_deliveries(self):
        action = self.env['ir.actions.actions']._for_xml_id('odoo_advance_sale.action_advance_deliveries')
        operation = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'), ('company_id', '=', self.env.company.id),
            ('warehouse_id', '!=', False),
        ], limit=1)
        action['context'] = dict(self.env.context, default_is_advance_delivery=True,
                                 restricted_picking_type_code='outgoing',
                                 default_picking_type_id=operation.id)
        return action

    def action_create_advance_sale(self):
        self.ensure_one()
        self.check_access('write')
        # Serialize duplicate clicks without bypassing access or company rules.
        self.env.cr.execute('SELECT id FROM stock_picking WHERE id = %s FOR UPDATE', [self.id])
        self.invalidate_recordset(['sale_id', 'state', 'is_advance_delivery'])
        if not self.is_advance_delivery or self.state != 'done' or self.picking_type_code != 'outgoing':
            raise ValidationError(_('Validate an Advance Delivery before creating its sale order.'))
        existing = self.env['sale.order'].search([('advance_delivery_id', '=', self.id)], limit=1)
        if existing:
            return existing.get_formview_action()
        if self.sale_id or self.move_ids.sale_line_id:
            raise ValidationError(_('This delivery is already linked to a sale order.'))
        if not self.partner_id:
            raise ValidationError(_('Set a customer on the delivery before creating the sale order.'))
        moves = self.move_ids.filtered(lambda m: m.state == 'done' and m.quantity > 0)
        if not moves or any(m.location_dest_id.usage != 'customer' or m.origin_returned_move_id for m in moves):
            raise ValidationError(_('Use a delivery with completed customer delivery lines, not a return.'))
        warehouse = self.picking_type_id.warehouse_id
        if not warehouse:
            raise ValidationError(_('The delivery operation type must belong to a warehouse.'))
        order = self.env['sale.order'].with_company(self.company_id).create({
            'partner_id': self.partner_id.commercial_partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'warehouse_id': warehouse.id,
            'is_advance_sale': True,
            'advance_delivery_id': self.id,
            'origin': self.name,
            'order_line': [Command.create({
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                'product_uom_qty': move.quantity,
                'advance_move_id': move.id,
            }) for move in moves],
        })
        for line in order.order_line:
            line.advance_move_id.sale_line_id = line
        return order.get_formview_action()
