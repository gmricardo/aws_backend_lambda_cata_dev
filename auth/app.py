from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
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

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (name and email and password):
        return jsonify({'error': 'name, email and password required'}), 400
    password_hash = generate_password_hash(password)
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (name, email, password_hash) VALUES (%s,%s,%s) RETURNING id', (name, email, password_hash))
        uid = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': 'could not create user', 'detail': str(e)}), 400
    cur.close()
    conn.close()
    return jsonify({'id': uid, 'name': name, 'email': email}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not (email and password):
        return jsonify({'error': 'email and password required'}), 400
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name, password_hash, role FROM users WHERE email=%s', (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({'error': 'invalid credentials'}), 401
    uid, name, password_hash, role = row
    # Demo behaviour: seeded users may have NULL password_hash — accept demo password '123456'
    if password_hash is None:
        if password != '123456':
            return jsonify({'error': 'invalid credentials'}), 401
    else:
        if not check_password_hash(password_hash, password):
            return jsonify({'error': 'invalid credentials'}), 401
    # For demo purposes return simple token stub and role
    return jsonify({'id': uid, 'name': name, 'email': email, 'role': role, 'token': f'user-{uid}-token'})


@app.route('/users', methods=['GET'])
def list_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name, email, role, created_at FROM users ORDER BY id')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    users = []
    for r in rows:
        users.append({'id': str(r[0]), 'name': r[1], 'email': r[2], 'role': r[3], 'created_at': r[4].isoformat()})
    return jsonify(users)


@app.route('/users/<int:uid>', methods=['PUT'])
def update_user(uid):
    data = request.get_json() or {}
    fields = []
    values = []
    if 'name' in data:
        fields.append('name = %s'); values.append(data['name'])
    if 'email' in data:
        fields.append('email = %s'); values.append(data['email'])
    if 'role' in data:
        fields.append('role = %s'); values.append(data['role'])
    if 'password' in data:
        from werkzeug.security import generate_password_hash
        fields.append('password_hash = %s'); values.append(generate_password_hash(data['password']))
    if not fields:
        return jsonify({'error': 'no fields to update'}), 400
    values.append(uid)
    sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s RETURNING id, name, email, role"
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
        return jsonify({'error': 'could not update user', 'detail': str(e)}), 400
    cur.close()
    conn.close()
    return jsonify({'id': str(row[0]), 'name': row[1], 'email': row[2], 'role': row[3]})


@app.route('/users/<int:uid>', methods=['DELETE'])
def delete_user(uid):
    if uid == 1:
        return jsonify({'error': 'cannot delete main admin'}), 400
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM users WHERE id=%s RETURNING id', (uid,))
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
        return jsonify({'error': 'could not delete user', 'detail': str(e)}), 400
    cur.close()
    conn.close()
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002)
