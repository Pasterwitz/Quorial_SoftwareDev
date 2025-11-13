from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flask_quorial.auth import login_required
from flask_quorial.db import get_db

#define the blueprint
bp = Blueprint('exams', __name__)

@bp.route('/exams')
@login_required
def exams():

    #document the session
    session['history'] = session['history'] + "/exams\n ... "
    flash(session['history'])

    db = get_db()
    matrnrper = db.execute(
            'SELECT Vorname, Nachname, Matrikelnummer, Studienfach, Immatrikulationsdatum'
            ' FROM Studenten, Personen'
            ' WHERE Personen.PANr = Studenten.PANr and Personen.PANr = ? ', (g.user['username'],)
    ).fetchone()

    #DEBUG: print(matrnrper, flush=True)
    examlist = None
    if matrnrper is not None:
        examlist = db.execute(
            #Remark: " instead of ' because of SQL internal string concatenation
            "SELECT (pe.vorname||' '||pe.nachname) Pruefer, v.V_Bezeichnung Vorlesung, Note, SWS ECTS"
            " FROM Prueft pr, Personen pe, Vorlesungen v"
            " WHERE pr.PAnr=pe.PAnr and pr.V_Bezeichnung=v.V_Bezeichnung"
            " and pr.Matrikelnummer = ?", (matrnrper['Matrikelnummer'],)
        ).fetchall()
    else:
        return render_template('guest/guest.html',)
    return render_template('exams/exams.html', matrnrper=matrnrper, examlist=examlist)
