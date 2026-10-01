"""Deterministic payment-clause schedule engine.

Signature: Mourad.Soltani
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Any


class ClauseError(ValueError):
    """Raised when a clause document is incomplete or inconsistent."""


@dataclass(frozen=True)
class Event:
    kind: str
    on: str
    amount: str
    title: str
    note: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _parse_date(value: str, field: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ClauseError(f"{field} must be YYYY-MM-DD") from exc


def _money(amount: float, currency: str) -> str:
    return f"{currency} {amount:,.2f}"


def _note(kind: str, client: str, project: str, amount: str, on: str) -> str:
    subject = {
        "deposit_request": f"Deposit to start {project}",
        "deposit_reminder": f"Deposit still open for {project}",
        "milestone_invoice": f"Invoice for {project}",
        "due_reminder": f"Payment due soon — {project}",
        "late_notice": f"Payment past due — {project}",
        "final_notice": f"Final notice — {project}",
    }[kind]
    body = {
        "deposit_request": (
            f"Hi {client}, the agreed deposit of {amount} starts {project}. "
            f"Please send it by {on} so I can hold the slot."
        ),
        "deposit_reminder": (
            f"Hi {client}, checking in on the {amount} deposit for {project}. "
            f"I can start once it lands."
        ),
        "milestone_invoice": (
            f"Hi {client}, {project} reached this milestone. "
            f"Invoice amount {amount}, dated {on}."
        ),
        "due_reminder": (
            f"Hi {client}, a friendly reminder that {amount} for {project} "
            f"is due on {on}."
        ),
        "late_notice": (
            f"Hi {client}, {amount} for {project} was due on {on} and is now past due. "
            f"Could you confirm the payment date today?"
        ),
        "final_notice": (
            f"Hi {client}, this is a final note on the overdue {amount} for {project}. "
            f"Please reply with a payment date so we can close it cleanly."
        ),
    }[kind]
    return f"Subject: {subject}\n\n{body}"


def build_schedule(doc: dict[str, Any]) -> dict[str, Any]:
    required = ("client", "project", "currency", "total", "deposit_percent", "net_days", "start_date", "milestones")
    missing = [key for key in required if key not in doc]
    if missing:
        raise ClauseError("missing fields: " + ", ".join(missing))

    client = str(doc["client"]).strip()
    project = str(doc["project"]).strip()
    currency = str(doc["currency"]).strip().upper()
    if not client or not project or len(currency) != 3:
        raise ClauseError("client, project, and 3-letter currency are required")

    total = float(doc["total"])
    deposit_percent = float(doc["deposit_percent"])
    net_days = int(doc["net_days"])
    if total <= 0 or not 0 <= deposit_percent <= 100 or net_days < 0:
        raise ClauseError("total, deposit_percent, or net_days is out of range")

    start = _parse_date(str(doc["start_date"]), "start_date")
    milestones = doc["milestones"]
    if not isinstance(milestones, list) or not milestones:
        raise ClauseError("milestones must be a non-empty list")

    deposit = round(total * deposit_percent / 100, 2)
    remaining = round(total - deposit, 2)
    weights = []
    parsed = []
    for index, item in enumerate(milestones):
        if not isinstance(item, dict) or "name" not in item or "date" not in item:
            raise ClauseError(f"milestone {index} needs name and date")
        weight = float(item.get("weight", 1))
        if weight <= 0:
            raise ClauseError(f"milestone {index} weight must be positive")
        parsed.append((str(item["name"]), _parse_date(str(item["date"]), f"milestones[{index}].date"), weight))
        weights.append(weight)

    weight_sum = sum(weights)
    events: list[Event] = []
    if deposit > 0:
        deposit_text = _money(deposit, currency)
        events.append(
            Event(
                "deposit_request",
                start.isoformat(),
                deposit_text,
                "Request deposit",
                _note("deposit_request", client, project, deposit_text, start.isoformat()),
            )
        )
        reminder_on = start - timedelta(days=2)
        events.append(
            Event(
                "deposit_reminder",
                reminder_on.isoformat(),
                deposit_text,
                "Deposit reminder",
                _note("deposit_reminder", client, project, deposit_text, start.isoformat()),
            )
        )

    allocated = 0.0
    for index, (name, when, weight) in enumerate(parsed):
        if index == len(parsed) - 1:
            amount = round(remaining - allocated, 2)
        else:
            amount = round(remaining * weight / weight_sum, 2)
            allocated += amount
        amount_text = _money(amount, currency)
        due = when + timedelta(days=net_days)
        events.append(
            Event(
                "milestone_invoice",
                when.isoformat(),
                amount_text,
                f"Invoice: {name}",
                _note("milestone_invoice", client, project, amount_text, when.isoformat()),
            )
        )
        events.append(
            Event(
                "due_reminder",
                (due - timedelta(days=3)).isoformat(),
                amount_text,
                f"Due reminder: {name}",
                _note("due_reminder", client, project, amount_text, due.isoformat()),
            )
        )
        events.append(
            Event(
                "late_notice",
                (due + timedelta(days=1)).isoformat(),
                amount_text,
                f"Late notice: {name}",
                _note("late_notice", client, project, amount_text, due.isoformat()),
            )
        )
        events.append(
            Event(
                "final_notice",
                (due + timedelta(days=7)).isoformat(),
                amount_text,
                f"Final notice: {name}",
                _note("final_notice", client, project, amount_text, due.isoformat()),
            )
        )

    events.sort(key=lambda item: (item.on, item.kind))
    return {
        "product": "payclause",
        "signature": "Mourad.Soltani",
        "client": client,
        "project": project,
        "currency": currency,
        "total": _money(total, currency),
        "deposit": _money(deposit, currency),
        "net_days": net_days,
        "event_count": len(events),
        "events": [event.to_dict() for event in events],
    }


def health() -> dict[str, str]:
    sample = {
        "client": "Ada",
        "project": "Brand kit",
        "currency": "USD",
        "total": 1000,
        "deposit_percent": 50,
        "net_days": 15,
        "start_date": "2026-10-01",
        "milestones": [{"name": "Delivery", "date": "2026-10-20", "weight": 1}],
    }
    schedule = build_schedule(sample)
    if schedule["event_count"] < 5:
        raise ClauseError("health schedule too short")
    return {"status": "ok", "product": "payclause", "signature": "Mourad.Soltani", "version": "0.1.0"}
