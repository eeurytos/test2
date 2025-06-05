import sqlite3
import json
import urllib.request
from flask import Flask, request, jsonify, send_from_directory

DB = 'inventory.db'
app = Flask(__name__, static_folder='frontend')

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS holdings '
        '(asset TEXT PRIMARY KEY, amount REAL NOT NULL)'
    )
    conn.commit()
    conn.close()

def fetch_currency_rates():
    url = 'https://api.exchangerate.host/latest?base=TRY&symbols=USD,EUR'
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.load(response)
            rates = data.get('rates', {})
            rates['TRY'] = 1.0
            rates['GOLD'] = 2000.0
            return rates
    except Exception:
        return {'USD': 32.0, 'EUR': 35.0, 'TRY': 1.0, 'GOLD': 2000.0}

def get_holdings():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT asset, amount FROM holdings')
    rows = c.fetchall()
    conn.close()
    return {a: amt for a, amt in rows}

def set_holding(asset, amount):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        'INSERT INTO holdings(asset, amount) VALUES(?, ?) '
        'ON CONFLICT(asset) DO UPDATE SET amount = amount + excluded.amount',
        (asset, amount)
    )
    conn.commit()
    conn.close()

def remove_holding(asset, amount):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT amount FROM holdings WHERE asset=?', (asset,))
    row = c.fetchone()
    if row:
        new_amt = row[0] - amount
        if new_amt <= 0:
            c.execute('DELETE FROM holdings WHERE asset=?', (asset,))
        else:
            c.execute(
                'UPDATE holdings SET amount=? WHERE asset=?',
                (new_amt, asset)
            )
    conn.commit()
    conn.close()

@app.route('/api/holdings')
def api_holdings():
    holdings = get_holdings()
    rates = fetch_currency_rates()
    values = {}
    total_try = 0.0
    for asset, qty in holdings.items():
        rate = rates.get(asset, 1.0)
        val = qty * rate
        values[asset] = {'amount': qty, 'value_try': val}
        total_try += val
    return jsonify({'holdings': values, 'total_try': total_try})

@app.route('/api/add', methods=['POST'])
def api_add():
    data = request.get_json(force=True)
    asset = data.get('asset', '').upper()
    amount = float(data.get('amount', 0))
    if asset:
        set_holding(asset, amount)
    return jsonify({'status': 'ok'})

@app.route('/api/remove', methods=['POST'])
def api_remove():
    data = request.get_json(force=True)
    asset = data.get('asset', '').upper()
    amount = float(data.get('amount', 0))
    if asset:
        remove_holding(asset, amount)
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
