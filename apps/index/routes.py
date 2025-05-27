# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.index import blueprint
from flask import render_template, request,redirect,url_for
from flask_login import login_required
from jinja2 import TemplateNotFound


@blueprint.route('/')
def index():

    return render_template('index/index.html',segment='index')
