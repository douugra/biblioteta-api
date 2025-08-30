import sqlite3
from flask import Flask, jsonify, request, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])  # Permite qualquer origem (você pode limitar depois)
DATABASE = "biblioteca.db"

# ---------- Conexão com Banco ----------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL
            )
        """)
        db.commit()

# ---------- Rotas ----------
@app.route("/api/livros", methods=["GET"])
def get_livros():
    db = get_db()
    livros = db.execute("SELECT * FROM livros").fetchall()
    return jsonify([dict(l) for l in livros])

@app.route("/api/livros/<int:livro_id>", methods=["GET"])
def get_livro(livro_id):
    db = get_db()
    livro = db.execute("SELECT * FROM livros WHERE id=?", (livro_id,)).fetchone()
    if livro:
        return jsonify(dict(livro))
    return jsonify({"erro": "Livro não encontrado"}), 404

@app.route("/api/livros", methods=["POST"])
def add_livro():
    novo = request.json
    if not novo.get("titulo") or not novo.get("autor"):
        return jsonify({"erro": "Título e autor são obrigatórios"}), 400
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO livros (titulo, autor) VALUES (?, ?)", (novo["titulo"], novo["autor"]))
    db.commit()
    novo["id"] = cursor.lastrowid
    return jsonify(novo), 201

@app.route("/api/livros/<int:livro_id>", methods=["DELETE"])
def delete_livro(livro_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM livros WHERE id=?", (livro_id,))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify({"erro": "Livro não encontrado"}), 404
    return jsonify({"msg": f"Livro {livro_id} removido com sucesso"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
