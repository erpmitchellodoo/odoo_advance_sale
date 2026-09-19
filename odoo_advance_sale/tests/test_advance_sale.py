from lxml import etree

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged('post_install', '-at_install')
class TestAdvanceSale(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Advance Sale Test'})
        cls.Order = cls.env['sale.order']

    def _order(self, advance=False, **values):
        return self.Order.create({
            'partner_id': self.partner.id, 'is_advance_sale': advance, **values,
        })

    def test_menu_defaults_and_domain(self):
        action = self.env.ref('odoo_advance_sale.action_advance_sales')
        normal = self.Order.create({'partner_id': self.partner.id})
        advance = self.Order.with_context(safe_eval(action.context)).create({'partner_id': self.partner.id})
        self.assertFalse(normal.is_advance_sale)
        self.assertTrue(advance.is_advance_sale)
        found = self.Order.search(safe_eval(action.domain))
        self.assertIn(advance, found)
        self.assertNotIn(normal, found)
        advance.is_advance_sale = False
        self.assertNotIn(advance, self.Order.search(safe_eval(action.domain)))
        self.assertEqual(action.res_model, 'sale.order')
        self.assertEqual(action.view_id, self.env.ref('sale.view_quotation_tree'))
        self.assertEqual(self.env.ref('odoo_advance_sale.menu_advance_sales').parent_id,
                         self.env.ref('sale.sale_order_menu'))

    def test_draft_and_sent_are_editable(self):
        order = self._order()
        for state in ('draft', 'sent'):
            order.state = state
            order.is_advance_sale = True
            self.assertTrue(order.is_advance_sale)
            order.is_advance_sale = False
            self.assertFalse(order.is_advance_sale)

    def test_convert_to_advance_sale_button(self):
        for state in ('draft', 'sent'):
            order = self._order(state=state)
            order.action_convert_to_advance_sale()
            self.assertTrue(order.is_advance_sale)
            self.assertEqual(order.state, state)
        for values in ({'state': 'sale'}, {'state': 'cancel'}, {'locked': True}):
            order = self._order(**values)
            with self.assertRaises(ValidationError):
                order.action_convert_to_advance_sale()
            self.assertFalse(order.is_advance_sale)

    def test_confirmation_prevents_both_classification_changes(self):
        for advance in (False, True):
            order = self._order(advance)
            order.action_confirm()
            self.assertEqual(order.state, 'sale')
            self.assertTrue(order.advance_sale_classification_locked)
            with self.assertRaises(ValidationError):
                order.write({'is_advance_sale': not advance})
            order.write({'is_advance_sale': advance, 'client_order_ref': 'Allowed'})
            self.assertEqual(order.client_order_ref, 'Allowed')
            order.action_lock()
            with self.assertRaises(ValidationError):
                order.write({'is_advance_sale': not advance})
            order.action_unlock()
            with self.assertRaises(ValidationError):
                order.write({'is_advance_sale': not advance})

    def test_reset_cannot_bypass_confirmation_lock(self):
        order = self._order(True)
        order.action_confirm()
        order.with_context(disable_cancel_warning=True).action_cancel()
        order.action_draft()
        self.assertEqual(order.state, 'draft')
        with self.assertRaises(ValidationError):
            order.write({'is_advance_sale': False})
        with self.assertRaises(ValidationError):
            order.write({'advance_sale_classification_locked': False})
        duplicate = order.copy()
        self.assertFalse(duplicate.advance_sale_classification_locked)
        duplicate.is_advance_sale = False

    def test_batch_and_combined_state_write_cannot_bypass_lock(self):
        draft = self._order()
        confirmed = self._order()
        confirmed.action_confirm()
        with self.assertRaises(ValidationError):
            (draft | confirmed).write({'is_advance_sale': True})
        self.assertFalse(draft.is_advance_sale)
        with self.assertRaises(ValidationError):
            confirmed.write({'state': 'draft', 'is_advance_sale': True})
        (draft | confirmed).write({'client_order_ref': 'Batch update'})
        self.assertEqual(draft.client_order_ref, 'Batch update')
        self.assertEqual(confirmed.client_order_ref, 'Batch update')

    def test_created_confirmed_order_is_protected(self):
        order = self._order(True, state='sale', advance_sale_classification_locked=False)
        with self.assertRaises(ValidationError):
            order.write({'is_advance_sale': False})

    def test_form_field_and_ribbon(self):
        arch = etree.fromstring(self.Order.get_view(
            view_id=self.env.ref('sale.view_order_form').id, view_type='form',
        )['arch'])
        field = arch.xpath("//page[@name='other_information']//field[@name='is_advance_sale']")[0]
        self.assertIn('advance_sale_classification_locked', field.get('readonly'))
        ribbon = arch.xpath("//widget[@name='web_ribbon'][@title='ADVANCE SALE']")[0]
        self.assertEqual(ribbon.get('invisible'), 'not is_advance_sale')
