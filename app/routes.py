from flask import Blueprint, Flask, request, jsonify, render_template
from .convert import run_convert

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    oracle_code = data.get("oracle_code", "")
    postgres_code = run_convert(oracle_code)
    return jsonify({"postgres_code": postgres_code})
