# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from apps import mongo, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from apps.authentication.util import verify_pass


# @blueprint.route('/')
# def route_default():
#     return redirect(url_for('authentication_blueprint.login'))


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    
    if 'login' in request.form:
        # Leer datos del formulario
        username = request.form['username']
        password = request.form['password']

        # Buscar usuario en MongoDB
        user = Users.find_by_username(username)

        # Si no se encuentra el usuario
        if not user:
            return render_template('accounts/login.html',
                                   msg='Unknown User',
                                   form=login_form)

        # Verificar contraseña
        if verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('authentication_blueprint.login'))

        return render_template('accounts/login.html',
                               msg='Wrong username or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html', form=login_form)

    return redirect(url_for('clients_blueprint.list_clients'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)

    if 'register' in request.form:
        username = request.form['username']

        # Verificar si el usuario ya existe
        if Users.find_by_username(username):
            return render_template('accounts/register.html',
                                   msg='Nombre de usuario ya registrado',
                                   success=False,
                                   form=create_account_form)

        # Crear usuario y guardarlo en MongoDB
        user = Users(username=username, password=request.form['password'])
        user.save()

        # Cerrar sesión por seguridad
        logout_user()

        return render_template('accounts/register.html',
                               msg='Usuario creado con éxito.',
                               success=True,
                               form=create_account_form)

    return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Manejo de errores

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
