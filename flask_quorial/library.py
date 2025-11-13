import sqlite3

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flask_quorial.auth import login_required
from flask_quorial.db import get_db

#define the blueprint
bp = Blueprint('library', __name__)

@bp.route('/library/search', methods=('GET', 'POST'))
@bp.route('/library', methods=('GET', 'POST'))
@login_required
def search():

    #document the session
    session['history'] = session['history'] + "/library/search\n ... "
    flash(session['history'])

    if request.method == 'POST':
        bookname = request.form['bookname']
        keywords = request.form['keywords']
        keywords_lc = keywords.lower()
        if len(keywords) == 0:
            keywords = None
            keywords_lc = None
        error = None

        if  (not bookname) and (not keywords):
            error = 'input is required.'

        if error is not None:
            flash(error)
            return render_template('library/search.html')
        else:
            db = get_db()
            booklist = db.execute(
                "select titel, Buecher.isbn, Buecher.verlagsname, verlagsort, buch_exemplare.auflage, jahr, seiten, preis, count(*) anzahl"
" from Buecher, verlage, Buch_exemplare, Buch_versionen"
" where Buecher.verlagsname = Verlage.verlagsname and"
" Buecher.isbn = Buch_Versionen.isbn and"
" Buch_versionen.auflage = buch_exemplare.auflage and"
" Buecher.isbn = Buch_Exemplare.isbn and"
" (lower(titel) like ?) "
" and ((? is null) or (? in ( select lower(Stichwort)"
" from Buch_Stichwort where Buch_Stichwort.isbn = Buecher.isbn )))"
" group by titel, Buecher.isbn, Buecher.verlagsname, verlagsort, buch_exemplare.auflage, jahr, seiten, preis"
" order by titel", (bookname.lower()+'%',keywords,keywords_lc,)).fetchall()
# keywords, keywords.lower(),

            print("show booklist", flush=True)
            print (bookname, flush=True)
            for book in booklist:
                print(book['titel'], flush=True)

            return render_template('library/search.html', booklist=booklist)
            #return redirect(url_for('library/search.html'))
    else:
        return render_template('library/search.html')

@bp.route('/library/borrowedbooks', methods=('GET', 'POST'))
@login_required
def borrowedbooks():

    #document the session
    session['history'] = session['history'] + "/library/borrowedbooks\n ... "
    flash(session['history'])

    db = get_db()
    matrnrper = db.execute(
        'SELECT Vorname, Nachname, Matrikelnummer, Studienfach, Immatrikulationsdatum'
        ' FROM Studenten, Personen'
        ' WHERE Personen.PANr = Studenten.PANr and Personen.PANr = ? ', (g.user['username'],)
    ).fetchone()

    #provide functionality ONLY if login id = valid student id
    if matrnrper is None:
        return render_template('guest/guest.html', )

    #borrow a book
    if request.method == 'POST':
        if 'returninv' in request.form:
            returninv = request.form['returninv']


            returnbook = db.execute(
                'DELETE FROM ausleihe WHERE Inventarnr = ? and PANr = ?',
                (returninv,g.user['username'],))
            retval = db.commit()

        elif 'inventorynr' in request.form:
            inventorynr = request.form['inventorynr']

            try:
                #check if book exists in the library
                bookexists = db.execute(
                    "SELECT * FROM Buch_Exemplare"
                    " WHERE inventarnr = ?", (inventorynr,)
                ).fetchone()
                if bookexists:
                    toborrow = db.execute(
                        'INSERT INTO Ausleihe (PANr, Inventarnr)'
                        ' VALUES (?, ?)',
                        (g.user['username'],inventorynr,)
                    )
                    retval = db.commit()
            except (sqlite3.Error) as e:
                flash(e)


    borrowed = db.execute(
        #Remark: " instead of ' because of SQL internal string concatenation
        "SELECT ausleihe.inventarnr Inventarnummer, Buecher.titel Titel, Buecher.verlagsname Verlagsname"
		" FROM ausleihe, Buch_exemplare, Buecher"
		" WHERE Buecher.isbn = Buch_Exemplare.isbn and Ausleihe.inventarnr = Buch_Exemplare.inventarnr"
		" and ausleihe.inventarnr in (select ausleihe.Inventarnr from ausleihe"
		" where ausleihe.panr = ?)",
        (g.user['username'],)
    ).fetchall()

    return render_template('library/borrowedbooks.html',  borrowed=borrowed,)

