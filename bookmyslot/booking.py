from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from werkzeug.exceptions import abort
from bookmyslot.auth import login_required
from bookmyslot.db import get_db
from datetime import datetime
from datetime import timedelta

bp = Blueprint('booking', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()

    slots = db.execute('SELECT * FROM slot ORDER BY time').fetchall()
    # slots=[]
    # try:
    #     pass
    # except Exception as e:
    #     flash(str(e))

    return render_template('booking/index.html', slots=slots)


@bp.route('/generate_slot', methods=('GET', 'POST'))
@login_required
def generate_slot():
    if request.method == 'POST':
        proctor = request.form.get('proctor')
        student = request.form.get('student')
        time = request.form['time']
        from_date = datetime.strptime(request.form['from_date'] + ' ' + time,
                                      '%Y-%m-%d %H:%M')
        to_date = datetime.strptime(request.form['to_date'] + ' ' + time,
                                    '%Y-%m-%d %H:%M')
        duration = to_date - from_date
        dates = [
            from_date + timedelta(days=x) for x in range(duration.days + 1)
        ]

        try:
            db = get_db()
            for dt in dates:
                db.execute(
                    'INSERT INTO slot (proctor, student, time) VALUES (?, ?, ?)',
                    (
                        proctor,
                        student,
                        dt,
                    ))
            db.commit()
            flash(
                f'Slot booked from {from_date} to {to_date} with {"Unalloted proctor" if proctor == "" else proctor} and {"Unalloted student" if student == "" else student}'
            )
        except Exception as e:
            flash(e)
    return render_template('booking/generate_slot.html')


@bp.route('/show_slots', methods=('GET', 'POST'))
@login_required
def show_slots():
    db = get_db()
    if request.method == 'POST':
        response = request.form
        for slot in response:
            db.execute('UPDATE slot SET proctor = ? WHERE time = ?', (
                g.user['id'],
                slot,
            ))
            flash(slot)
        db.commit()

    slots = db.execute('SELECT * FROM slot ORDER BY time')
    slots_by_date = {}
    for slot in slots:
        strdate = str(slot['time'].date())
        if strdate not in slots_by_date:
            slots_by_date[strdate] = []
        slots_by_date[strdate].append(slot)
    return render_template('booking/show_slots.html',
                           slots=slots,
                           slots_by_date=slots_by_date)
