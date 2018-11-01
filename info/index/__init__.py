from flask import Blueprint
index_blu = Blueprint("index",__name__)
favicon_blu = Blueprint("favicon",__name__)

from . import views