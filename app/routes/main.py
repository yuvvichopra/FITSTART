from flask import Blueprint, render_template
from app.services.research_data import get_all_sources

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/research')
def research():
    sources = get_all_sources()
    return render_template('main/research.html', sources=sources)

@main_bp.route('/about')
def about():
    return render_template('main/about.html')
