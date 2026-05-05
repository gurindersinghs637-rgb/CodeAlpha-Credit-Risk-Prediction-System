from flask import Flask, request, jsonify, render_template_string
import pickle
import pandas as pd
import os

app = Flask(__name__)

# ---------------- LOAD MODEL ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_pkl(name):
    try:
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
    except:
        return None

model = load_pkl('credit_risk_model.pkl')
columns = load_pkl('model_columns.pkl')

# ---------------- DUMMY MODEL ----------------
if model is None or columns is None:
    class DummyModel:
        def predict(self, X): return [0]
        def predict_proba(self, X): return [[0.7, 0.3]]

    model = DummyModel()

    columns = [
        'Credit_Utilization','age','Late_30_59_Days','DebtRatio',
        'MonthlyIncome','NumberOfOpenCreditLinesAndLoans',
        'NumberOfTimes90DaysLate','NumberRealEstateLoansOrLines',
        'Late_60_89_Days','NumberOfDependents','TotalLatePayments'
    ]

# ---------------- UI ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Credit Risk Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    margin: 0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

.container {
    max-width: 900px;
    margin: auto;
    padding: 40px 20px;
}

h1 {
    text-align: center;
    font-size: 34px;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
}

.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 35px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* GRID FIX */
.grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 22px;
}

/* FIELD BOX (KEY FIX) */
.field {
    background: rgba(255,255,255,0.04);
    padding: 12px;
    border-radius: 14px;
}

/* INPUT */
.field input {
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: none;
    background: #1e293b;
    color: white;
    font-size: 14px;
}

/* FOCUS */
.field input:focus {
    outline: none;
    box-shadow: 0 0 8px rgba(56,189,248,0.6);
}

/* BUTTON */
button {
    width: 100%;
    margin-top: 25px;
    padding: 15px;
    border-radius: 14px;
    border: none;
    font-size: 16px;
    font-weight: bold;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    color: white;
    cursor: pointer;
    transition: 0.3s;
}

button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(59,130,246,0.4);
}

/* RESULT */
.result {
    margin-top: 25px;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}

.safe { border: 1px solid #00ff95; }
.risk { border: 1px solid #ff4d4d; }

/* BAR */
.bar {
    height: 10px;
    background: #1e293b;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 10px;
}

.fill {
    height: 100%;
    width: 0%;
    transition: 1s;
}

/* MOBILE */
@media(max-width: 600px){
    .grid {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>

<div class="container">

<h1>💳 Credit Risk Prediction</h1>
<div class="subtitle">AI-powered financial risk assessment</div>

<div class="card">

<div class="grid">

<div class="field"><input id="age" placeholder="Age"></div>
<div class="field"><input id="MonthlyIncome" placeholder="Monthly Income"></div>

<div class="field"><input id="Credit_Utilization" placeholder="Credit Utilization (0-1)"></div>
<div class="field"><input id="DebtRatio" placeholder="Debt Ratio"></div>

<div class="field"><input id="NumberOfOpenCreditLinesAndLoans" placeholder="Credit Lines"></div>
<div class="field"><input id="NumberRealEstateLoansOrLines" placeholder="Real Estate Loans"></div>

<div class="field"><input id="NumberOfDependents" placeholder="Dependents"></div>
<div class="field"><input id="Late_30_59_Days" placeholder="Late 30-59 Days"></div>

<div class="field"><input id="Late_60_89_Days" placeholder="Late 60-89 Days"></div>
<div class="field"><input id="NumberOfTimes90DaysLate" placeholder="Late 90+ Days"></div>

</div>

<button onclick="predict()">⚡ Analyze Risk</button>

<div id="result"></div>

</div>

</div>

<script>
async function predict(){

    let data = {
        age: parseFloat(age.value),
        MonthlyIncome: parseFloat(MonthlyIncome.value),
        Credit_Utilization: parseFloat(Credit_Utilization.value),
        DebtRatio: parseFloat(DebtRatio.value),
        NumberOfOpenCreditLinesAndLoans: parseFloat(NumberOfOpenCreditLinesAndLoans.value),
        NumberRealEstateLoansOrLines: parseFloat(NumberRealEstateLoansOrLines.value),
        NumberOfDependents: parseFloat(NumberOfDependents.value),
        Late_30_59_Days: parseFloat(Late_30_59_Days.value),
        Late_60_89_Days: parseFloat(Late_60_89_Days.value),
        NumberOfTimes90DaysLate: parseFloat(NumberOfTimes90DaysLate.value)
    };

    let res = await fetch('/predict', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(data)
    });

    let out = await res.json();
    let box = document.getElementById('result');

    if(out.error){
        box.innerHTML = "<div class='result risk'>❌ "+out.error+"</div>";
        return;
    }

    let prob = (out.probability * 100).toFixed(2);
    let color = out.prediction == 0 ? "safe" : "risk";
    let label = out.prediction == 0 ? "✅ Low Risk" : "⚠️ High Risk";

    box.innerHTML = `
        <div class="result ${color}">
            <h2>${label}</h2>
            <h3>${prob}% Probability</h3>
            <div class="bar">
                <div class="fill" id="barFill"></div>
            </div>
        </div>
    `;

    setTimeout(()=>{
        document.getElementById('barFill').style.width = prob + "%";
        document.getElementById('barFill').style.background =
            out.prediction == 0 ? "#00ff95" : "#ff4d4d";
    }, 100);
}
</script>

</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        age = float(data['age'])
        inc = float(data['MonthlyIncome'])
        util = float(data['Credit_Utilization'])
        debt = float(data['DebtRatio'])
        ocl = float(data['NumberOfOpenCreditLinesAndLoans'])
        rel = float(data['NumberRealEstateLoansOrLines'])
        dep = float(data['NumberOfDependents'])
        l30 = float(data['Late_30_59_Days'])
        l60 = float(data['Late_60_89_Days'])
        l90 = float(data['NumberOfTimes90DaysLate'])

        row = {
            'Credit_Utilization': util,
            'age': age,
            'Late_30_59_Days': l30,
            'DebtRatio': debt,
            'MonthlyIncome': inc,
            'NumberOfOpenCreditLinesAndLoans': ocl,
            'NumberOfTimes90DaysLate': l90,
            'NumberRealEstateLoansOrLines': rel,
            'Late_60_89_Days': l60,
            'NumberOfDependents': dep,
        }

        df = pd.DataFrame([row])
        df = df.reindex(columns=columns, fill_value=0)

        pred = model.predict(df)[0]
        prob = model.predict_proba(df)[0][1]

        return jsonify({'prediction': int(pred), 'probability': float(prob)})

    except Exception as e:
        return jsonify({'error': str(e)})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)