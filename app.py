from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import sqlite3
from datetime import datetime
import pandas as pd
from io import BytesIO
import re
from functools import wraps
from werkzeug.security import check_password_hash
from DatabaseManager import inicializar_base_dados


inicializar_base_dados()

app = Flask(__name__)
app.secret_key = "hotel_python_palace_2026"

DB_NAME = "hotel.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("cliente_id") and not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def campo_vazio(*campos):
    return any(campo is None or str(campo).strip() == "" for campo in campos)


def validar_nif(nif):
    nif = str(nif).strip()

    if not re.fullmatch(r"\d{9}", nif):
        return False

    soma = 0

    for i in range(8):
        soma += int(nif[i]) * (9 - i)

    resto = soma % 11
    digito = 0 if resto < 2 else 11 - resto

    return digito == int(nif[8])


def validar_datas(data_entrada, data_saida):
    try:
        entrada = datetime.strptime(data_entrada, "%Y-%m-%d").date()
        saida = datetime.strptime(data_saida, "%Y-%m-%d").date()

        if saida <= entrada:
            return False, "A data de saída tem de ser posterior à data de entrada."

        return True, ""

    except ValueError:
        return False, "Formato de data inválido."


def quarto_ocupado(conn, quarto_id, data_entrada, data_saida, reserva_id=None):
    if reserva_id:
        conflito = conn.execute("""
            SELECT id
            FROM reservas
            WHERE quarto_id = ?
            AND id != ?
            AND estado = 'Ativa'
            AND data_entrada < ?
            AND data_saida > ?
        """, (quarto_id, reserva_id, data_saida, data_entrada)).fetchone()
    else:
        conflito = conn.execute("""
            SELECT id
            FROM reservas
            WHERE quarto_id = ?
            AND estado = 'Ativa'
            AND data_entrada < ?
            AND data_saida > ?
        """, (quarto_id, data_saida, data_entrada)).fetchone()

    return conflito is not None


def carregar_quartos():
    conn = get_db()
    quartos = conn.execute("SELECT * FROM quartos ORDER BY numero").fetchall()
    conn.close()
    return quartos


def criar_tabelas():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nif TEXT NOT NULL UNIQUE,
            contacto TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quartos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            preco REAL NOT NULL,
            estado TEXT DEFAULT 'Disponível',
            capacidade INTEGER,
            camas TEXT,
            descricao TEXT,
            amenities TEXT,
            imagem TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            quarto_id INTEGER NOT NULL,
            data_entrada TEXT NOT NULL,
            data_saida TEXT NOT NULL,
            estado TEXT DEFAULT 'Ativa',
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (quarto_id) REFERENCES quartos(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER NOT NULL,
            valor_total REAL,
            valor REAL,
            data_emissao TEXT,
            estado TEXT DEFAULT 'Emitida',
            FOREIGN KEY (reserva_id) REFERENCES reservas(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilizadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            tipo TEXT DEFAULT 'admin'
        )
    """)

    conn.commit()
    conn.close()


def inserir_dados_iniciais():
    conn = get_db()
    cursor = conn.cursor()

    total_quartos = cursor.execute("SELECT COUNT(*) FROM quartos").fetchone()[0]

    if total_quartos == 0:
        quartos = [
            ("101", "Quarto Standard", 80.00, "Disponível", 2, "1 cama de casal", "Pequeno-almoço incluído.", "Wi-Fi, TV, Casa de banho privada", "standard.jpg"),
            ("102", "Quarto Twin", 95.00, "Disponível", 2, "2 camas individuais", "Ideal para estadias profissionais.", "Wi-Fi, Secretária, TV, Ar condicionado", "twin.jpg"),
            ("201", "Suite Python Palace", 180.00, "Disponível", 2, "1 cama king size", "Vista premium e pequeno-almoço incluído.", "Wi-Fi, TV, Jacuzzi, Varanda, Room service", "suite.jpg")
        ]

        cursor.executemany("""
            INSERT INTO quartos 
            (numero, tipo, preco, estado, capacidade, camas, descricao, amenities, imagem)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, quartos)

    total_clientes = cursor.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]

    if total_clientes == 0:
        cursor.execute("""
            INSERT INTO clientes (nome, nif, contacto, email)
            VALUES (?, ?, ?, ?)
        """, ("cliente", "123456789", "", ""))

    conn.commit()
    conn.close()


def carregar_dashboard():
    conn = get_db()

    clientes = conn.execute("""
        SELECT * FROM clientes
        ORDER BY id DESC
    """).fetchall()

    quartos = conn.execute("""
        SELECT * FROM quartos
        ORDER BY numero
    """).fetchall()

    reservas = conn.execute("""
        SELECT 
            reservas.id,
            reservas.cliente_id,
            reservas.quarto_id,
            clientes.nome AS cliente,
            quartos.numero AS quarto,
            quartos.tipo AS tipo_quarto,
            reservas.data_entrada,
            reservas.data_saida,
            reservas.estado
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
        JOIN quartos ON reservas.quarto_id = quartos.id
        ORDER BY reservas.data_entrada DESC
    """).fetchall()

    total_clientes = len(clientes)
    total_quartos = len(quartos)
    total_reservas = len(reservas)

    total_faturacao = 0

    faturacao = conn.execute("""
        SELECT reservas.data_entrada, reservas.data_saida, quartos.preco
        FROM reservas
        JOIN quartos ON reservas.quarto_id = quartos.id
        WHERE reservas.estado = 'Ativa'
    """).fetchall()

    for f in faturacao:
        entrada = datetime.strptime(f["data_entrada"], "%Y-%m-%d")
        saida = datetime.strptime(f["data_saida"], "%Y-%m-%d")
        total_faturacao += (saida - entrada).days * f["preco"]

    conn.close()

    return {
        "clientes": clientes,
        "quartos": quartos,
        "reservas": reservas,
        "total_clientes": total_clientes,
        "total_quartos": total_quartos,
        "total_reservas": total_reservas,
        "total_faturacao": total_faturacao
    }


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        nif = request.form.get("nif", "").strip()

        if campo_vazio(nome, nif):
            erro = "Preenche o nome e a password/NIF."
            return render_template("login.html", erro=erro)

        conn = get_db()

        admin = conn.execute("""
            SELECT * FROM utilizadores
            WHERE username = ? AND tipo = 'admin'
        """, (nome,)).fetchone()

        if admin and check_password_hash(admin["password_hash"], nif):
            conn.close()
            session.clear()
            session["admin"] = True
            session["admin_nome"] = admin["username"]
            return redirect(url_for("dashboard"))

        cliente = conn.execute("""
            SELECT * FROM clientes
            WHERE nome = ? AND nif = ?
        """, (nome, nif)).fetchone()

        conn.close()

        if cliente:
            session.clear()
            session["cliente_id"] = cliente["id"]
            session["cliente_nome"] = cliente["nome"]
            return redirect(url_for("reservas"))

        return render_template("erro_login.html")

    return render_template("login.html", erro=erro)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/quartos")
@login_required
def quartos():
    conn = get_db()
    quartos = conn.execute("SELECT * FROM quartos ORDER BY numero").fetchall()
    conn.close()

    return render_template("quartos.html", quartos=quartos)


@app.route("/reservas")
@login_required
def reservas():
    quartos = carregar_quartos()
    return render_template("reservas.html", quartos=quartos)


@app.route("/criar_reserva", methods=["POST"])
@login_required
def criar_reserva():
    if not session.get("cliente_id"):
        return redirect(url_for("login"))

    quarto_id = request.form.get("quarto_id")
    data_entrada = request.form.get("data_entrada")
    data_saida = request.form.get("data_saida")

    quartos = carregar_quartos()

    if campo_vazio(quarto_id, data_entrada, data_saida):
        return render_template(
            "reservas.html",
            erro="Preenche todos os campos obrigatórios.",
            quartos=quartos
        )

    datas_validas, mensagem = validar_datas(data_entrada, data_saida)

    if not datas_validas:
        return render_template(
            "reservas.html",
            erro=mensagem,
            quartos=quartos
        )

    conn = get_db()

    if quarto_ocupado(conn, quarto_id, data_entrada, data_saida):
        conn.close()
        return render_template(
            "reservas.html",
            erro="Este quarto não está disponível nas datas escolhidas.",
            quartos=quartos
        )

    conn.execute("""
        INSERT INTO reservas 
        (cliente_id, quarto_id, data_entrada, data_saida, estado)
        VALUES (?, ?, ?, ?, 'Ativa')
    """, (
        session["cliente_id"],
        quarto_id,
        data_entrada,
        data_saida
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("calendario"))


@app.route("/calendario")
@login_required
def calendario():
    conn = get_db()

    clientes = conn.execute("""
        SELECT * FROM clientes
        ORDER BY nome
    """).fetchall()

    quartos = conn.execute("""
        SELECT * FROM quartos
        ORDER BY numero
    """).fetchall()

    conn.close()

    return render_template(
        "calendario.html",
        clientes=clientes,
        quartos=quartos,
        is_admin=session.get("admin", False)
    )


@app.route("/api/reservas")
@login_required
def api_reservas():
    conn = get_db()

    reservas = conn.execute("""
        SELECT 
            reservas.id,
            clientes.nome AS cliente,
            quartos.numero AS quarto,
            quartos.tipo AS tipo_quarto,
            quartos.id AS quarto_id,
            reservas.data_entrada,
            reservas.data_saida
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
        JOIN quartos ON reservas.quarto_id = quartos.id
        WHERE reservas.estado = 'Ativa'
    """).fetchall()

    conn.close()

    cores = [
        "#2563eb", "#16a34a", "#dc2626", "#9333ea",
        "#ea580c", "#0891b2", "#be123c", "#4f46e5"
    ]

    eventos = []

    for r in reservas:
        cor = cores[r["quarto_id"] % len(cores)]

        eventos.append({
            "id": r["id"],
            "title": f"Quarto {r['quarto']} - {r['cliente']}",
            "start": r["data_entrada"],
            "end": r["data_saida"],
            "backgroundColor": cor,
            "borderColor": cor,
            "extendedProps": {
                "cliente": r["cliente"],
                "quarto": r["quarto"],
                "tipo_quarto": r["tipo_quarto"]
            },
            "url": url_for("fatura", reserva_id=r["id"])
        })

    return jsonify(eventos)

@app.route("/fatura/<int:reserva_id>")
@login_required
def fatura(reserva_id):
    conn = get_db()

    reserva = conn.execute("""
        SELECT 
            reservas.id,
            reservas.cliente_id,
            clientes.nome,
            clientes.nif,
            quartos.numero,
            quartos.tipo,
            quartos.preco,
            reservas.data_entrada,
            reservas.data_saida
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
        JOIN quartos ON reservas.quarto_id = quartos.id
        WHERE reservas.id = ?
    """, (reserva_id,)).fetchone()

    conn.close()

    if not reserva:
        return "Reserva não encontrada."

    if session.get("cliente_id") and reserva["cliente_id"] != session.get("cliente_id"):
        return redirect(url_for("reservas"))

    entrada = datetime.strptime(reserva["data_entrada"], "%Y-%m-%d")
    saida = datetime.strptime(reserva["data_saida"], "%Y-%m-%d")
    noites = (saida - entrada).days
    total = noites * reserva["preco"]

    return render_template(
        "fatura.html",
        reserva=reserva,
        noites=noites,
        total=total,
        data_emissao=datetime.now().strftime("%d/%m/%Y")
    )


@app.route("/dashboard")
@admin_required
def dashboard():
    dados = carregar_dashboard()
    erro = session.pop("erro_dashboard", None)
    sucesso = session.pop("sucesso_dashboard", None)

    return render_template(
        "dashboard.html",
        erro=erro,
        sucesso=sucesso,
        **dados
    )


@app.route("/admin/adicionar_quarto", methods=["POST"])
@admin_required
def adicionar_quarto():
    numero = request.form.get("numero")
    tipo = request.form.get("tipo")
    preco = request.form.get("preco")
    capacidade = request.form.get("capacidade")
    camas = request.form.get("camas")
    descricao = request.form.get("descricao")
    amenities = request.form.get("amenities")
    imagem = request.form.get("imagem")

    if campo_vazio(numero, tipo, preco, capacidade, camas):
        session["erro_dashboard"] = "Preenche os campos obrigatórios do quarto."
        return redirect(url_for("dashboard"))

    try:
        preco = float(preco)
        capacidade = int(capacidade)
    except ValueError:
        session["erro_dashboard"] = "Preço ou capacidade inválidos."
        return redirect(url_for("dashboard"))

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO quartos 
            (numero, tipo, preco, capacidade, camas, descricao, amenities, imagem, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Disponível')
        """, (
            numero,
            tipo,
            preco,
            capacidade,
            camas,
            descricao,
            amenities,
            imagem
        ))

        conn.commit()
        session["sucesso_dashboard"] = "Quarto adicionado com sucesso."

    except sqlite3.IntegrityError:
        session["erro_dashboard"] = "Já existe um quarto com esse número."

    finally:
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/admin/editar_quarto/<int:id>", methods=["POST"])
@admin_required
def editar_quarto(id):
    numero = request.form.get("numero")
    tipo = request.form.get("tipo")
    preco = request.form.get("preco")
    capacidade = request.form.get("capacidade")
    camas = request.form.get("camas")
    descricao = request.form.get("descricao")
    amenities = request.form.get("amenities")
    imagem = request.form.get("imagem")

    if campo_vazio(numero, tipo, preco, capacidade, camas):
        session["erro_dashboard"] = "Preenche os campos obrigatórios do quarto."
        return redirect(url_for("dashboard"))

    try:
        preco = float(preco)
        capacidade = int(capacidade)
    except ValueError:
        session["erro_dashboard"] = "Preço ou capacidade inválidos."
        return redirect(url_for("dashboard"))

    conn = get_db()

    try:
        conn.execute("""
            UPDATE quartos
            SET numero = ?,
                tipo = ?,
                preco = ?,
                capacidade = ?,
                camas = ?,
                descricao = ?,
                amenities = ?,
                imagem = ?
            WHERE id = ?
        """, (
            numero,
            tipo,
            preco,
            capacidade,
            camas,
            descricao,
            amenities,
            imagem,
            id
        ))

        conn.commit()
        session["sucesso_dashboard"] = "Quarto atualizado com sucesso."

    except sqlite3.IntegrityError:
        session["erro_dashboard"] = "Já existe um quarto com esse número."

    finally:
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/admin/remover_quarto/<int:id>")
@admin_required
def remover_quarto(id):
    conn = get_db()
    conn.execute("DELETE FROM reservas WHERE quarto_id = ?", (id,))
    conn.execute("DELETE FROM quartos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    session["sucesso_dashboard"] = "Quarto removido com sucesso."
    return redirect(url_for("dashboard"))


@app.route("/admin/adicionar_cliente", methods=["POST"])
@admin_required
def adicionar_cliente():
    nome = request.form.get("nome")
    nif = request.form.get("nif")
    contacto = request.form.get("contacto", "")
    email = request.form.get("email", "")

    if campo_vazio(nome, nif):
        session["erro_dashboard"] = "Preenche o nome e o NIF do cliente."
        return redirect(url_for("dashboard"))

    if not validar_nif(nif):
        session["erro_dashboard"] = "NIF inválido."
        return redirect(url_for("dashboard"))

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO clientes (nome, nif, contacto, email)
            VALUES (?, ?, ?, ?)
        """, (
            nome,
            nif,
            contacto,
            email
        ))

        conn.commit()
        session["sucesso_dashboard"] = "Cliente adicionado com sucesso."

    except sqlite3.IntegrityError:
        session["erro_dashboard"] = "Já existe um cliente com esse NIF."

    finally:
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/admin/editar_cliente/<int:id>", methods=["POST"])
@admin_required
def editar_cliente(id):
    nome = request.form.get("nome")
    nif = request.form.get("nif")
    contacto = request.form.get("contacto", "")
    email = request.form.get("email", "")

    if campo_vazio(nome, nif):
        session["erro_dashboard"] = "Preenche o nome e o NIF do cliente."
        return redirect(url_for("dashboard"))

    if not validar_nif(nif):
        session["erro_dashboard"] = "NIF inválido."
        return redirect(url_for("dashboard"))

    conn = get_db()

    try:
        conn.execute("""
            UPDATE clientes
            SET nome = ?,
                nif = ?,
                contacto = ?,
                email = ?
            WHERE id = ?
        """, (
            nome,
            nif,
            contacto,
            email,
            id
        ))

        conn.commit()
        session["sucesso_dashboard"] = "Cliente atualizado com sucesso."

    except sqlite3.IntegrityError:
        session["erro_dashboard"] = "Já existe outro cliente com esse NIF."

    finally:
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/admin/remover_cliente/<int:id>")
@admin_required
def remover_cliente(id):
    conn = get_db()
    conn.execute("DELETE FROM reservas WHERE cliente_id = ?", (id,))
    conn.execute("DELETE FROM clientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    session["sucesso_dashboard"] = "Cliente removido com sucesso."
    return redirect(url_for("dashboard"))


@app.route("/admin/adicionar_reserva", methods=["POST"])
@admin_required
def adicionar_reserva_admin():
    cliente_id = request.form.get("cliente_id")
    quarto_id = request.form.get("quarto_id")
    data_entrada = request.form.get("data_entrada")
    data_saida = request.form.get("data_saida")

    if campo_vazio(cliente_id, quarto_id, data_entrada, data_saida):
        session["erro_dashboard"] = "Preenche todos os campos da reserva."
        return redirect(url_for("dashboard"))

    datas_validas, mensagem = validar_datas(data_entrada, data_saida)

    if not datas_validas:
        session["erro_dashboard"] = mensagem
        return redirect(url_for("dashboard"))

    conn = get_db()

    if quarto_ocupado(conn, quarto_id, data_entrada, data_saida):
        conn.close()
        session["erro_dashboard"] = "Este quarto já está ocupado nesse período."
        return redirect(url_for("dashboard"))

    conn.execute("""
        INSERT INTO reservas 
        (cliente_id, quarto_id, data_entrada, data_saida, estado)
        VALUES (?, ?, ?, ?, 'Ativa')
    """, (
        cliente_id,
        quarto_id,
        data_entrada,
        data_saida
    ))

    conn.commit()
    conn.close()

    session["sucesso_dashboard"] = "Reserva adicionada com sucesso."
    return redirect(url_for("dashboard"))


@app.route("/admin/editar_reserva/<int:id>", methods=["POST"])
@admin_required
def editar_reserva(id):
    cliente_id = request.form.get("cliente_id")
    quarto_id = request.form.get("quarto_id")
    data_entrada = request.form.get("data_entrada")
    data_saida = request.form.get("data_saida")
    estado = request.form.get("estado")

    if campo_vazio(cliente_id, quarto_id, data_entrada, data_saida, estado):
        session["erro_dashboard"] = "Preenche todos os campos da reserva."
        return redirect(url_for("dashboard"))

    datas_validas, mensagem = validar_datas(data_entrada, data_saida)

    if not datas_validas:
        session["erro_dashboard"] = mensagem
        return redirect(url_for("dashboard"))

    conn = get_db()

    if estado == "Ativa" and quarto_ocupado(conn, quarto_id, data_entrada, data_saida, id):
        conn.close()
        session["erro_dashboard"] = "Este quarto já está ocupado nesse período."
        return redirect(url_for("dashboard"))

    conn.execute("""
        UPDATE reservas
        SET cliente_id = ?,
            quarto_id = ?,
            data_entrada = ?,
            data_saida = ?,
            estado = ?
        WHERE id = ?
    """, (
        cliente_id,
        quarto_id,
        data_entrada,
        data_saida,
        estado,
        id
    ))

    conn.commit()
    conn.close()

    session["sucesso_dashboard"] = "Reserva atualizada com sucesso."
    return redirect(url_for("dashboard"))


@app.route("/admin/remover_reserva/<int:id>")
@admin_required
def remover_reserva(id):
    conn = get_db()
    conn.execute("DELETE FROM reservas WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    session["sucesso_dashboard"] = "Reserva removida com sucesso."
    return redirect(url_for("dashboard"))


@app.route("/admin/exportar_excel")
@admin_required
def exportar_excel():
    conn = get_db()

    clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    quartos = pd.read_sql_query("SELECT * FROM quartos", conn)
    reservas = pd.read_sql_query("SELECT * FROM reservas", conn)
    faturas = pd.read_sql_query("SELECT * FROM faturas", conn)

    conn.close()

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        clientes.to_excel(writer, sheet_name="clientes", index=False)
        quartos.to_excel(writer, sheet_name="quartos", index=False)
        reservas.to_excel(writer, sheet_name="reservas", index=False)
        faturas.to_excel(writer, sheet_name="faturas", index=False)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="hotel_python_palace_backup.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/admin/importar_excel", methods=["POST"])
@admin_required
def importar_excel():
    ficheiro = request.files.get("ficheiro_excel")

    if not ficheiro:
        session["erro_dashboard"] = "Escolhe um ficheiro Excel para importar."
        return redirect(url_for("dashboard"))

    try:
        excel = pd.ExcelFile(ficheiro)
    except Exception:
        session["erro_dashboard"] = "Ficheiro Excel inválido."
        return redirect(url_for("dashboard"))

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM faturas")
        cursor.execute("DELETE FROM reservas")
        cursor.execute("DELETE FROM quartos")
        cursor.execute("DELETE FROM clientes")

        if "clientes" in excel.sheet_names:
            clientes = pd.read_excel(excel, sheet_name="clientes")
            clientes.to_sql("clientes", conn, if_exists="append", index=False)

        if "quartos" in excel.sheet_names:
            quartos = pd.read_excel(excel, sheet_name="quartos")
            quartos.to_sql("quartos", conn, if_exists="append", index=False)

        if "reservas" in excel.sheet_names:
            reservas = pd.read_excel(excel, sheet_name="reservas")
            reservas.to_sql("reservas", conn, if_exists="append", index=False)

        if "faturas" in excel.sheet_names:
            faturas = pd.read_excel(excel, sheet_name="faturas")
            faturas.to_sql("faturas", conn, if_exists="append", index=False)

        conn.commit()
        session["sucesso_dashboard"] = "Base de dados importada com sucesso."

    except Exception as e:
        conn.rollback()
        session["erro_dashboard"] = f"Erro ao importar Excel: {e}"

    finally:
        conn.close()

    return redirect(url_for("dashboard"))


@app.route("/api/criar_reserva_calendario", methods=["POST"])
@admin_required
def criar_reserva_calendario():
    dados = request.json

    cliente_id = dados.get("cliente_id")
    quarto_id = dados.get("quarto_id")
    data_entrada = dados.get("data_entrada")
    data_saida = dados.get("data_saida")

    if campo_vazio(cliente_id, quarto_id, data_entrada, data_saida):
        return jsonify({"erro": "Preenche todos os campos."}), 400

    datas_validas, mensagem = validar_datas(data_entrada, data_saida)

    if not datas_validas:
        return jsonify({"erro": mensagem}), 400

    conn = get_db()

    if quarto_ocupado(conn, quarto_id, data_entrada, data_saida):
        conn.close()
        return jsonify({"erro": "Quarto indisponível."}), 400

    conn.execute("""
        INSERT INTO reservas
        (cliente_id, quarto_id, data_entrada, data_saida, estado)
        VALUES (?, ?, ?, ?, 'Ativa')
    """, (
        cliente_id,
        quarto_id,
        data_entrada,
        data_saida
    ))

    conn.commit()
    conn.close()

    return jsonify({"sucesso": True})


if __name__ == "__main__":
    criar_tabelas()
    inserir_dados_iniciais()
    app.run(debug=True)

@app.errorhandler(404)
def erro_404(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def erro_500(error):
    return render_template("500.html"), 500