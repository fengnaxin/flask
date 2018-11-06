from . import news_blue
from flask import render_template


@news_blue.route("/<int:news_id>")
def new(news_id):
    return render_template("news/detail.html")
