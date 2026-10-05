# Africa Outbreak & Population Watch

Open-source public-interest visualization for African outbreak events, demographic impact, displacement, and official travel advisories concerning the Democratic Republic of the Congo (DRC).

**Developed by Hanni Cheng.**

## Principles
- Source-first: retain source, as-of time, retrieval time, and validation state.
- Missing is not zero.
- Official travel advisories retain native wording; normalized risk is secondary.
- Failed refreshes do not overwrite the last trusted snapshot.
- Public-interest visualization only; not medical or travel advice.

## Credits & acknowledgements
This project openly documents its development stack and contributors.

- **Developed by Hanni Cheng** — product concept, requirements, data-governance design and project direction.
- **ChatGPT by OpenAI** — AI-assisted requirements refinement, code generation, documentation and implementation support.
- **GitHub** — repository hosting and collaboration.
- **GitHub Actions** — scheduled data-refresh and deployment workflows.
- **GitHub Pages** — public static-site hosting.
- **HTML / CSS / JavaScript / JSON / Python** — implementation stack.

Public-health agencies, scientific organizations and data providers are credited as sources; attribution does **not** imply endorsement of this project.

## Sources
WHO, ReliefWeb, UN World Population Prospects, UNHCR/IOM (planned), and official national travel-advisory authorities.

## Automation
GitHub Actions will refresh source status and versioned data snapshots. Source-specific parsers must pass validation before values are published.

## License
MIT for project code. Upstream datasets remain subject to their respective source terms.
