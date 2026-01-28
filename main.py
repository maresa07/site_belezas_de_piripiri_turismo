from flask import Flask, render_template, abort, jsonify, url_for, session, request, json, redirect

from firebase import db
from upload_to_firestore import upload_to_firestore

app = Flask(__name__, template_folder="src/templates", static_folder="src/static")

from flask_mail import Mail, Message

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "belezaspiripiri@gmail.com"
app.config["MAIL_PASSWORD"] = "opgy sfmj xjgx xkap"  # não é a senha normal
app.config["MAIL_DEFAULT_SENDER"] = "belezaspiripiri@gmail.com"

mail = Mail(app)


app.secret_key = "qualquer-coisa-aqui"

db = db()

# ===================== DADOS =====================
def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def lerColecao(nome_colecao):
   
   
    ref = db.collection(nome_colecao)
    docs = ref.stream()

    u = []
    for doc in docs:
        print("documento firestore", doc)
        item = doc.to_dict()
        item['id'] = doc.id
        u.append(item)

    return u


def gerar_proximo_loc_id():
    docs = db.collection("locations").stream()

    maior = 0

    for doc in docs:
        doc_id = doc.id
        if doc_id.startswith("loc_"):
            try:
                numero = int(doc_id.split("_")[1])
                if numero > maior:
                    maior = numero
            except:
                pass

    return f"loc_{maior + 1}"


# ===================== ROTAS =====================

@app.route("/export-data")
def export_data():
    return upload_to_firestore()

import random

@app.route("/")
def index():
    docs = db.collection("locations").stream()

    lugares = []
    for doc in docs:
        lugar = doc.to_dict()
        lugar["id"] = doc.id
        lugares.append(lugar)

    print(lugares)  # 👈 DEBUG (IMPORTANTE)

    lugares_sorteados = random.sample(
        lugares,
        min(len(lugares), 8)
    )

    return render_template(
        "index.html",
        lugares=lugares_sorteados
    )


@app.route("/categoria/<nome>")
def categoria(nome):

    docs = db.collection("locations") \
        .where("category_slug", "==", nome) \
        .stream()

    lugares = []
    for doc in docs:
        lugar = doc.to_dict()
        lugar["id"] = doc.id
        lugares.append(lugar)

    return render_template(
        "lista_lugares.html",
        categoria=nome,
        lugares=lugares
    )




@app.route("/lugar/<id>")
def lugar(id):
    doc = db.collection("locations").document(id).get()

    if not doc.exists:
        abort(404)

    lugar = doc.to_dict()
    lugar["id"] = doc.id

    return render_template("detalhes.html", lugar=lugar)

@app.route("/buscar")
def buscar():
    termo = request.args.get("q")

    if not termo:
        return redirect(url_for("index"))

    termo = termo.lower()

    docs = db.collection("locations").stream()

    resultados = []

    for doc in docs:
        lugar = doc.to_dict()
        lugar["id"] = doc.id

        nome = lugar.get("nome", "").lower()
        descricao = lugar.get("descricao_curta", "").lower()

        if termo in nome or termo in descricao:
            resultados.append(lugar)

    return render_template(
        "lista_lugares.html",
        categoria=f'Resultados para "{termo}"',
        lugares=resultados
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        email = request.form["email"]

        usuarios = lerColecao("users")
        admin_encontrado = False

        for users in usuarios:
            if users["name"] == usuario and users["password"] == senha and users["email"] == email:
                session["admin"] = True
                admin_encontrado = True
                return redirect(url_for("admin"))

        if not admin_encontrado:
            erro = "Acesso negado. Apenas administrador."

    return render_template("login.html", erro=erro)

@app.route("/contato", methods=["GET", "POST"])
def contato():
    sucesso = False
    erro = None

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        mensagem = request.form.get("mensagem")

        try:
            # 🔹 pega TODOS os emails da coleção users
            admins = db.collection("users").stream()
            emails_admins = []

            for admin in admins:
                dados = admin.to_dict()
                if "email" in dados:
                    emails_admins.append(dados["email"])

            if not emails_admins:
                raise Exception("Nenhum email encontrado")

            # 🔹 monta o email
            msg = Message(
                subject="Nova mensagem de contato - Belezas de Piripiri",
                recipients=emails_admins,
                body=f"""
Nova mensagem enviada pelo site:

Nome: {nome}
Email: {email}

Mensagem:
{mensagem}
"""
            )

            mail.send(msg)
            sucesso = True

        except Exception as e:
            print("ERRO EMAIL:", e)
            erro = "Erro ao enviar a mensagem. Tente novamente."

    return render_template(
        "contato.html",
        sucesso=sucesso,
        erro=erro
    )

@app.route("/admin")
def admin():
    if not session.get("admin"):
        abort(403)
    return render_template("admin/dashboard.html")

@app.route("/admin/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if not session.get("admin"):
        abort(403)

    if request.method == "POST":
        novo_id = gerar_proximo_loc_id()

        # dados vindos do formulário
        nome = request.form["nome"]
        category_slug = request.form["category_ref"]  # ex: pizzaria
        descricao_curta = request.form["descricao_curta"]
        descricao_longa = request.form["descricao_longa"]
        endereco = request.form["endereco"]
        telefone = request.form.get("telefone")
        imagem = request.form.get("imagem")

        # 🔗 referências do Firestore
        category_ref = db.document(f"cat_locations/{category_slug}")

        # se você NÃO tiver sistema de usuário logado com id,
        # pode fixar um admin padrão:
        user_ref = db.document("users/user_1")

        dados = {
            "nome": nome,
            "category_slug": category_slug,
            "category_ref": category_ref,

            "descricao_curta": descricao_curta,
            "descricao_longa": descricao_longa,
            "endereco": endereco,
            "telefone": telefone,
            "imagem": imagem,

            # campos que não vêm do formulário
            "avaliacoes": "Sem avaliações",
            "opcoes_servico": "",
            "user_ref": user_ref
        }

        # cria documento com ID sequencial
        db.collection("locations").document(novo_id).set(dados)

        return render_template(
            "admin/sucesso.html",
            dados=dados,
            doc_id=novo_id
        )

    return render_template("admin/cadastrar.html")


@app.route("/admin/locais")
def locais():
    if not session.get("admin"):
        abort(403)

    busca = request.args.get("busca", "").lower()
    categoria = request.args.get("categoria", "")

    docs = db.collection("locations").stream()

    locais = []

    for doc in docs:
        local = doc.to_dict()
        local["id"] = doc.id

        nome = local.get("nome", "").lower()
        cat = local.get("category_slug", "")

        if busca and busca not in nome:
            continue

        if categoria and categoria != cat:
            continue

        locais.append(local)

    return render_template(
        "admin/locais.html",
        locais=locais
    )


@app.route("/admin/local/<id>")
def detalhar_local_admin(id):
    if not session.get("admin"):
        abort(403)

    doc = db.collection("locations").document(id).get()

    if not doc.exists:
        abort(404)

    local = doc.to_dict()
    local["id"] = doc.id

    return render_template("admin/detalhar.html", local=local)

@app.route("/admin/editar/<id>", methods=["GET", "POST"])
def editar_local(id):
    if not session.get("admin"):
        abort(403)

    ref = db.collection("locations").document(id)
    doc = ref.get()

    if not doc.exists:
        abort(404)

    if request.method == "POST":
        ref.update({
            "nome": request.form["nome"],
            "category_slug": request.form["category_slug"],
            "descricao_curta": request.form["descricao_curta"],
            "descricao_longa": request.form["descricao_longa"],
            "endereco": request.form["endereco"],
            "telefone": request.form["telefone"],
            "imagem": request.form["imagem"]
        })

        return redirect(url_for("detalhar_local_admin", id=id))

    local = doc.to_dict()
    local["id"] = doc.id

    return render_template("admin/editar.html", local=local)

@app.route("/admin/excluir/<id>", methods=["POST"])
def excluir_local(id):
    if not session.get("admin"):
        abort(403)

    db.collection("locations").document(id).delete()
    return redirect(url_for("locais"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)