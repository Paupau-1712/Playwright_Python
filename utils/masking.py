"""Regex-based, format-preserving masking of API records.

Each field has a masking rule: a regex selecting the characters to replace. Every matched
character is swapped for a different random one of the same kind (letter -> letter of the same
case, digit -> digit), so the masked value keeps the original's shape (length, spaces,
punctuation) but none of its content. The ``id`` is retained so records still line up.
Output is seeded by the id, so the same record always masks to the same values.
"""

import copy
import hashlib
import html
import random
import re

RETAINED_FIELDS = {"id"}

DEFAULT_RULE = r"[A-Za-z0-9]"
FIELD_RULES = {
    "price": r"\d",  # keep the "Rs." currency prefix, mask only the amount
}

LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = LOWER.upper()
DIGITS = "0123456789"


def _different_char(char, rng):
    pool = LOWER if char in LOWER else UPPER if char in UPPER else DIGITS
    return rng.choice([c for c in pool if c != char])


def mask_text(value, rng, rule=DEFAULT_RULE):
    return re.sub(rule, lambda m: _different_char(m.group(), rng), value)


def _mask_value(value, key, rng):
    if isinstance(value, dict):
        return {k: _mask_value(v, k, rng) if k not in RETAINED_FIELDS else v for k, v in value.items()}
    if isinstance(value, list):
        return [_mask_value(v, key, rng) for v in value]
    if isinstance(value, str):
        return mask_text(value, rng, FIELD_RULES.get(key, DEFAULT_RULE))
    return value


def mask_record(record, secret="test-masking-salt"):
    """Return a masked deep copy of ``record``; the input is left untouched."""
    seed = hashlib.sha256(f"{secret}:{record['id']}".encode()).hexdigest()
    rng = random.Random(seed)
    return _mask_value(copy.deepcopy(record), None, rng)


def flatten(record, prefix=""):
    """{'category': {'category': 'Tops'}} -> {'category.category': 'Tops'}"""
    flat = {}
    for key, value in record.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(flatten(value, f"{name}."))
        else:
            flat[name] = value
    return flat


def render_text_table(title, rows, columns):
    widths = [max(len(c), *(len(str(r[c])) for r in rows)) for c in columns]
    line = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    out = [title, line, "| " + " | ".join(c.ljust(w) for c, w in zip(columns, widths)) + " |", line]
    for row in rows:
        out.append("| " + " | ".join(str(row[c]).ljust(w) for c, w in zip(columns, widths)) + " |")
    out.append(line)
    return "\n".join(out)


def _html_table(title, rows, columns, highlight=None):
    head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
    body = ""
    for i, row in enumerate(rows):
        cells = ""
        for c in columns:
            changed = highlight and highlight[i][c]
            cells += f"<td class='{'changed' if changed else ''}'>{html.escape(str(row[c]))}</td>"
        body += f"<tr>{cells}</tr>"
    return f"<h2>{html.escape(title)}</h2><table><tr>{head}</tr>{body}</table>"


def comparison_html(original_rows, masked_rows, columns):
    changed = [{c: o[c] != m[c] for c in columns} for o, m in zip(original_rows, masked_rows)]
    style = (
        "body{font-family:sans-serif;background:#ece9ff;padding:24px}"
        "table{border-collapse:collapse;background:#fff;margin-bottom:24px}"
        "th,td{border:1px solid #ccc;padding:4px 10px;font-size:13px}"
        "th{background:#f26b5b;color:#fff;text-align:left}"
        "td.changed{background:#e8f4ff}"
    )
    return (
        f"<html><head><meta charset='utf-8'><title>Data masking</title><style>{style}</style></head><body>"
        + _html_table("From production data (GET /productsList)", original_rows, columns)
        + _html_table("To synthetically identical masked data (id retained)", masked_rows, columns, changed)
        + "</body></html>"
    )
