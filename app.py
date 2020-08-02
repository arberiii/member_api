from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = "admin"
api_password = "pass"

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({"message": "auth failed"}), 401
    return decorated

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()

    cur = db.execute("select id, name, email, level from members")
    results = cur.fetchall()

    all_members = []
    for result in results:
        member = {"id": result["id"], "name": result["name"], "email": result["email"], "level": result["level"]}
        all_members.append(member)

    return jsonify({"members": all_members})


@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()

    cur = db.execute("select id, name, email, level from members where id = ?", [member_id])
    result = cur.fetchone()
    member = {"id": result["id"], "name": result["name"], "email": result["email"], "level": result["level"]}
    return jsonify(member)

@app.route('/member', methods=['POST'])
@protected
def add_member():
    new_member = request.get_json()

    name = new_member["name"]
    email = new_member["email"]
    level = new_member["level"]

    db = get_db()
    db.execute("insert into members(name, email, level) values(?,?,?)", [name, email, level])
    db.commit()

    mem_cur = db.execute("select id, name, email, level from members where name=?", [name])
    mem = mem_cur.fetchone()

    return jsonify({"id": mem["id"], "name": mem["name"], "email": mem["email"], "level": mem["level"]})

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    new_member_data = request.get_json()

    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
    db.commit()

    member_cur = db.execute('select id, name, email, level from members where id = ?', [member_id])
    member = member_cur.fetchone()

    return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})


@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    db.execute('delete from members where id = ?', [member_id])
    db.commit()

    return jsonify({'message': 'The member has been deleted!'})