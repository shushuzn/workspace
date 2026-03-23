"""Data validation for Stock PRO"""

def validate_stock_data(symbol, data):
    """Validate stock data completeness and consistency"""
    errors = []
    warnings = []

    # Required fields
    required = ["price", "score", "target", "upside", "rating"]
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")

    # Data type checks
    if "price" in data:
        if data["price"] <= 0:
            errors.append(f"Invalid price: {data['price']}")
        elif data["price"] > 100000:
            warnings.append(f"High price: ${data['price']}")

    if "target" in data:
        if data["target"] <= 0:
            errors.append(f"Invalid target: {data['target']}")

    if "score" in data:
        if not 0 <= data["score"] <= 100:
            errors.append(f"Score out of range: {data['score']}")

    # Consistency checks
    if "price" in data and "target" in data:
        upside = (data["target"] - data["price"]) / data["price"] * 100
        if abs(upside - data.get("upside", 0)) > 1:  # Allow 1% tolerance
            warnings.append(f"Upside mismatch: calculated {upside:.1f}%, stored {data.get('upside', 0):.1f}%")

    # Financial ratios
    if "pe" in data:
        if data["pe"] < 0:
            errors.append(f"Negative P/E: {data['pe']}")
        elif data["pe"] > 500:
            warnings.append(f"Very high P/E: {data['pe']}x")

    if "peg" in data:
        if data["peg"] < 0:
            errors.append(f"Negative PEG: {data['peg']}")

    if "beta" in data:
        if data["beta"] < 0:
            errors.append(f"Negative beta: {data['beta']}")
        elif data["beta"] > 3:
            warnings.append(f"Very high beta: {data['beta']}")

    return {
        "symbol": symbol,
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_dataset(stocks):
    """Validate entire dataset"""
    all_errors = []
    all_warnings = []

    for sym, data in stocks.items():
        result = validate_stock_data(sym, data)
        all_errors.extend([(sym, e) for e in result["errors"]])
        all_warnings.extend([(sym, w) for w in result["warnings"]])

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "total_stocks": len(stocks)
    }


def check_data_freshness(data):
    """Check if data is fresh enough"""
    from datetime import datetime

    if "fetched_at" not in data:
        return {
            "fresh": False,
            "message": "No timestamp found",
            "age_hours": None
        }

    try:
        fetched = datetime.fromisoformat(data["fetched_at"])
        now = datetime.now()
        age = (now - fetched).total_seconds() / 3600

        if age < 1:
            message = "Fresh data (<1 hour)"
            fresh = True
        elif age < 24:
            message = f"Data is {age:.1f} hours old"
            fresh = True
        else:
            message = f"Data is {age:.1f} hours old - consider refreshing"
            fresh = False

        return {
            "fresh": fresh,
            "message": message,
            "age_hours": age
        }
    except:
        return {
            "fresh": False,
            "message": "Invalid timestamp format",
            "age_hours": None
        }


def data_quality_report(results):
    """Generate data quality report"""
    report = "# Data Quality Report\n\n"

    total = len(results)
    valid_count = 0
    all_errors = []
    all_warnings = []

    for r in results:
        validation = validate_stock_data(r["symbol"], r)
        if validation["valid"]:
            valid_count += 1
        all_errors.extend([(r["symbol"], e) for e in validation["errors"]])
        all_warnings.extend([(r["symbol"], w) for w in validation["warnings"]])

    # Summary
    quality_pct = (valid_count / total * 100) if total > 0 else 0
    report += f"**Overall Quality:** {quality_pct:.0f}% ({valid_count}/{total} valid)\n\n"

    # Errors
    if all_errors:
        report += "## Errors\n\n"
        for sym, error in all_errors[:10]:
            report += f"- **{sym}:** {error}\n"
        if len(all_errors) > 10:
            report += f"\n*...and {len(all_errors) - 10} more errors*\n"
    else:
        report += "**No errors found**\n\n"

    # Warnings
    if all_warnings:
        report += "## Warnings\n\n"
        for sym, warning in all_warnings[:10]:
            report += f"- **{sym}:** {warning}\n"
        if len(all_warnings) > 10:
            report += f"\n*...and {len(all_warnings) - 10} more warnings*\n"

    return report
