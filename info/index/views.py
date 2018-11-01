
import logging
from . import index_blu, favicon_blu
from flask import render_template, current_app, Blueprint


@index_blu.route("/")
def index():
    logging.debug("This is a debug log.")
    logging.info("This is a info log.")
    logging.warning("This is a warning log.")
    logging.error("This is a error log.")
    logging.critical("This is a critical log.")
    return render_template("news/index.html")


"""
    如果不用装饰器的话可以用这下面这句，直接调
    index_blu.add_url_rule("/", "index", index)
"""


def favicon():
    return current_app.send_static_file("news/favicon.icon")


favicon_blu.add_url_rule("/favicon.icon", "favicon", favicon)
