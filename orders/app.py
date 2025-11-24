from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_conn():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 5432)),
        dbname=os.environ.get('DB_NAME', 'ecommerce'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'Apple2000!')
    )

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json(silent=True)
    # Accept either a JSON object {user_id, items: [...]}\n+    # or directly a list of items posted as the root JSON array.
    if isinstance(data, list):
        items = data
        user_id = None
    else:
        data = data or {}
        user_id = data.get('user_id')
        items = data.get('items', [])  # list of {product_id, quantity}
    if not items:
        return jsonify({'error': 'no items provided'}), 400
    conn = get_conn()
    cur = conn.cursor()
    total = 0
    try:
        for it in items:
            cur.execute('SELECT price FROM products WHERE id=%s', (it['product_id'],))
            row = cur.fetchone()
            if not row:
                raise Exception(f"product {it['product_id']} not found")
            total += float(row[0]) * int(it['quantity'])
        # create order
        cur.execute('INSERT INTO orders (user_id, total) VALUES (%s,%s) RETURNING id', (user_id, total))
        order_id = cur.fetchone()[0]
        # insert items
        for it in items:
            cur.execute('SELECT price FROM products WHERE id=%s', (it['product_id'],))
            price = float(cur.fetchone()[0])
            cur.execute('INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)', (order_id, it['product_id'], it['quantity'], price))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 400
    cur.close()
    conn.close()
    return jsonify({'order_id': order_id, 'total': total}), 201

@app.route('/orders/<int:oid>', methods=['GET'])
def get_order(oid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, user_id, total, created_at FROM orders WHERE id=%s', (oid,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({'error': 'not found'}), 404
    order = {'id': row[0], 'user_id': row[1], 'total': float(row[2]), 'created_at': row[3].isoformat()}
    cur.execute('SELECT product_id, quantity, unit_price FROM order_items WHERE order_id=%s', (oid,))
    items = []
    for r in cur.fetchall():
        items.append({'product_id': r[0], 'quantity': r[1], 'unit_price': float(r[2])})
    cur.close()
    conn.close()
    order['items'] = items
    return jsonify(order)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)
