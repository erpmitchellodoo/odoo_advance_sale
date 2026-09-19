# Odoo 18 port

Source: the delivery-first Odoo 19 addon, including editable pricing and
quantity protection. This is an addon code port, not a database downgrade.

Compatibility changes:

- Use sale.order.line.product_uom and tax_id where applicable.
- Use _sql_constraints for unique source delivery and stock move links.
- Link transfers and sales through procurement.group, including the sale's
  procurement_group_id and the completed picking/move group_id. Give each
  completed source delivery its own group so sibling backorders are not
  assigned to its sale.
- Preserve standard procurement for additional lines; skip already-delivered
  source lines.
- Use the target version's stock-rule method signature.
- Update user-group, sale tax and unit field names in tests.
- Remove obsolete tests referencing a classification-history field absent
  from the source addon; keep current Sales and delivery workflow tests.
- Update the manifest and HTML listing to Odoo 18. Reuse the icon and provide
  a version-neutral 2:1 cover banner.

Validation results are recorded after the target-version test run.
