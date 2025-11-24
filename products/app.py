from flask import Flask, jsonify, abort, request
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

@app.route('/products', methods=['GET'])
def list_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, price, stock, image_url, category FROM products ORDER BY id')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    products = []
    for r in rows:
        products.append({
            'id': r[0],
            'name': r[1],
            'description': r[2],
            'price': float(r[3]),
            'stock': r[4],
            'imageUrl': r[5],
            'category': r[6]
        })
    return jsonify(products)


@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock', 0)
    image_url = data.get('imageUrl') or data.get('image_url')
    category = data.get('category')
    if not (name and price is not None):
        return jsonify({'error': 'name and price required'}), 400
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO products (name, description, price, stock, image_url, category) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id',
                    (name, description, price, stock, image_url, category))
        pid = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': 'could not create product', 'detail': str(e)}), 400
    cur.close()
    conn.close()
    return jsonify({'id': pid, 'name': name, 'description': description, 'price': float(price), 'stock': stock, 'imageUrl': image_url, 'category': category}), 201


@app.route('/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    data = request.get_json() or {}
    fields = []
    values = []
    mapping = {
        'name': 'name',
        'description': 'description',
        'price': 'price',
        'stock': 'stock',
        'imageUrl': 'image_url',
        'image_url': 'image_url',
        'category': 'category'
    }
    for k, col in mapping.items():
        if k in data:
            fields.append(f"{col} = %s")
            values.append(data[k])
    if not fields:
        return jsonify({'error': 'no fields to update'}), 400
    values.append(pid)
    sql = f"UPDATE products SET {', '.join(fields)} WHERE id = %s RETURNING id, name, description, price, stock, image_url, category"
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql, tuple(values))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({'error': 'not found'}), 404
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': 'could not update product', 'detail': str(e)}), 400
    cur.close()
    conn.close()
    product = {'id': row[0], 'name': row[1], 'description': row[2], 'price': float(row[3]), 'stock': row[4], 'imageUrl': row[5], 'category': row[6]}
    return jsonify(product)


@app.route('/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM products WHERE id=%s RETURNING id', (pid,))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({'error': 'not found'}), 404
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': 'could not delete product', 'detail': str(e)}), 400
    cur.close()
    conn.close()
    return '', 204

@app.route('/products/<int:pid>', methods=['GET'])
def get_product(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, price, stock, image_url, category FROM products WHERE id=%s', (pid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        abort(404)
    product = {
        'id': row[0],
        'name': row[1],
        'description': row[2],
        'price': float(row[3]),
        'stock': row[4],
        'imageUrl': row[5],
        'category': row[6]
    }
    return jsonify(product)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
