"""Deterministic, synthetic masking of customer records.

The customer ``id`` is kept so masked records can still be joined back to the original;
every other personal field is replaced with generated data seeded from that id, so the same
customer always masks to the same values and no original value is derived from the output.
"""

import hashlib
import random

RETAINED_FIELDS = {"id"}
PRESERVED_FIELDS = {"title", "country"}  # not personal; kept so the record stays realistic

FIRST_NAMES = ["Alex", "Jamie", "Taylor", "Morgan", "Casey", "Riley", "Jordan", "Quinn"]
LAST_NAMES = ["Rivera", "Nguyen", "Okafor", "Lindqvist", "Tanaka", "Moreau", "Novak", "Silva"]
COMPANIES = ["Acme Labs", "Globex Corp", "Initech", "Umbrella Ltd", "Hooli", "Stark Works"]
STREETS = ["Maple Ave", "Oak Street", "Cedar Lane", "Harbour Road", "Sunset Blvd", "Elm Court"]
CITIES = ["Springfield", "Riverton", "Lakeside", "Fairview", "Georgetown", "Brookfield"]
STATES = ["North", "South", "East", "West", "Central"]
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]  # fmt: skip


def _rng(seed_value):
    digest = hashlib.sha256(f"mask:{seed_value}".encode()).hexdigest()
    return random.Random(digest)


def _differs(make, original):
    """Draw from ``make`` until the value differs from the original one."""
    for _ in range(100):
        value = make()
        if value != original:
            return value
    return f"{value}x"


def mask_customer(record, secret="test-masking-salt"):
    """Return a masked copy of ``record``; the original is not modified."""
    rng = _rng(f"{secret}:{record['id']}")
    get = record.get

    first = _differs(lambda: rng.choice(FIRST_NAMES), get("first_name"))
    last = _differs(lambda: rng.choice(LAST_NAMES), get("last_name"))
    token = f"{rng.randrange(16**6):06x}"
    makers = {
        "company": lambda: rng.choice(COMPANIES),
        "address1": lambda: f"{rng.randint(1, 999)} {rng.choice(STREETS)}",
        "address2": lambda: f"Unit {rng.randint(1, 99)}",
        "city": lambda: rng.choice(CITIES),
        "state": lambda: rng.choice(STATES),
        "zipcode": lambda: f"{rng.randint(10000, 99999)}",
        "mobile_number": lambda: f"9{rng.randint(1000000, 9999999)}",
        "birth_day": lambda: str(rng.randint(1, 28)),
        "birth_month": lambda: rng.choice(MONTHS),
        "birth_year": lambda: str(rng.randint(1950, 2005)),
    }
    generated = {
        "name": f"{first} {last}",
        "first_name": first,
        "last_name": last,
        "email": f"{first}.{last}.{token}@masked.example.com".lower(),
    }

    masked = {}
    for key, value in record.items():
        if key in RETAINED_FIELDS or key in PRESERVED_FIELDS:
            masked[key] = value
        elif key in makers:
            masked[key] = _differs(makers[key], value)
        else:
            masked[key] = generated.get(key, "***")
    return masked
