# Africa Outbreak & Population Watch

Open-source public-interest visualization for African outbreak events, demographic impact, displacement, and official travel advisories concerning the Democratic Republic of the Congo (DRC).

**Developed by Hanni Cheng.**

## Principles
- Source-first: retain source, as-of time, retrieval time, and validation state.
- Missing is not zero.
- Official travel advisories retain native wording; normalized risk is secondary.
- Failed refreshes do not overwrite the last trusted snapshot.
- Public-interest visualization only; not medical or travel advice.

## Sources
WHO, ReliefWeb, UN World Population Prospects, UNHCR/IOM (planned), and official national travel-advisory authorities.

## Automation
GitHub Actions will refresh source status and versioned data snapshots. Source-specific parsers must pass validation before values are published.

## License
MIT for project code. Upstream datasets remain subject to their respective source terms.
