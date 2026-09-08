.PHONY: new validate test site-install site-dev site-build

new:
	uv run python scripts/create_question.py

validate:
	uv run python scripts/validate_content.py

test:
	uv run python -m unittest discover -s tests -v

site-install:
	npm install --prefix site

site-dev: validate
	ASTRO_TELEMETRY_DISABLED=1 npm run dev --prefix site

site-build: validate
	ASTRO_TELEMETRY_DISABLED=1 npm run build --prefix site
