{
    'name': 'Advance Sale Delivery',
    'version': '17.0.2.0.1',
    'summary': 'Deliver goods first, then create a linked Advance Sale with protected quantities and editable pricing',
    'description': '''
Advance Sale Delivery for Odoo 17
================================

Start in Inventory when goods need to reach the customer before a sales order
is created. Validate an Advance Delivery, then generate a linked Advance Sale
quotation from the actual delivered products and quantities.

Delivery-first workflow
----------------------
* Inventory > Operations > Advance Deliveries: create and validate deliveries.
* Create Advance Sale: generate a draft quotation from a completed delivery.
* Keep the original delivery linked through standard Odoo stock moves.
* Protect delivered quantities while editing prices, discounts and taxes
  according to standard Odoo rules.
* Confirm without generating another delivery for the original items.
* Add new sale lines for additional products and deliver them normally.
* Invoice using standard Odoo invoicing and the products' invoice policies.

Traceability and controls
-------------------------
* One sale per Advance Delivery; repeated clicks open the existing sale.
* Standard Delivery smart button and an Open Advance Sale button.
* Advance Sale and Advance Delivery ribbons.
* Advance Sales menu and an Advance Sale search filter in Sales.
* Draft or sent normal quotations can be converted to Advance Sales.
* Generated lines retain their delivered product, unit and source links.
* Generated lines and their source sale cannot be deleted.

Uses standard sale orders, order lines, deliveries and invoices.
Requires Sales and Sales/Inventory integration (sale_management, sale_stock).
Users generating sales need Inventory and Sales permissions. Configure a
warehouse with an outgoing operation type and a customer on the delivery.
Designed for Odoo 17 Community; no Enterprise module dependency.
This workflow concerns delivery before sale creation, not advance payments.

Maintainer: Mitchel Admin
Support: erpmitchellodoo@gmail.com
''',
    'category': 'Sales/Sales',
    'license': 'LGPL-3',
    'author': 'Mitchel Admin',
    'maintainer': 'Mitchel Admin',
    'support': 'erpmitchellodoo@gmail.com',
    'images': ['static/description/banner.png'],
    'depends': ['sale_management', 'sale_stock'],
    'data': ['views/sale_order_views.xml', 'views/stock_picking_views.xml'],
    'installable': True,
    'application': True,
}
