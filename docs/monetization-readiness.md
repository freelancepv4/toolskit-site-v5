# Monetization and consent readiness (documentation only — no ad or tracking scripts are shipped)

Status: **no ad network, no analytics and no third-party request is active.** `src/assets/analytics.js` does nothing unless the owner sets `window.TK_ANALYTICS` AND the visitor grants consent; there is no consent banner UI yet.

Before any ads or analytics go live:
1. **Legal identity.** EU law (e.g. DDG §5 in Germany, e-Commerce Directive) expects an imprint/operator identity for commercial sites. `ToolsKit Administration` is a label, not a legal entity. Owner must supply the real details; localized EU pages should not launch commercially before that. (Launch blocker, not invented here.)
2. **Consent banner (CMP).** Needed before AdSense/GA4 for EEA/UK/CH visitors (ePrivacy + GDPR; Google requires a Google-certified CMP with TCF for ad personalisation in the EEA/UK). Not built; choose a CMP, then wire `TKA.setConsent`.
3. **CSP.** Current `script-src 'self'` blocks third-party scripts by design. Each ad/analytics domain must be added deliberately in `site.config.json`/`vercel.json`, and the privacy page rewritten.
4. **Privacy and cookie text** (all 7 languages) must be updated and legally reviewed at the same time.
5. **ads.txt**, AdSense site approval and layout (no ads near controls, reserved space to avoid layout shift) are open tasks.
6. Google approval typically expects substantive content on every indexed page; translated pages are unreviewed drafts (see `docs/localization-guide.md`).

No revenue figures are estimated here, because none could be measured.
