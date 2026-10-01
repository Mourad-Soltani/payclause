# Buyer notes

Signature: Mourad.Soltani

Product: PayClause, a local payment-clause chase calendar.

## Who it is for

Solo designers, developers, and writers who already quote a deposit and Net terms, then forget the follow-up date. Not for agencies that need accounting, tax, or payment collection.

## What a buyer gets

- Offline CLI, no account, no API key.
- Deterministic schedule from one JSON clause.
- Note drafts they copy into their own email client.
- MIT license, small surface, health tests.

## What it is not

- Not an invoice sender.
- Not a payment processor.
- Not a legal opinion. Dates are calendar arithmetic from the clause the user typed.

## Suggested price

$19 one-time for the CLI, or $9/month if a later hosted version stores clauses. This repo is the local core only.

## Handoff check

1. `PYTHONPATH=src python3 -m payclause.cli health` prints status ok.
2. `PYTHONPATH=src python3 -m unittest tests.test_health` passes.
3. Sample clause produces a EUR 600.00 deposit and six events.
