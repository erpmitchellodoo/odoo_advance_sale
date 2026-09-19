# App Store assets

The listing emphasizes the delivery-first workflow implemented in this module.
It describes editable pricing and protected delivery quantities, without
claiming advance-payment functionality or adding fictional UI screenshots.

- `static/description/icon.png`: square PNG app icon, 1254 × 1254.
- `static/description/banner.png`: 1774 × 887 PNG, exactly 2:1, used as the
  manifest cover and the responsive description banner.
- `static/description/index.html`: Bootstrap 4 layout, system fonts, dark body
  text, plum accents, no section background fills, scripts or external assets.
- `LICENSE` and `COPYING`: LGPL-3 and its incorporated GPL-3 terms.

The 2:1 cover matches the cover area observed on the existing App Store listing.
Its live rendering should be checked after the repository is rescanned.

References checked:
- https://apps.odoo.com/apps/vendor-guidelines
- https://apps.odoo.com/apps/upload

Publish the module files to the connected repository and re-scan it in Odoo
Apps. This local preparation does not publish or re-scan the repository.

## Image generation

Both images were created with the built-in image generation tool and visually
reviewed. They are marketing illustrations, not screenshots of the application.

### Icon prompt

Create a polished Odoo business app icon for 'Advance Sale Delivery'. Square 1:1 PNG. Deep plum rounded-square tile, a bold clean ivory delivery carton on left connected by a short turquoise rightward arrow to a small ivory sales document on right, document has two plum lines and turquoise checkmark. Represents deliver goods first then create sale. Flat geometric editorial icon, subtle dimensional shading, centered with generous safe padding, few large shapes clearly readable at 64px. No text, letters, numbers, watermark or Odoo logo. Professional and restrained.

### Banner prompt

Create an Odoo App Store cover banner EXACT 2:1 landscape aspect ratio, 1600x800 preferred. Premium business editorial design, ivory background with plum typography and teal accents, uncluttered layout, generous 8 percent safe margins so no text crops at thumbnail size. Left 55 percent: small heading 'ODOO 19', main bold large text on two or three lines exactly 'Advance Sale Delivery', and subtitle exactly 'Deliver first. Create the sale next.' Right 40 percent: tasteful dimensional illustration of a delivered carton with teal checkmark, arrow moving to a sales order document, visually communicates inventory delivery before sales paperwork. Tiny bottom caption 'Inventory → Sales'. Use only those text strings, correct spelling. Professional matching plum/ivory/teal business identity. No interface screenshot, no fake Odoo UI, no official Odoo logo, no extra tiny labels or watermark. All important contents fully contained within canvas. Readable at 628x314.
