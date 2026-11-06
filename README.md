# Swingora recreation

A faithful static recreation of https://swingora.webflow.io/, with 26 pages and 133 locally hosted design assets. Original responsive styling, fonts, images, Webflow interactions, tabs, FAQs, and sliders are retained. The floating “Made in Webflow” badge is disabled on every page.

Run `npm run dev` and open http://127.0.0.1:5195/. Run `npm run check` to validate pages and local asset references.

Contact submissions are deliberately local only and display a preview notice; no message is delivered. Third-party review telemetry and Turnstile form integration have been removed. Vimeo lightbox playback still requires its external video service.

Validation covered the desktop homepage against the reference, the 390px mobile homepage and seven representative list/detail pages, menu interaction, service tabs, FAQ expansion, and the local form notice. All 1,226 internal links and asset references pass the static verification. This is a close recreation; absolute pixel identity across every browser and animation frame is not asserted.

## GitHub Pages

The GitHub Actions workflow publishes the `dist/` website on each push to `main`. It prepares links for the `/swingora/` project path while preserving the existing Sites publication.

Repository: https://github.com/muhirwacoder1/swingora

Live GitHub Pages website: https://muhirwacoder1.github.io/swingora/
