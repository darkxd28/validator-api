# IBAN + VAT Validator API

Validates IBAN bank account numbers (77 countries) and EU VAT numbers (27 EU states + UK).
Pure logic — no external APIs, no cost to run, no dependencies that can break.

## Run locally

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /validate/iban | Validate a single IBAN |
| POST | /validate/vat | Validate a single VAT number |
| POST | /validate/batch | Validate up to 100 IBANs/VATs at once |
| GET | /countries | List all supported countries |
| GET | /health | Health check |

## Deploy free on Render (5 minutes)

1. Push this folder to GitHub
2. Go to render.com → New → Web Service
3. Connect your GitHub repo
4. Runtime: Docker
5. Click Deploy — you get a free URL like `https://yourapp.onrender.com`

## List on RapidAPI (where you earn money)

1. Go to rapidapi.com/provider → My APIs → Add New API
2. Name: "IBAN + VAT Validator"
3. Base URL: your Render URL
4. Add endpoints:
   - POST /validate/iban
   - POST /validate/vat  
   - POST /validate/batch
   - GET /countries
5. Pricing (suggested):
   - Free: 50 requests/month
   - Basic ($5/mo): 1,000 requests/month
   - Pro ($20/mo): 10,000 requests/month
   - Ultra ($0.001/request): pay per use
6. Description to use:
   "Validate IBAN bank account numbers and EU VAT numbers instantly.
   Supports 77 countries for IBAN and all 27 EU member states + UK for VAT.
   Returns validity, country, formatted output, and error details.
   Batch endpoint validates up to 100 numbers in one request."

## Why this sells

- E-commerce platforms validate VAT at checkout — legally required in EU
- Fintech apps validate IBANs before bank transfers — prevents failed payments  
- Accountancy software validates both — Xero, QuickBooks integrations
- These customers call it thousands of times per month = recurring revenue
