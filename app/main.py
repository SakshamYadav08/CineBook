from flask import Flask, jsonify, render_template, request
from .config import CINEMA, TIERS, PRICING
from .pricing import PricingEngine, PricingError
from .importer import import_price_list

app = Flask(__name__)
engine = PricingEngine(TIERS, PRICING)

def serialize(v):
    return f"{v:.2f}" if hasattr(v, "quantize") else v

@app.get("/")
def index():
    return render_template(
        "index.html",
        cinema=CINEMA,
        tiers=engine.available_tiers(),
        config=PRICING,
    )

@app.get("/api/tiers")
def tiers():
    return jsonify([
        {**t, "price": f'{t["price"]:.2f}'} for t in engine.available_tiers()
    ])

@app.post("/api/import-prices")
def import_prices():
    global engine
    data = request.get_json(silent=True) or {}
    result = import_price_list(data.get("text", ""), {k.lower(): t.available_seats for k, t in engine.tiers.items()})
    if not result["tiers"]:
        return jsonify({"error": "No valid price rows were imported", "imported": result["imported"], "deduplicated": result["deduplicated"], "rejected": result["rejected"]}), 400
    engine = PricingEngine(result["tiers"], PRICING)
    return jsonify({
        "tiers": [{**t, "price": f'{t["price"]:.2f}'} for t in engine.available_tiers()],
        "imported": [{**x, "price": f'{x["price"]:.2f}'} for x in result["imported"]],
        "deduplicated": result["deduplicated"],
        "rejected": result["rejected"],
    })

@app.post("/api/price")
def price():
    data = request.get_json(silent=True) or {}
    try:
        selections = data.get("selections", {})
        if not isinstance(selections, dict):
            raise PricingError("Invalid ticket selections")
        parsed = {}
        for tier, qty in selections.items():
            if not isinstance(qty, int) or isinstance(qty, bool):
                raise PricingError("Ticket quantities must be whole numbers")
            if qty > 0:
                parsed[tier] = qty
        result = engine.calculate(parsed, bool(data.get("member", False)), bool(data.get("festival", True)))

        def clean(obj):
            if isinstance(obj, dict):
                return {k: clean(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [clean(v) for v in obj]
            return serialize(obj)

        return jsonify(clean(result))
    except PricingError as exc:
        return jsonify({"error": str(exc)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
