"""
EU VAT + IBAN Validator API
Pure logic — no external APIs, no cost to run.
"""
import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ── IBAN ──────────────────────────────────────────────────────────────────────

IBAN_FORMATS = {
    "AL": (28, "Albania"),           "AD": (24, "Andorra"),
    "AT": (20, "Austria"),           "AZ": (28, "Azerbaijan"),
    "BH": (22, "Bahrain"),           "BE": (16, "Belgium"),
    "BA": (20, "Bosnia"),            "BR": (29, "Brazil"),
    "BG": (22, "Bulgaria"),          "CR": (22, "Costa Rica"),
    "HR": (21, "Croatia"),           "CY": (28, "Cyprus"),
    "CZ": (24, "Czech Republic"),    "DK": (18, "Denmark"),
    "DO": (28, "Dominican Republic"),"EG": (29, "Egypt"),
    "SV": (28, "El Salvador"),       "EE": (20, "Estonia"),
    "FO": (18, "Faroe Islands"),     "FI": (18, "Finland"),
    "FR": (27, "France"),            "GE": (22, "Georgia"),
    "DE": (22, "Germany"),           "GI": (23, "Gibraltar"),
    "GR": (27, "Greece"),            "GL": (18, "Greenland"),
    "GT": (28, "Guatemala"),         "HU": (28, "Hungary"),
    "IS": (26, "Iceland"),           "IQ": (23, "Iraq"),
    "IE": (22, "Ireland"),           "IL": (23, "Israel"),
    "IT": (27, "Italy"),             "JO": (30, "Jordan"),
    "KZ": (20, "Kazakhstan"),        "XK": (20, "Kosovo"),
    "KW": (30, "Kuwait"),            "LV": (21, "Latvia"),
    "LB": (28, "Lebanon"),           "LI": (21, "Liechtenstein"),
    "LT": (20, "Lithuania"),         "LU": (20, "Luxembourg"),
    "MT": (31, "Malta"),             "MR": (27, "Mauritania"),
    "MU": (30, "Mauritius"),         "MD": (24, "Moldova"),
    "MC": (27, "Monaco"),            "ME": (22, "Montenegro"),
    "NL": (18, "Netherlands"),       "MK": (19, "North Macedonia"),
    "NO": (15, "Norway"),            "PK": (24, "Pakistan"),
    "PS": (29, "Palestine"),         "PL": (28, "Poland"),
    "PT": (25, "Portugal"),          "QA": (29, "Qatar"),
    "RO": (24, "Romania"),           "LC": (32, "Saint Lucia"),
    "SM": (27, "San Marino"),        "SA": (24, "Saudi Arabia"),
    "RS": (22, "Serbia"),            "SC": (31, "Seychelles"),
    "SK": (24, "Slovakia"),          "SI": (19, "Slovenia"),
    "ES": (24, "Spain"),             "SD": (18, "Sudan"),
    "SE": (24, "Sweden"),            "CH": (21, "Switzerland"),
    "TL": (23, "Timor-Leste"),       "TN": (24, "Tunisia"),
    "TR": (26, "Turkey"),            "UA": (29, "Ukraine"),
    "AE": (23, "UAE"),               "GB": (22, "United Kingdom"),
    "VA": (22, "Vatican"),           "VG": (24, "Virgin Islands"),
}

def iban_to_int(iban):
    iban = iban[4:] + iban[:4]
    digits = ""
    for ch in iban:
        if ch.isdigit():
            digits += ch
        else:
            digits += str(ord(ch) - ord('A') + 10)
    return int(digits)

def validate_iban(raw):
    iban = re.sub(r"\s+", "", raw).upper()

    if len(iban) < 4:
        return {"valid": False, "error": "Too short to be a valid IBAN"}

    country_code = iban[:2]
    if not country_code.isalpha():
        return {"valid": False, "error": "IBAN must start with a 2-letter country code"}

    if country_code not in IBAN_FORMATS:
        return {"valid": False, "error": f"Country code '{country_code}' not recognized or not IBAN-enabled"}

    expected_length, country_name = IBAN_FORMATS[country_code]

    if len(iban) != expected_length:
        return {
            "valid": False,
            "error": f"{country_name} IBANs must be {expected_length} characters (got {len(iban)})"
        }

    if not re.match(r'^[A-Z0-9]+$', iban):
        return {"valid": False, "error": "IBAN contains invalid characters"}

    checksum_valid = iban_to_int(iban) % 97 == 1

    if not checksum_valid:
        return {"valid": False, "error": "Checksum failed — IBAN has a digit error"}

    formatted = " ".join(iban[i:i+4] for i in range(0, len(iban), 4))

    return {
        "valid": True,
        "iban": iban,
        "formatted": formatted,
        "country_code": country_code,
        "country": country_name,
        "length": len(iban),
        "check_digits": iban[2:4],
        "bban": iban[4:],
    }


# ── VAT ───────────────────────────────────────────────────────────────────────

VAT_FORMATS = {
    "AT": {"country": "Austria",        "pattern": r"^ATU\d{8}$",                  "example": "ATU12345678"},
    "BE": {"country": "Belgium",        "pattern": r"^BE0\d{9}$",                  "example": "BE0123456789"},
    "BG": {"country": "Bulgaria",       "pattern": r"^BG\d{9,10}$",               "example": "BG123456789"},
    "CY": {"country": "Cyprus",         "pattern": r"^CY\d{8}[A-Z]$",             "example": "CY12345678A"},
    "CZ": {"country": "Czech Republic", "pattern": r"^CZ\d{8,10}$",               "example": "CZ12345678"},
    "DE": {"country": "Germany",        "pattern": r"^DE\d{9}$",                   "example": "DE123456789"},
    "DK": {"country": "Denmark",        "pattern": r"^DK\d{8}$",                   "example": "DK12345678"},
    "EE": {"country": "Estonia",        "pattern": r"^EE\d{9}$",                   "example": "EE123456789"},
    "ES": {"country": "Spain",          "pattern": r"^ES[A-Z0-9]\d{7}[A-Z0-9]$",  "example": "ESA1234567A"},
    "FI": {"country": "Finland",        "pattern": r"^FI\d{8}$",                   "example": "FI12345678"},
    "FR": {"country": "France",         "pattern": r"^FR[A-Z0-9]{2}\d{9}$",       "example": "FRAA123456789"},
    "GB": {"country": "United Kingdom", "pattern": r"^GB(\d{9}|\d{12}|GD\d{3}|HA\d{3})$", "example": "GB123456789"},
    "GR": {"country": "Greece",         "pattern": r"^GR\d{9}$",                   "example": "GR123456789"},
    "HR": {"country": "Croatia",        "pattern": r"^HR\d{11}$",                  "example": "HR12345678901"},
    "HU": {"country": "Hungary",        "pattern": r"^HU\d{8}$",                   "example": "HU12345678"},
    "IE": {"country": "Ireland",        "pattern": r"^IE\d[A-Z0-9+*]\d{5}[A-Z]{1,2}$", "example": "IE1A12345B"},
    "IT": {"country": "Italy",          "pattern": r"^IT\d{11}$",                  "example": "IT12345678901"},
    "LT": {"country": "Lithuania",      "pattern": r"^LT(\d{9}|\d{12})$",          "example": "LT123456789"},
    "LU": {"country": "Luxembourg",     "pattern": r"^LU\d{8}$",                   "example": "LU12345678"},
    "LV": {"country": "Latvia",         "pattern": r"^LV\d{11}$",                  "example": "LV12345678901"},
    "MT": {"country": "Malta",          "pattern": r"^MT\d{8}$",                   "example": "MT12345678"},
    "NL": {"country": "Netherlands",    "pattern": r"^NL\d{9}B\d{2}$",            "example": "NL123456789B01"},
    "PL": {"country": "Poland",         "pattern": r"^PL\d{10}$",                  "example": "PL1234567890"},
    "PT": {"country": "Portugal",       "pattern": r"^PT\d{9}$",                   "example": "PT123456789"},
    "RO": {"country": "Romania",        "pattern": r"^RO\d{2,10}$",               "example": "RO12345678"},
    "SE": {"country": "Sweden",         "pattern": r"^SE\d{12}$",                  "example": "SE123456789012"},
    "SI": {"country": "Slovenia",       "pattern": r"^SI\d{8}$",                   "example": "SI12345678"},
    "SK": {"country": "Slovakia",       "pattern": r"^SK\d{10}$",                  "example": "SK1234567890"},
}

def validate_vat(raw):
    vat = re.sub(r"[\s.\-]", "", raw).upper()

    if len(vat) < 4:
        return {"valid": False, "error": "Too short to be a valid VAT number"}

    country_code = vat[:2]
    if not country_code.isalpha():
        return {"valid": False, "error": "VAT number must start with a 2-letter country code"}

    if country_code not in VAT_FORMATS:
        return {"valid": False, "error": f"Country code '{country_code}' not recognized or not EU VAT-enabled"}

    info = VAT_FORMATS[country_code]

    if not re.match(info["pattern"], vat):
        return {
            "valid": False,
            "error": f"Format invalid for {info['country']}. Expected format like: {info['example']}",
            "country_code": country_code,
            "country": info["country"],
            "expected_format": info["example"],
        }

    return {
        "valid": True,
        "vat_number": vat,
        "country_code": country_code,
        "country": info["country"],
        "normalized": vat,
        "expected_format": info["example"],
    }


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/validate/iban", methods=["POST"])
def iban_route():
    """
    Validate and parse an IBAN number.

    POST /validate/iban
    Body: { "iban": "GB82 WEST 1234 5698 7654 32" }

    Returns validity, country, formatted version, and parsed components.
    Supports 77 countries.
    """
    data = request.get_json(silent=True)
    if not data or not data.get("iban"):
        return jsonify({"error": "iban field is required"}), 400

    result = validate_iban(data["iban"])
    return jsonify({"status": "ok", "input": data["iban"], **result})


@app.route("/validate/vat", methods=["POST"])
def vat_route():
    """
    Validate an EU VAT number.

    POST /validate/vat
    Body: { "vat": "DE123456789" }

    Returns validity, country, and normalized format.
    Supports all 27 EU member states + UK.
    """
    data = request.get_json(silent=True)
    if not data or not data.get("vat"):
        return jsonify({"error": "vat field is required"}), 400

    result = validate_vat(data["vat"])
    return jsonify({"status": "ok", "input": data["vat"], **result})


@app.route("/validate/batch", methods=["POST"])
def batch_route():
    """
    Validate multiple IBANs and/or VAT numbers in one request.

    POST /validate/batch
    Body: {
      "ibans": ["GB82WEST12345698765432", "DE89370400440532013000"],
      "vats":  ["DE123456789", "FR12345678901"]
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    ibans = data.get("ibans", [])
    vats  = data.get("vats", [])

    if not ibans and not vats:
        return jsonify({"error": "Provide at least one iban or vat in arrays"}), 400
    if len(ibans) + len(vats) > 100:
        return jsonify({"error": "Max 100 items per batch request"}), 400

    return jsonify({
        "status": "ok",
        "iban_results": [{"input": i, **validate_iban(i)} for i in ibans],
        "vat_results":  [{"input": v, **validate_vat(v)}  for v in vats],
        "summary": {
            "ibans_valid":   sum(1 for i in ibans if validate_iban(i)["valid"]),
            "ibans_invalid": sum(1 for i in ibans if not validate_iban(i)["valid"]),
            "vats_valid":    sum(1 for v in vats  if validate_vat(v)["valid"]),
            "vats_invalid":  sum(1 for v in vats  if not validate_vat(v)["valid"]),
        }
    })


@app.route("/countries", methods=["GET"])
def countries():
    """List all supported countries for IBAN and VAT validation."""
    return jsonify({
        "status": "ok",
        "iban_countries": {k: {"country": v[1], "length": v[0]} for k, v in IBAN_FORMATS.items()},
        "vat_countries":  {k: {"country": v["country"], "example": v["example"]} for k, v in VAT_FORMATS.items()},
        "iban_count": len(IBAN_FORMATS),
        "vat_count":  len(VAT_FORMATS),
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "iban-vat-validator", "version": "1.0.0"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
