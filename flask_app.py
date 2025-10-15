from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
import sqlite3
from lm import lm_bp
from flask import jsonify

app = Flask(__name__)
app.secret_key="f84b2a5c1e764eac9c2d8b9c1fb13e7a"
#app.permanent_session_lifetime = timedelta(minutes=10) 

@app.route("/")
def inicio():
    return redirect("/login")

app.register_blueprint(lm_bp, url_prefix="/lmregistros")


# Ruta principal con formulario
@app.route("/formventas", methods=["GET", "POST"])
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes where cond_cli=1")
    datos = c.fetchall()
    conn.close()

    if request.method == "POST":
        nom = request.form["nom"]
        fecha = request.form["date"]
        mon_cob=request.form["mon_cob"]
        mon_pag=request.form["mon_pag"]
        cond_ven=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO ventas (cod_cli, fec_ven, cobro , pago, cond_ven) VALUES (?, ?, ?, ?, ?)", (nom, fecha, mon_cob, mon_pag, cond_ven))
        conn.commit()
        conn.close()

        return redirect("/registrosventas")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario_ventas.html", registros=datos)


@app.route("/form1ventas", methods=["GET", "POST"])
def form1ventas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if "carrito" not in session:
        session["carrito"] = []
    if "datos_for" not in session:
            session["datos_for"] = []

    totalcob = sum(Decimal(str(item.get("mon_cob",0))) for item in session["carrito"])
    totalpag = sum(Decimal(str(item.get("mon_pag",0))) for item in session["carrito"])

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT MAX(cod_ven) as codalto FROM ventas where cond_ven=1")
    codigoalto = c.fetchone()[0]
    if codigoalto is None:
        codigoalto = 0

    c.execute("SELECT * FROM clientes where cond_cli=1 ORDER BY nom_cli asc")
    clientes = c.fetchall()

    c.execute("SELECT * FROM plataformas where cond_pla=1 ")
    plataformas = c.fetchall()

    conn.close()

    if request.method == "POST":
        nom = request.form["nom"]
        fecha = request.form["date"]
        mon_cob=float(request.form["mon_cob"])
        mon_pag=float(request.form["mon_pag"])
        cond_ven=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO ventas (cod_cli, fec_ven, cobro , pago, cond_ven) VALUES (?, ?, ?, ?, ?)", (nom, fecha, mon_cob, mon_pag, cond_ven))
        conn.commit()


        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        
        carrito = session.get("carrito", [])
        for item in carrito:
            c.execute("""
                INSERT INTO cuentas 
                (cod_pla, cod_ven, correo, password, perfil, clave, tiempo, fec_ini, fec_cul, cond_cue, cob, pag) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id_pla"], 
                codigoalto+1, 
                item["correo"], 
                item["password"], 
                item["perfil"], 
                item["clave"], 
                item["tiempo"], 
                item["dateinicio"], 
                item["datefin"], 
                1,   # cond_cue
                item["mon_cob"],
                item["mon_pag"],
            ))

        
        conn.commit()
        conn.close()
        session.pop("carrito", None)


        return redirect("/registrosventas")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario1_ventas.html", registros=clientes, carrito=session["carrito"], plataformas=plataformas, datos_for=session["datos_for"],totalcob=totalcob,totalpag=totalpag)

@app.route("/agregar_servicio", methods=["POST"])
def agregarservicio():
    

    plataforma=request.form["plataforma"]
    id_pla,nom_pla=plataforma.split("|")
    correo=request.form["correo"]
    password=request.form["password"]
    perfil=request.form["perfil"]
    clave=request.form["clave"]
    tiempo=request.form["tiempo"]
    dateinicio=request.form["dateinicio"]
    datefin=request.form["datefin"]
    moncob=request.form["moncob"]
    monpag=request.form["monpag"]

    moncob = Decimal(moncob).quantize(Decimal("0.00"))
    monpag = Decimal(monpag).quantize(Decimal("0.00"))

    item={
        "id_pla": id_pla,
        "nom_pla":nom_pla,
        "correo": correo,
        "password": password,
        "perfil": perfil,
        "clave": clave,
        "tiempo": tiempo,
        "dateinicio":dateinicio,
        "datefin": datefin,
        "mon_cob": moncob,
        "mon_pag": monpag
    }
    carrito = session.get("carrito", [])
    carrito.append(item)
    session["carrito"] = carrito



    return redirect("/form1ventas")

@app.route("/borrar1ventas/<int:index>")
def borrar1ventas(index):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    carrito = session.get("carrito", [])
    if 0 <= index < len(carrito):
        del carrito[index]
        session["carrito"] = carrito
    return redirect(url_for("form1ventas"))


@app.route("/form1clientes", methods=["GET", "POST"])
def form1clientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        cliente=request.form["cliente"]
        phone=request.form["phone"]
        nomcont = request.form["nomcont"]
        cond_cli=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO clientes (nom_cli, whatsapp, nom_cont, cond_cli) VALUES (?, ?, ?, ?)", (cliente, phone, nomcont, cond_cli))
        conn.commit()
        conn.close()

    return redirect("/form1ventas")  

# Mostrar registros
@app.route("/registrosventas")
def registros():
    if "usuario" not in session or session["usuario"]["rol"] != 5:
        return redirect(url_for('inicio1'))
    

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT cod_ven, clientes.nom_cli, fec_ven, cobro, pago FROM ventas, clientes where ventas.cod_cli=clientes.id and ventas.cond_ven=1 ORDER BY cod_ven DESC")
    datos = c.fetchall()
    conn.close()
    return render_template("registros_ventas.html", registros=datos)

@app.route("/editarventas/<int:id>", methods=["GET", "POST"])
def editarventas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        cliente = request.form["cliente"]
        fec_ven = request.form["fec_ven"]
        mon_cob = request.form["mon_cob"]
        mon_pag = request.form["mon_pag"]

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""
            UPDATE ventas
            SET cod_cli = ?, fec_ven = ?, cobro = ?, pago = ?
            WHERE cod_ven = ?
        """, (cliente, fec_ven, mon_cob, mon_pag, id))
        conn.commit()
        conn.close()

        return redirect("/registrosventas")

    # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM ventas WHERE cod_ven = ?", (id,))
    registro = c.fetchone()
    conn.close()

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes where cond_cli=1")
    datos = c.fetchall()
    conn.close()

    return render_template("editarventas.html", registro=registro, datos=datos)

@app.route("/borrarventas/<int:id>")
def borrarventas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE ventas SET cond_ven=0 WHERE cod_ven = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/registrosventas")

# FORMULARIO CLIENTES
@app.route("/form_clientes", methods=["GET", "POST"])
def formClientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        nombre = request.form["NomCliente"]
        whatsapp = request.form["phone"]
        nom_cont=request.form["nom_cont"]
        cond_cli=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO clientes (nom_cli, whatsapp, nom_cont, cond_cli) VALUES (?, ?, ?, ?)", (nombre, whatsapp, nom_cont, cond_cli))
        conn.commit()
        conn.close()

        return redirect("/registrosclientes")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario_clientes.html")


@app.route("/reportesplataformas")
def reportesplataformas():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes where cond_cli=1 ORDER BY nom_cli asc")
    datos = c.fetchall()

    c.execute("SELECT SUM(cobro) AS total_cobro, SUM(pago) as total_pago FROM ventas;")
    ingresos = c.fetchone()

    conn.close()
    return render_template("reportes_plataformas.html", datos=datos, ingresos=ingresos)

@app.route("/registrosclientes")
def registrosClientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes where cond_cli=1 ORDER BY nom_cli asc")
    datos = c.fetchall()
    conn.close()
    return render_template("registros_clientes.html", registros=datos)

@app.route("/editarclientes/<int:id>", methods=["GET", "POST"])
def editarclientes(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        nombre = request.form["nombre"]
        whatsapp = request.form["whatsapp"]
        nom_cont = request.form["nom_cont"]

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""
            UPDATE clientes
            SET nom_cli = ?, whatsapp = ?, nom_cont = ?
            WHERE id = ?
        """, (nombre, whatsapp, nom_cont, id))
        conn.commit()
        conn.close()

        return redirect("/registrosclientes")

    # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE id = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("editarclientes.html", registro=registro)

@app.route("/borrarclientes/<int:id>")
def borrarclientes(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE clientes SET cond_cli=0 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/registrosclientes")

# FORMULARIO CUENTAS
@app.route("/form_cuentas", methods=["GET", "POST"])
def formcuentas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM plataformas where cond_pla=1")
    datos = c.fetchall()
    conn.close()

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM ventas where cond_VEN=1")
    ventas = c.fetchall()
    conn.close()

    if request.method == "POST":
        plataforma = request.form["plataforma"]
        ven = request.form["ven"]
        correo=request.form["correo"]
        password=request.form["password"]
        perfil=request.form["perfil"]
        clave=request.form["clave"]
        tiempo=request.form["tiempo"]
        dateinicio=request.form["dateinicio"]
        datefin=request.form["datefin"]
        cond_cue=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO cuentas (cod_pla, cod_ven, correo, password, perfil, clave, tiempo, fec_ini, fec_cul, cond_cue) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (plataforma, ven, correo, password, perfil, clave, tiempo, dateinicio, datefin, cond_cue))
        conn.commit()
        conn.close()
        
        return redirect("/registroscuentas")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario_cuentas.html", registros=datos, ventas=ventas)

@app.route("/registroscuentas")
def registroscuentas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT cuentas.cod_cue,plataformas.nom_pla,cuentas.cod_ven,cuentas.correo,cuentas.password,cuentas.perfil,cuentas.clave,cuentas.tiempo,cuentas.fec_ini,cuentas.fec_cul,cuentas.cond_cue, cob, pag, ROUND(julianday(cuentas.fec_cul) - julianday(date('now'))) AS dias_restantes FROM cuentas,plataformas where cond_cue=1 AND cuentas.cod_pla=plataformas.cod_pla ORDER BY cod_cue DESC")
    datos = c.fetchall()
    conn.close()
    return render_template("registros_cuentas.html", registros=datos)

@app.route("/editarcuentas/<int:id>", methods=["GET", "POST"])
def editarcuentas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM plataformas where cond_pla=1")
    datos = c.fetchall()
    conn.close()

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM ventas where cond_ven=1")
    ventas = c.fetchall()
    conn.close()

    if request.method == "POST":
        # Procesar actualización
        plataforma = request.form["plataforma"]
        ven = request.form["ven"]
        correo=request.form["correo"]
        password=request.form["password"]
        perfil=request.form["perfil"]
        clave=request.form["clave"]
        tiempo=request.form["tiempo"]
        dateinicio=request.form["dateinicio"]
        datefin=request.form["datefin"]
        cond_cue=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("UPDATE cuentas SET cod_pla=?, cod_ven=?, correo=?, password=?, perfil=?, clave=?, tiempo=?, fec_ini=?, fec_cul=?, cond_cue=?WHERE cod_cue=?", (plataforma, ven, correo, password, perfil, clave, tiempo, dateinicio, datefin, cond_cue, id))
        conn.commit()
        conn.close()

        return redirect("/registroscuentas")

    # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cuentas WHERE cod_cue = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("editarcuentas.html", registro=registro, datos=datos, ventas=ventas)

@app.route("/borrarcuentas/<int:id>")
def borrarcuentas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE cuentas SET cond_cue=0 WHERE cod_cue = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/registroscuentas")

#ESTADO DE CUENTAS
#------------------------------------------------------------------------------------------------------------

@app.route("/formestadocuentas", methods=["GET", "POST"])
def formestadocuentas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        estadocuentas = request.form["estadocuentas"]
        cond_est=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO estadocuentas (nom_est, cond_est) VALUES (?, ?)", (estadocuentas, cond_est))
        conn.commit()
        conn.close()

        return redirect("/registrosestadocuentas")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario_estadocuentas.html")

# Mostrar registros
@app.route("/registrosestadocuentas")
def registrosestadocuentas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM estadocuentas WHERE cond_est=1")
    datos = c.fetchall()
    conn.close()
    return render_template("registros_estadocuentas.html", registros=datos)

@app.route("/editarestadocuentas/<int:id>", methods=["GET", "POST"])
def editarestadocuentas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        estadocuentas = request.form["estadocuentas"]

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""
            UPDATE estadocuentas
            SET nom_est = ?
            WHERE cod_est = ?
        """, (estadocuentas, id))
        conn.commit()
        conn.close()

        return redirect("/registrosestadocuentas")

    # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM estadocuentas WHERE cod_est = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("editarestadocuentas.html", registro=registro)

@app.route("/borrarestadocuentas/<int:id>")
def borrarestadocuentas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE estadocuentas SET cond_est = 0 WHERE cod_est = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/registrosestadocuentas")


#NOTIFICACIONES
#--------------------------------------------------------------------------------------------------------------------------


@app.route("/formnotificaciones", methods=["GET", "POST"])
def formnotificaciones():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tiponotificacion WHERE cond_tip_not = 1")
    registro = c.fetchall()
    conn.close()

    if request.method == "POST":
        fecnotificacion=request.form["fecnotificacion"]
        cod_cue=request.form["cod_cue"]
        tip_not = request.form["tip_not"]
        cond_not=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO notificaciones (fec_not, cod_cue, tip_not, cond_not) VALUES (?, ?, ?, ?)", (fecnotificacion, cod_cue, tip_not, cond_not))
        conn.commit()
        conn.close()

        return redirect("/registrosnotificaciones")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario_notificaciones.html", registro=registro)

# Mostrar registros
@app.route("/registrosnotificaciones")
def registrosnotificaciones():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT notificaciones.cod_not, notificaciones.fec_not,cod_cue, tiponotificacion.nom_tip FROM notificaciones,tiponotificacion WHERE notificaciones.cond_not=1")
    datos = c.fetchall()
    conn.close()
    return render_template("registros_notificaciones.html", registros=datos)

@app.route("/editarnotificaciones/<int:id>", methods=["GET", "POST"])
def editarnotificaciones(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        fecnotificacion=request.form["fecnotificacion"]
        cod_cue=request.form["cod_cue"]
        tip_not = request.form["tip_not"]
        cond_not=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""
            UPDATE notificaciones
            SET fec_not = ?, cod_cue=?, tip_not=?, cond_not=?
            WHERE cod_not = ?
        """, (fecnotificacion, cod_cue, tip_not,cond_not, id))
        conn.commit()
        conn.close()

        return redirect("/registrosnotificaciones")

    # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notificaciones WHERE cod_not = ?", (id,))
    registro = c.fetchone()
    conn.close()

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tiponotificacion WHERE cond_tip_not = 1")
    datos = c.fetchall()
    conn.close()

    return render_template("editarnotificaciones.html", registro=registro, datos=datos)

@app.route("/borrarnotificaciones/<int:id>")
def borrarnotificaciones(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE notificaciones SET cond_not = 0 WHERE cod_not = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/registrosnotificaciones")


#Notificaciones
#----------------------------------------------------------------------------------------------------------------


@app.route("/formtiponotificaciones", methods=["GET", "POST"])
def formtiponotificaciones():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    

    if request.method == "POST":
        nomtip=request.form["nomtip"]
        tiempo=request.form["tiempo"]
        cond_tip_not=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO tiponotificacion (nom_tip, tiempo, cond_tip_not) VALUES (?, ?, ?)", (nomtip, tiempo, cond_tip_not))
        conn.commit()
        conn.close()

        return redirect("/registrostiponotificaciones")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario_tiponotificaciones.html")

# Mostrar registros
@app.route("/registrostiponotificaciones")
def registrostiponotificaciones():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tiponotificacion WHERE cond_tip_not=1")
    datos = c.fetchall()
    conn.close()
    return render_template("registros_tiponotificaciones.html", registros=datos)

@app.route("/editartiponotificaciones/<int:id>", methods=["GET", "POST"])
def editartiponotificaciones(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        tipnot=request.form["tipnot"]
        dettie = request.form["dettie"]
        cond_tip_not=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""
            UPDATE tiponotificacion
            SET nom_tip = ?, tiempo=?, cond_tip_not=?
            WHERE cod_tip_not = ?
        """, (tipnot, dettie, cond_tip_not, id))
        conn.commit()
        conn.close()

        return redirect("/registrostiponotificaciones")

    # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tiponotificacion WHERE cod_tip_not = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("editartiponotificaciones.html", registro=registro)

@app.route("/borrartiponotificaciones/<int:id>")
def borrartiponotificaciones(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE tiponotificacion SET cond_tip_not = 0 WHERE cod_tip_not = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/registrostiponotificaciones")


#PLATAFORMAS
#-------------------------------------------------------------------------------------------------------------------


@app.route("/formplataformas", methods=["GET", "POST"])
def formplataformas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    

    if request.method == "POST":
        nompla=request.form["nompla"]
        cond_pla=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("INSERT INTO plataformas (nom_pla, cond_pla) VALUES (?, ?)", (nompla, cond_pla))
        conn.commit()
        conn.close()

        return redirect("/registrosplataformas")  # Redirigir después de guardar

    # Mostrar formulario
    return render_template("formulario_plataformas.html")

# Mostrar registros
@app.route("/registrosplataformas")
def registrosplataformas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM plataformas WHERE cond_pla=1")
    datos = c.fetchall()
    conn.close()
    return render_template("registros_plataformas.html", registros=datos)

@app.route("/editarplataformas/<int:id>", methods=["GET", "POST"])
def editarplataformas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        nompla=request.form["nompla"]
        cond_pla=1

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("""
            UPDATE plataformas
            SET nom_pla = ?, cond_pla=?
            WHERE cod_pla = ?
        """, (nompla, cond_pla, id))
        conn.commit()
        conn.close()

        return redirect("/registrosplataformas")

    # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM plataformas WHERE cod_pla = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("editarplataformas.html", registro=registro)

@app.route("/borrarplataformas/<int:id>")
def borrarplataformas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("UPDATE plataformas SET cond_pla = 0 WHERE cod_pla = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/registrosplataformas")


#REPORTES

@app.route("/reporte_general")
def reportegeneral():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) from ventas WHERE cond_ven=1")
    ventas = c.fetchone()[0]

    c.execute("SELECT COUNT(*) from clientes WHERE cond_cli=1")
    clientes = c.fetchone()[0]

    c.execute("SELECT COUNT(*) from plataformas WHERE cond_pla=1")
    plataformas = c.fetchone()[0]

    c.execute("SELECT COUNT(*) from cuentas WHERE cond_cue=1")
    cuentas = c.fetchone()[0]

    c.execute("SELECT COUNT(*) AS cantidad FROM cuentas WHERE (JULIANDAY(fec_cul) - JULIANDAY(date('now'))) > -1 and cond_cue=1;")
    cuentasact = c.fetchone()[0]

    c.execute("SELECT COUNT(*) AS cantidad FROM cuentas WHERE (JULIANDAY(fec_cul) - JULIANDAY(date('now'))) < 0 and cond_cue=1;")
    cuentasina = c.fetchone()[0]

    c.execute("SELECT COUNT(*) from notificaciones WHERE cond_not=1")
    notificaciones = c.fetchone()[0]

    c.execute("SELECT COUNT(*) from tiponotificacion WHERE cond_tip_not=1")
    tipnotificacion = c.fetchone()[0]

    conn.close()

    return render_template("reportegeneral.html", ventas=ventas, clientes=clientes, plataformas=plataformas, cuentas=cuentas, cuentasact=cuentasact, cuentasina=cuentasina, notificaciones=notificaciones, tipnotificacion=tipnotificacion)

@app.route("/reporte_fechas", methods=["GET", "POST"])
def reportefechas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    # Si viene POST, filtrar por rango
    if request.method == "POST":
        mes1 = request.form["mes1"]
        mes2 = request.form["mes2"]

        c.execute("""
            SELECT strftime('%Y-%m', fec_ven) AS mes, 
                   SUM(cobro-pago) AS total_ventas 
            FROM ventas 
            WHERE cond_ven=1
              AND strftime('%Y-%m', fec_ven) BETWEEN ? AND ? 
            GROUP BY mes 
            ORDER BY mes LIMIT 10
        """, (mes1, mes2))
    else:
        # Si es GET, mostrar todo
        c.execute("""
            SELECT strftime('%Y-%m', fec_ven) AS mes, 
                   SUM(cobro-pago) AS total_ventas 
            FROM ventas 
            GROUP BY mes 
            ORDER BY mes LIMIT 10
        """)

    ventas = c.fetchall()
    conn.close()

    meses = [r[0] for r in ventas]
    totales = [r[1] for r in ventas]

    return render_template("reportefechas.html", meses=meses, totales=totales)

@app.route("/reporte_dias", methods=["GET", "POST"])
def reportedias():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    mesactual= datetime.now()
    mesa= mesactual.strftime("%Y-%m")

    if request.method == "POST":
        mes = request.form["mes"]

        c.execute("SELECT strftime('%d', fec_ven) AS dia, SUM(cobro - pago) AS total FROM ventas WHERE strftime('%Y-%m', fec_ven) = ? GROUP BY strftime('%d', fec_ven) ORDER BY dia;", (mes,))
    else:
        # Si es GET, mostrar todo
        c.execute("SELECT strftime('%d', fec_ven) AS dia, SUM(cobro - pago) AS total FROM ventas WHERE strftime('%Y-%m', fec_ven) = ? GROUP BY strftime('%d', fec_ven) ORDER BY dia;", (mesa,))

    ventas = c.fetchall()
    conn.close()

    dias = [r[0] for r in ventas]
    totales = [r[1] for r in ventas]

    return render_template("reportefechasdias.html", dias=dias, totales=totales)
#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------
#DESDE AQUI SE HACE PARA TRANSPORTE
#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

@app.route("/tregistrosservicios")
def tregistrosservicios():
    if "usuario" not in session or session["usuario"]["rol"] != 5:
        return redirect(url_for('inicio1'))
    

    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("""SELECT cod_ser,des_ser,fec_ser,clientes.nom_cli,servicios.monto 
              FROM servicios,clientes 
              WHERE cond_ser=1 and servicios.cod_cli=clientes.cod_cli ORDER BY cod_ser DESC""")
    datos = c.fetchall()
    conn.close()
    return render_template("tregistros_servicios.html", registros=datos)



@app.route("/tformservicios", methods=["GET", "POST"])
def tformservicios():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE cond_cli = 1")
    registro = c.fetchall()
    conn.close()

    if request.method == "POST":
        form_name = request.form.get("form_name")
        if form_name == "form1":
            descripcion=request.form["descripcion"]
            fecservicio=request.form["fecservicio"]
            cliente = request.form["cliente"]
            monto=request.form["monto"]
            cond_ser=1

            conn = sqlite3.connect("data1.db")
            c = conn.cursor()
            c.execute("INSERT INTO servicios (des_ser, fec_ser, cod_cli, monto, cond_ser) VALUES (?, ?, ?, ?, ?)", (descripcion, fecservicio, cliente, monto, cond_ser))
            conn.commit()
            conn.close()

            return redirect("/tregistrosservicios")  # Redirigir después de guardar
        if form_name == "form2":
            cliente=request.form["cliente"]
            phone=request.form["phone"]
            nomcont = request.form["nomcont"]
            cond_cli=1

            conn = sqlite3.connect("data1.db")
            c = conn.cursor()
            c.execute("INSERT INTO clientes (nom_cli, tel_cli, nom_con, cond_cli) VALUES (?, ?, ?, ?)", (cliente, phone, nomcont, cond_cli))
            conn.commit()
            conn.close()

            return redirect("/tformservicios")  # Redirigir después de guardar
    return render_template("tformulario_servicios.html", registros=registro)

@app.route("/teditarservicios/<int:id>", methods=["GET", "POST"])
def teditarservicios(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        descripcion=request.form["descripcion"]
        fecservicio=request.form["fecservicio"]
        cliente = request.form["cliente"]
        monto=request.form["monto"]
        cond_ser=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("""
            UPDATE servicios
            SET des_ser = ?, fec_ser = ?, cod_cli = ?, monto = ?, cond_ser = ?
            WHERE cod_ser = ?
        """, (descripcion, fecservicio, cliente, monto, cond_ser, id))
        conn.commit()
        conn.close()

        return redirect("/tregistrosservicios")
     # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM servicios WHERE cod_ser = ?", (id,))
    registro = c.fetchone()
    conn.close()

    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE cond_cli = 1")
    clientes = c.fetchall()
    conn.close()

    return render_template("teditarservicios.html", registros=registro, cliente=clientes)

@app.route("/tborrarservicios/<int:id>")
def tborrarservicios(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("UPDATE servicios SET cond_ser = 0 WHERE cod_ser = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/tregistrosservicios")




@app.route("/tregistrosclientes")
def tregistrosclientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("""SELECT * 
              FROM clientes 
              WHERE cond_cli=1 ORDER BY nom_cli""")
    datos = c.fetchall()
    conn.close()
    return render_template("tregistros_clientes.html", registros=datos)

@app.route("/tformclientes", methods=["GET", "POST"])
def tformclientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
   
    if request.method == "POST":
        cliente=request.form["cliente"]
        phone=request.form["phone"]
        nomcont = request.form["nomcont"]
        cond_cli=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("INSERT INTO clientes (nom_cli, tel_cli, nom_con, cond_cli) VALUES (?, ?, ?, ?)", (cliente, phone, nomcont, cond_cli))
        conn.commit()
        conn.close()

        return redirect("/tregistrosclientes")  # Redirigir después de guardar
    return render_template("tformulario_clientes.html")

@app.route("/teditarclientes/<int:id>", methods=["GET", "POST"])
def teditarclientes(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        nombre=request.form["nombre"]
        tel=request.form["tel"]
        nomcont = request.form["nomcont"]
        cond_cli=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("""
            UPDATE clientes
            SET nom_cli = ?, tel_cli = ?, nom_con = ?, cond_cli = ?
            WHERE cod_cli = ?
        """, (nombre, tel, nomcont, cond_cli, id))
        conn.commit()
        conn.close()

        return redirect("/tregistrosclientes")
     # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE cod_cli = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("teditarclientes.html", registros=registro)

@app.route("/tborrarclientes/<int:id>")
def tborrarclientes(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("UPDATE clientes SET cond_cli = 0 WHERE cod_cli = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/tregistrosclientes")




@app.route("/tregistrosgastos")
def tregistrosgastos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT gastos.cod_gas, gastos.des_gas, gastos.fec_gas, cat_gas.nom_cat, gastos.monto FROM gastos, cat_gas where cond_gas=1 and cat_gas.cod_cat=gastos.cod_cat ORDER BY fec_gas DESC, gastos.cod_gas DESC")
    datos = c.fetchall()
    conn.close()
    return render_template("tregistros_gastos.html", registros=datos)

@app.route("/tformgastos", methods=["GET", "POST"])
def tformgastos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()

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

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("INSERT INTO gastos (des_gas, fec_gas, cod_cat, monto, cond_gas) VALUES (?, ?, ?, ?, ?)", (des, fec, cat, mon,  cond))
        conn.commit()
        conn.close()

        return redirect("/tregistrosgastos")  # Redirigir después de guardar
    return render_template("tformulario_gastos.html", categoria=categoria)

@app.route("/teditargastos/<int:id>", methods=["GET", "POST"])
def teditargastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        des=request.form["des"]
        fec=request.form["fec"]
        mon = request.form["mon"]
        cond_gas=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("""
            UPDATE gastos
            SET des_gas = ?, fec_gas = ?, monto = ?, cond_gas = ?
            WHERE cod_gas = ?
        """, (des, fec, mon, cond_gas, id))
        conn.commit()
        conn.close()

        return redirect("/tregistrosgastos")
     # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM gastos WHERE cod_gas = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("teditargastos.html", registros=registro)

@app.route("/tborrargastos/<int:id>")
def tborrargastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("UPDATE gastos SET cond_gas = 0 WHERE cod_gas = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/tregistrosgastos")





@app.route("/tregistrosdeudas")
def tregistrosdeudas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("""SELECT * 
              FROM deudas 
              WHERE cond_deu=1""")
    datos = c.fetchall()
    conn.close()
    return render_template("tregistros_deudas.html", registros=datos)

@app.route("/tformdeudas", methods=["GET", "POST"])
def tformdeudas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
   
    if request.method == "POST":
        des=request.form["des"]
        mon = request.form["mon"]
        fece=request.form["fece"]
        fecp=request.form["fecp"]
        cond_deu=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("INSERT INTO deudas (des_deu, monto, fec_emi, fec_pag, cond_deu) VALUES (?, ?, ?, ?, ?)", (des, mon, fece, fecp, cond_deu))
        conn.commit()
        conn.close()

        return redirect("/tregistrosdeudas")  # Redirigir después de guardar
    return render_template("tformulario_deudas.html")

@app.route("/teditardeudas/<int:id>", methods=["GET", "POST"])
def teditardeudas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        des=request.form["des"]
        mon = request.form["mon"]
        fece=request.form["fece"]
        fecp=request.form["fecp"]
        cond_deu=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("""
            UPDATE deudas
            SET des_deu = ?, monto = ?, fec_emi = ?, fec_pag = ?, cond_deu = ?
            WHERE cod_deu = ?
        """, (des, mon, fece, fecp, cond_deu, id))
        conn.commit()
        conn.close()

        return redirect("/tregistrosdeudas")
     # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM deudas WHERE cod_deu = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("teditardeudas.html", registros=registro)

@app.route("/tborrardeudas/<int:id>")
def tborrardeudas(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("UPDATE deudas SET cond_deu = 0 WHERE cod_deu = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/tregistrosdeudas")





@app.route("/tregistroscobros")
def tregistroscobros():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("""SELECT * 
              FROM cobros 
              WHERE cond_cob=1""")
    datos = c.fetchall()
    conn.close()
    return render_template("tregistros_cobros.html", registros=datos)

@app.route("/tformcobros", methods=["GET", "POST"])
def tformcobros():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
   
    if request.method == "POST":
        des=request.form["des"]
        mon = request.form["mon"]
        fece=request.form["fece"]
        fecp=request.form["fecp"]
        cond_deu=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("INSERT INTO cobros (des_cob, monto, fec_emi, fec_cob, cond_cob) VALUES (?, ?, ?, ?, ?)", (des, mon, fece, fecp, cond_deu))
        conn.commit()
        conn.close()

        return redirect("/tregistroscobros")  # Redirigir después de guardar
    return render_template("tformulario_cobros.html")

@app.route("/teditarcobros/<int:id>", methods=["GET", "POST"])
def teditarcobros(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Procesar actualización
        des=request.form["des"]
        mon = request.form["mon"]
        fece=request.form["fece"]
        fecp=request.form["fecp"]
        cond_cob=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("""
            UPDATE cobros
            SET des_cob = ?, monto = ?, fec_emi = ?, fec_cob = ?, cond_cob = ?
            WHERE cod_cob = ?
        """, (des, mon, fece, fecp, cond_cob, id))
        conn.commit()
        conn.close()

        return redirect("/tregistroscobros")
     # Si es GET, mostrar datos actuales
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cobros WHERE cod_cob = ?", (id,))
    registro = c.fetchone()
    conn.close()

    return render_template("teditarcobros.html", registros=registro)

@app.route("/tborrarcobros/<int:id>")
def tborrarcobros(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("UPDATE cobros SET cond_cob = 0 WHERE cod_cob = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/tregistroscobros")

@app.route("/tcategorias", methods=["GET", "POST"])
def tcategorias():
    if "usuario" not in session :
        return redirect(url_for('inicio1'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cat_gas where cond_cat=1 ORDER BY fec_cat DESC")
    datos = c.fetchall()
    conn.close()

    if request.method == "POST":
        nom = request.form["nom"]
        hoy = date.today()
        fecha_formateada = hoy.strftime("%Y-%m-%d")
        cond=1

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("INSERT INTO cat_gas (nom_cat, fec_cat, cond_cat) VALUES (?, ?, ?)", (nom, fecha_formateada, cond))
        conn.commit()
        conn.close()

        return redirect(url_for("tcategorias"))  # Redirigir después de guardar

    return render_template("tcategorias.html", datos=datos)    

@app.route("/teditarcategoriasgastos/<int:id>", methods=["GET", "POST"])
def teditarcategoriasgastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cat_gas WHERE cod_cat = ?", (id,))
    registro = c.fetchone()
    conn.close()
    if request.method == "POST":
        nom = request.form["nom"]

        conn = sqlite3.connect("data1.db")
        c = conn.cursor()
        c.execute("UPDATE cat_gas SET nom_cat= ? WHERE cod_cat = ?", (nom, id))
        conn.commit()
        conn.close()

        return redirect(url_for("tcategorias"))  # Redirigir después de guardar
    return render_template("teditarcategoriasgastos.html", registro=registro)


@app.route("/tborrarcategoriasgastos/<int:id>")
def tborrarcategoriasgastos(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("UPDATE cat_gas SET cond_cat=0 WHERE cod_cat = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("tcategorias"))

@app.route("/tresumen")
def tresumen():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("select  nom_cat, SUM(monto), gastos.cod_cat from gastos, cat_gas  where gastos.cod_cat = cat_gas.cod_cat and cond_gas=1 and strftime('%Y-%m', fec_gas) = strftime('%Y-%m', 'now') GROUP BY gastos.cod_cat")
    datos = c.fetchall()
    conn.close()
    return render_template("tresumen.html", datos=datos)

@app.route("/datos_tresumen")
def datos_tresumen():
    conn = sqlite3.connect("data1.db")
    c = conn.cursor()
    c.execute("""
        SELECT nom_cat, SUM(monto)
        FROM gastos, cat_gas  
        WHERE gastos.cod_cat = cat_gas.cod_cat 
        AND cond_gas = 1 
        AND strftime('%Y-%m', fec_gas) = strftime('%Y-%m', 'now')
        GROUP BY gastos.cod_cat
    """)
    filas = c.fetchall()
    conn.close()

    # Convertir los datos a formato JSON legible por ECharts
    datos = [{"name": fila[0], "value": fila[1]} for fila in filas]
    return jsonify(datos)

#----------------------------------------------------------------------------------------------------------
#TRABAJANDO CON EL LOGIN
#----------------------------------------------------------------------------------------------------------
@app.route('/ini')
def inicio1():
    if 'usuario' in session:
        return render_template("menuprincipal.html", usuario=session['usuario'])
    
    return redirect(url_for('login'))


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["usuario"]
        password=request.form["clave"]

        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        usuario = c.fetchone()
        conn.close()

        if usuario:
            session['usuario'] = {
            "id": usuario[0],
            "username": usuario[1],
            "rol": usuario[3]
            }
            return redirect("/ini")
        else:
            return "Usuario o contraseña incorrectos"
    
    return render_template("logeado.html")

@app.route('/logout')
def logout():
    session.pop('usuario5', None)
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
