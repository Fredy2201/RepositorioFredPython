from flask import Blueprint, render_template, session, redirect, url_for, request
from decimal import Decimal, ROUND_HALF_UP
import sqlite3
from datetime import date

lm_bp=Blueprint("lm",__name__)

@lm_bp.route("/", methods=["GET", "POST"])
def registrosgastos():
    if "usuario" not in session :
        return redirect(url_for('inicio1'))
    
    conn = sqlite3.connect("lm.db")
    c = conn.cursor()
    c.execute("SELECT gastos.cod_gas, gastos.des_gas, gastos.fec_gas, cat_gas.nom_cat, gastos.mon_gas FROM gastos, cat_gas where cond_gas=1 and cat_gas.cod_cat=gastos.cod_cat ORDER BY fec_gas DESC")
    datos = c.fetchall()

    c.execute("SELECT * FROM cat_gas where cond_cat=1 ORDER BY nom_cat ASC")
    categoria = c.fetchall()

    conn.close()

    if request.method == "POST":
        cat=request.form["cat"]
        des = request.form["des"]
        fec = request.form["fec"]
        mon=Decimal(request.form["mon"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        mon=str(mon)
        cond=1

        conn = sqlite3.connect("lm.db")
        c = conn.cursor()
        c.execute("INSERT INTO gastos (des_gas, fec_gas, mon_gas, cod_cat, cond_gas) VALUES (?, ?, ?, ?, ?)", (des, fec, mon, cat, cond))
        conn.commit()
        conn.close()

        return redirect("/lmregistros")  # Redirigir después de guardar

    return render_template("lmregistros.html", datos=datos, categoria=categoria)

@lm_bp.route("/lmeditargastos/<int:id>", methods=["GET", "POST"])
def lmeditargastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect("lm.db")
    c = conn.cursor()
    c.execute("SELECT * FROM gastos WHERE cod_gas = ?", (id,))
    registro = c.fetchone()
    conn.close()
    if request.method == "POST":
        des = request.form["des"]
        fec = request.form["fec"]
        mon=request.form["mon"]
        cond=1

        conn = sqlite3.connect("lm.db")
        c = conn.cursor()
        c.execute("UPDATE gastos SET des_gas = ?, fec_gas= ?, mon_gas = ?, cond_gas = ? WHERE cod_gas = ?", (des, fec, mon, cond, id))
        conn.commit()
        conn.close()

        return redirect("/lmregistros")  # Redirigir después de guardar
    return render_template("lmeditargastos.html", registro=registro)

@lm_bp.route("/lmborrargastos/<int:id>")
def lmborrargastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("lm.db")
    c = conn.cursor()
    c.execute("UPDATE gastos SET cond_gas=0 WHERE cod_gas = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/lmregistros/")

@lm_bp.route("/lmregistroscategorias", methods=["GET", "POST"])
def registroscategorias():
    if "usuario" not in session :
        return redirect(url_for('inicio1'))
    
    conn = sqlite3.connect("lm.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cat_gas where cond_cat=1 ORDER BY fec_cat DESC")
    datos = c.fetchall()
    conn.close()

    if request.method == "POST":
        nom = request.form["nom"]
        hoy = date.today()
        fecha_formateada = hoy.strftime("%Y-%m-%d")
        cond=1

        conn = sqlite3.connect("lm.db")
        c = conn.cursor()
        c.execute("INSERT INTO cat_gas (nom_cat, fec_cat, cond_cat) VALUES (?, ?, ?)", (nom, fecha_formateada, cond))
        conn.commit()
        conn.close()

        return redirect(url_for("lm.registroscategorias"))  # Redirigir después de guardar

    return render_template("lmregistrocategoriasgastos.html", datos=datos)

@lm_bp.route("/lmeditarcategoriasgastos/<int:id>", methods=["GET", "POST"])
def lmeditarcategoriasgastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect("lm.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cat_gas WHERE cod_cat = ?", (id,))
    registro = c.fetchone()
    conn.close()
    if request.method == "POST":
        nom = request.form["nom"]

        conn = sqlite3.connect("lm.db")
        c = conn.cursor()
        c.execute("UPDATE cat_gas SET nom_cat= ? WHERE cod_cat = ?", (nom, id))
        conn.commit()
        conn.close()

        return redirect(url_for("lm.registroscategorias"))  # Redirigir después de guardar
    return render_template("lmeditarcategoriasgastos.html", registro=registro)

@lm_bp.route("/lmborrargategoriasgastos/<int:id>")
def lmborrarcategoriasgastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("lm.db")
    c = conn.cursor()
    c.execute("UPDATE cat_gas SET cond_cat=0 WHERE cod_cat = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("lm.registroscategorias"))