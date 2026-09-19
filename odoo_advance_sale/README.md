# Advance Sale and Delivery — Odoo 19

Install or upgrade `odoo_advance_sale` after restarting Odoo. This version
requires `sale_management` and `sale_stock`.

## Delivery-first workflow

1. Open **Inventory → Operations → Advance Deliveries**, immediately after
   Deliveries. A new transfer defaults to Advance Delivery and the current
   company's outgoing operation type. Select the appropriate warehouse if the
   company has several warehouses.
2. Set the customer, add products and validate the delivery using Odoo's normal
   reservation, lot/serial and delivery controls.
3. Click **Create Advance Sale**. The user needs both Inventory and Sales access.
   This creates a draft Advance Sale using the delivery's customer, company,
   warehouse, products, units and actual delivered quantities. Prices and taxes
   use the standard sale order defaults for that customer.
4. The original transfer appears in the sale's standard **Delivery** smart
   button. Its completed stock moves determine delivered and invoiceable
   quantities. **Open Advance Sale** on the delivery opens the linked sale.
5. Confirm the quotation normally. Original delivery lines do not generate
   another procurement or delivery. Add new editable sale lines for additional
   items; these use standard stock routes and generate a new delivery.

One delivery generates one sale order. Repeated clicks open that order. Only
completed positive-quantity moves are included. Undelivered backorders remain
separate transfers and can generate their own sale after validation. Returns
must use Odoo's standard return workflow, not Create Advance Sale.

Delivery-generated quantities are read-only in the form and protected by backend
validation. Prices, discounts, taxes, descriptions and other commercial fields
follow standard Odoo editing behavior. Product/unit identity, source links and
deletion remain protected to preserve the connection to the completed delivery.
Normal and newly added sale lines retain standard editing behavior.

## Sales entry points

**Sales → Orders → Advance Sales** still opens standard sale orders filtered
by Advance Sale, defaulting new quotations to that classification. Regular
Sales menus remain unchanged and include an **Advance Sale** search filter.
The form displays the standard **ADVANCE SALE** ribbon for advance orders.

The conversion button is available for normal, unlocked Draft/Sent quotations.
An order generated from a delivery must remain an Advance Sale with the same
customer and shipping address as its delivery.

## Validation

Workflow tests: `--test-enable --test-tags=/odoo_advance_sale:TestAdvanceDelivery`.
Use a disposable database. Existing classification-history tests in
`test_advance_sale.py` refer to the earlier confirmation-lock implementation,
which was removed independently before the delivery-first workflow was added.

All six delivery-workflow integration tests passed on local Odoo 19 in an
isolated database. They cover source linking, repeat-click handling, delivered
quantity invoicing, extra lines before and after confirmation, returns, and
backend quantity/deletion protection, and editable prices, discounts and taxes
carried into the invoice. XML views loaded successfully; no browser
visual test was run. The available test server used PostgreSQL 12, below Odoo
19's supported minimum of PostgreSQL 13.
