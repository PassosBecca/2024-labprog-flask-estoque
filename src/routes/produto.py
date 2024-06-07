from base64 import b64encode

from flask import Blueprint, flash, redirect, url_for, render_template, request, abort, Response
from flask_login import login_required

from src.forms.produto import ProdutoForm
from src.models.categoria import Categoria
from src.models.produto import Produto
from src.modules import db

bp = Blueprint('produto', __name__, url_prefix='/produto')


@bp.route('/add', methods=['GET','POST'])
@login_required
def add():
    if Categoria.is_empty():
        flash("Impossível adicionar produto. Adicione pelo menos uma categoria",
              category='warning')
        return redirect(url_for('categoria.add'))

    form = ProdutoForm()
    form.submit.label.text="Adicionar produto"
    categorias = db.session.execute(db.select(Categoria).order_by(Categoria.nome)).scalars()
    form.categoria.choices = [(str(i.id), i.nome) for i in categorias]
    if form.validate_on_submit():
        produto = Produto(nome=form.nome.data,
                          preco = form.preco.data,
                          ativo = form.ativo.data,
                          estoque = form.estoque.data)
        if form.foto.data:
            produto.possui_foto = True
            produto.foto_base64 = (b64encode(request.files[form.foto.name].read()).
                                   decode('ascii'))
            produto.foto_mime = request.files[form.foto.name].mimetype
        else:
            produto.possui_foto = False
            produto.foto_base64 = None
            produto.foto_mime = None
        categoria = Categoria.get_by_id(form.categoria.data)
        if categoria is None:
            flash("Categoria inxeistente !", category='danger')
            return redirect(url_for('produto.add'))
        produto.categoria = categoria
        db.session.add(produto)
        db.session.commit()
        flash("Produto adicionado com sucesso!")
        return redirect(url_for('index'))

    return render_template('produto/add_edit.jinja2', form=form,
                           title='Adicionar novo produto')

@bp.route('/lista', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
def lista():
    sentenca = db.select(Produto).order_by(Produto.nome)
    rset = db.session.execute(sentenca).scalars()

    return render_template('produto/lista.jinja2',
                           title='Lista de produtos',
                           rset=rset)

@bp.route('/imagem/<uuid:id_produto>', methods=['GET'])
def imagem(id_produto):
    produto = Produto.get_by_id(id_produto)
    if produto is None:
        return abort(404)
    conteudo, tipo = produto.imagem
    return Response(conteudo, mimetype=tipo)

@bp.route('/thumbnail/<uuid:id_produto>/<int:size>', methods=['GET'])
@bp.route('/thumbnail/<uuid:id_produto>', methods=['GET'])
def thumbnail(id_produto, size=128):
    produto = Produto.get_by_id(id_produto)
    if produto is None:
        return abort(404)
    conteudo, tipo = produto.thumbnail(size)
    return Response(conteudo, mimetype=tipo)