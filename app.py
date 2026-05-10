from flask import Flask, render_template, request, abort
import json
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / 'data' / 'one_piece.json'



def formatear_recompensa(valor):
    if valor is None or valor == "":
        return "Desconocida"

    if isinstance(valor, (int, float)):
        return f"{int(valor):,}".replace(",", ".")

    texto = str(valor).strip()

    if texto.isdigit():
        return f"{int(texto):,}".replace(",", ".")

    return texto


def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    personajes = data.get('personajes', [])

    for p in personajes:
        p['recompensa_formateada'] = formatear_recompensa(p.get('recompensa'))

        fruta = p.get('fruta_del_diablo')

        if isinstance(fruta, dict):
            p['tipo_fruta'] = fruta.get('tipo', 'Desconocida')
            p['nombre_fruta'] = fruta.get('nombre', 'Desconocida')
        elif isinstance(fruta, str) and fruta.strip():
            p['tipo_fruta'] = 'Desconocida'
            p['nombre_fruta'] = fruta.strip()
        else:
            p['tipo_fruta'] = 'Sin fruta'
            p['nombre_fruta'] = 'No tiene'

    return data, personajes


def get_roles(personajes):
    return sorted({p.get('rol', 'Desconocido') for p in personajes if p.get('rol')})


@app.route('/')
def index():
    data, personajes = load_data()
    destacados = personajes[:3]
    return render_template('index.html', universo=data, destacados=destacados)


@app.route('/personajes')
def personajes():
    data, personajes = load_data()

    nombre = request.args.get('nombre', '').strip()
    rol = request.args.get('rol', '').strip()
    orden = request.args.get('orden', 'asc').strip().lower()

    filtrados = personajes

    if nombre:
        texto = nombre.lower()
        filtrados = [p for p in filtrados if texto in p.get('nombre', '').lower()]

    if rol:
        filtrados = [p for p in filtrados if p.get('rol', '') == rol]

    reverse = orden == 'desc'
    filtrados = sorted(
        filtrados,
        key=lambda p: p.get('nombre', '').lower(),
        reverse=reverse
    )

    return render_template(
        'items.html',
        universo=data,
        personajes=filtrados,
        roles=get_roles(personajes),
        nombre=nombre,
        rol=rol,
        orden=orden
    )


@app.route('/personaje/<int:item_id>')
def detalle_personaje(item_id):
    data, personajes = load_data()
    personaje = next((p for p in personajes if p.get('id') == item_id), None)

    if personaje is None:
        abort(404)

    return render_template(
        'detail.html',
        universo=data,
        personaje=personaje
    )


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)

