from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAdvanceDelivery(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref('sales_team.group_sale_salesman')
        cls.warehouse = cls.env['stock.warehouse'].search([('company_id', '=', cls.env.company.id)], limit=1)
        cls.product = cls.env['product.product'].create({
            'name': 'Advance delivered item', 'type': 'consu', 'is_storable': True,
            'list_price': 50, 'invoice_policy': 'delivery',
            'property_account_income_id': cls.company_data['default_account_revenue'].id,
            'taxes_id': [Command.clear()],
        })
        cls.env['stock.quant']._update_available_quantity(cls.product, cls.warehouse.lot_stock_id, 100)

    def _delivery(self, done=True, quantity=3):
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_a.id,
            'is_advance_delivery': True,
            'picking_type_id': self.warehouse.out_type_id.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'location_dest_id': self.partner_a.property_stock_customer.id,
            'move_ids': [Command.create({
                'name': self.product.display_name,
                'product_id': self.product.id, 'product_uom': self.product.uom_id.id,
                'product_uom_qty': quantity, 'location_id': self.warehouse.lot_stock_id.id,
                'location_dest_id': self.partner_a.property_stock_customer.id,
            })],
        })
        if done:
            picking.action_confirm()
            picking.action_assign()
            picking.move_ids.quantity = quantity
            picking.move_ids.picked = True
            picking.button_validate()
            self.assertEqual(picking.state, 'done')
        return picking

    def test_delivery_sale_link_no_duplicate_delivery_and_invoicing(self):
        picking = self._delivery()
        action = picking.action_create_advance_sale()
        sale = self.env['sale.order'].browse(action['res_id'])
        self.assertTrue(sale.is_advance_sale)
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.advance_delivery_id, picking)
        self.assertEqual(picking.sale_id, sale)
        self.assertEqual(sale.picking_ids, picking)
        line = sale.order_line
        self.assertEqual(line.advance_move_id, picking.move_ids)
        self.assertEqual(line.product_uom_qty, 3)
        self.assertEqual(line.qty_delivered, 3)
        self.assertEqual(line.price_unit, 50)
        self.assertEqual(picking.action_create_advance_sale()['res_id'], sale.id)
        sale.action_confirm()
        self.assertEqual(sale.picking_ids, picking)
        self.assertEqual(line.qty_to_invoice, 3)
        invoice = sale._create_invoices()
        self.assertEqual(invoice.invoice_line_ids.quantity, 3)
        extra = self.env['sale.order.line'].create({
            'order_id': sale.id, 'product_id': self.product.id, 'product_uom_qty': 2,
        })
        new_delivery = sale.picking_ids - picking
        self.assertEqual(len(new_delivery), 1)
        self.assertEqual(new_delivery.move_ids.sale_line_id, extra)
        self.assertEqual(new_delivery.move_ids.product_uom_qty, 2)
        self.assertFalse(extra.advance_move_id)
        extra.product_uom_qty = 4
        self.assertEqual(extra.product_uom_qty, 4)

    def test_generated_line_delivery_details_cannot_be_changed_or_deleted(self):
        picking = self._delivery()
        sale = self.env['sale.order'].browse(picking.action_create_advance_sale()['res_id'])
        line = sale.order_line
        for vals in ({'product_uom_qty': 4}, {'advance_move_id': False}):
            with self.assertRaises(ValidationError):
                line.write(vals)
        with self.assertRaises(ValidationError):
            line.unlink()
        with self.assertRaises(ValidationError):
            sale.write({'advance_delivery_id': False})
        with self.assertRaises(ValidationError):
            sale.sudo().unlink()
        with self.assertRaises(ValidationError):
            picking.move_ids.write({'sale_line_id': False})

    def test_generated_line_pricing_is_editable(self):
        picking = self._delivery()
        sale = self.env['sale.order'].browse(picking.action_create_advance_sale()['res_id'])
        line = sale.order_line
        tax = self.env['account.tax'].create({
            'name': 'Advance sale test tax', 'amount': 10, 'amount_type': 'percent',
            'type_tax_use': 'sale', 'company_id': sale.company_id.id,
        })
        line.write({'price_unit': 80, 'discount': 10, 'tax_id': [Command.set(tax.ids)],
                    'name': 'Updated commercial description',
                    'product_uom_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'advance_move_id': line.advance_move_id.id})
        self.assertEqual(line.price_subtotal, 216)
        self.assertAlmostEqual(line.price_total, 237.6)
        sale.action_confirm()
        line.price_unit = 100
        self.assertEqual(line.product_uom_qty, 3)
        self.assertEqual(line.qty_delivered, 3)
        self.assertEqual(sale.picking_ids, picking)
        invoice = sale._create_invoices()
        self.assertEqual(invoice.invoice_line_ids.price_unit, 100)
        self.assertEqual(invoice.invoice_line_ids.discount, 10)
        self.assertEqual(invoice.invoice_line_ids.tax_ids, tax)

    def test_extra_line_before_confirmation_and_return(self):
        picking = self._delivery()
        sale = self.env['sale.order'].browse(picking.action_create_advance_sale()['res_id'])
        extra = self.env['sale.order.line'].create({
            'order_id': sale.id, 'product_id': self.product.id, 'product_uom_qty': 2,
        })
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids - picking), 1)
        self.assertEqual((sale.picking_ids - picking).move_ids.sale_line_id, extra)
        wizard = self.env['stock.return.picking'].with_context(
            active_id=picking.id, active_ids=picking.ids, active_model='stock.picking',
        ).create({})
        wizard.product_return_moves.quantity = 1
        action = wizard.action_create_returns()
        returned = self.env['stock.picking'].browse(action['res_id'])
        self.assertFalse(returned.is_advance_delivery)
        returned.move_ids.quantity = 1
        returned.move_ids.picked = True
        returned.button_validate()
        self.assertEqual(returned.state, 'done')
        self.assertEqual(sale.order_line.filtered('advance_move_id').qty_delivered, 2)

    def test_requires_validated_delivery(self):
        picking = self._delivery(done=False)
        with self.assertRaises(ValidationError):
            picking.action_create_advance_sale()

    def test_menu_context_and_standard_defaults(self):
        action = self.env['stock.picking'].action_open_advance_deliveries()
        self.assertTrue(action['context']['default_is_advance_delivery'])
        self.assertEqual(action['context']['default_picking_type_id'], self.warehouse.out_type_id.id)
        self.assertFalse(self.env['stock.picking'].default_get(['is_advance_delivery'])['is_advance_delivery'])
