from flask import Flask, render_template, request
from tree_advisor import run_tree_advisor  # new import

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    soil_raw = request.form.get('soil', '').strip()
    seed = request.form.get('seed', '').strip()
    rain_raw = request.form.get('rain', '').strip()
    region = request.form.get('region', '').strip()
    land = request.form.get('land', '').strip()
    temperature_raw = request.form.get('temperature', '').strip()
    purpose = request.form.get('purpose', '').strip()

    if not all([soil_raw, seed, rain_raw, region, land, temperature_raw, purpose]):
        return render_template(
            'index.html',
            error="Please fill all the fields.",
            soil=soil_raw, seed=seed, rain=rain_raw,
            region=region, land=land, temperature=temperature_raw, purpose=purpose
        )

    # Call real model
    model_output = run_tree_advisor(
        tree=seed,
        soil_raw=soil_raw,
        rain_raw=rain_raw,
        region=region,
        land_raw=land,
        temperature=temperature_raw,
        purpose=purpose
    )

    return render_template(
        'agriinfo.html',
        soil=soil_raw,
        seed=seed,
        rain=rain_raw,
        region=region,
        land=land,
        temperature=temperature_raw,
        purpose=purpose,
        model_output=model_output
    )

if __name__ == '__main__':
    app.run(debug=True)
