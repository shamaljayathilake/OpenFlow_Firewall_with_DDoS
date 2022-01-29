from flask import Blueprint,request,render_template, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import requests
from requests.auth import HTTPBasicAuth

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/scj-page', methods=['GET', 'POST'])
@login_required
def scjPage():
    return render_template("scj_page.html", user=current_user)

@views.route('/post-page', methods=['GET', 'POST'])
@login_required
def postPage():
    return render_template("post_page.html", user=current_user)
