# PayClause

Signature: Mourad.Soltani

PayClause is a local micro-tool that turns a freelance payment clause into a dated chase calendar and one-to-one note drafts. It does not send email. It does not call a network. It is a stdlib Python CLI a solo freelancer can run before a deposit or milestone invoice.

Trending fit: 2026 micro-SaaS lists keep pointing at trade-specific billing and deposit workflows, while generic invoicing is crowded. A GitHub name search for `payclause` returned no existing repository.

## What it does

- Splits a total into a deposit and weighted milestone invoices.
- Builds deposit request, deposit reminder, invoice, due reminder, late notice, and final notice dates.
- Drafts a short one-to-one note for each date. You send it yourself.

## Run

```bash
PYTHONPATH=src python3 -m payclause.cli health
PYTHONPATH=src python3 -m payclause.cli schedule --input examples/sample.json
PYTHONPATH=src python3 -m unittest tests.test_health
```

Health output is JSON with `"status": "ok"`.

## Clause file

```json
{
  "client": "Nora Berg",
  "project": "Autumn catalog",
  "currency": "EUR",
  "total": 1200,
  "deposit_percent": 50,
  "net_days": 14,
  "start_date": "2026-10-06",
  "milestones": [{"name": "Final files", "date": "2026-10-28", "weight": 1}]
}
```

## Buyer notes

See `docs/BUYER_NOTES.md` and `docs/OUTREACH_TEMPLATES.md`. Templates are for one-to-one use only. Do not bulk-send them.
