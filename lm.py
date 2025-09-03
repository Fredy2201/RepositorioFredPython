from flask import Blueprint, render_template, session, redirect, url_for, request
from decimal import Decimal, ROUND_HALF_UP
import sqlite3

lm_bp=Blueprint("lm",__name__)

@lm_bp.route("/", methods=["GET", "POST"])
def registrosgastos():
    if "usuario" not in session :
        return redirect(url_for('inicio1'))
    
    conn = sqlite3.connect("lm.db")
    c = conn.cursor()
    c.execute("SELECT * FROM gastos where cond_gas=1 ORDER BY fec_gas DESC")
    datos = c.fetchall()
    conn.close()

    if request.method == "POST":
        des = request.form["des"]
        fec = request.form["fec"]
        mon=Decimal(request.form["mon"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        mon=str(mon)
        cond=1

        conn = sqlite3.connect("lm.db")
        c = conn.cursor()
        c.execute("INSERT INTO gastos (des_gas, fec_gas, mon_gas, cond_gas) VALUES (?, ?, ?, ?)", (des, fec, mon, cond))
        conn.commit()
        conn.close()

        return redirect("/lmregistros")  # Redirigir después de guardar

    return render_template("lmregistros.html", datos=datos)

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