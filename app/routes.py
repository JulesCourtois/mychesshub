from flask import Response, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from io import StringIO
import csv
from app import app, db
from app.forms import CreateTournamentForm, LoginForm, RegisterForm
from app.models import Federation, Ranking, Registration, User, Tournament


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user is None:
            name = form.full_name.data
            email = form.email.data
            birth = form.birth.data
            password = form.password.data
            user = User(name=name, email=email, birth=birth)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('profile')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/index')
@app.route('/')
@login_required
def example():
    return render_template('template.html', title='ChessHub')


@app.route('/profile')
@login_required
def profile():
    federations = Federation.query.all()
    return render_template('profile.html', title='Profile', federations=federations)


@app.route('/my_tournaments')
@login_required
def my_tournaments():
    return render_template('my_tournaments.html', title="My Tournaments")


@app.route('/tournaments')
@login_required
def tournaments():
    all_tournaments = db.session.query(Tournament).all()
    return render_template('tournaments.html', title="Tournaments", tournaments=all_tournaments)


@app.route('/add_player', methods=['POST'])
@login_required
def add_player():
    federation = request.form["federation"]
    number = request.form["number"]
    print(federation + "  " + number)
    ranking = Ranking.query.filter_by(player_id=number, federation=federation).first()
    if ranking is not None:
        ranking.user_id = current_user.id
        db.session.add(ranking)
        db.session.commit()
    return redirect(url_for('profile'))


@app.route('/create_tournament', methods=['GET', 'POST'])
@login_required
def create_tournament():
    form = CreateTournamentForm()
    if form.validate_on_submit():
        tournament = Tournament(
            name=form.name.data,
            place=form.name.data,
            federation=form.federation.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            rounds=form.rounds.data,
            play_system=form.play_system.data,
            move_rate=form.move_rate.data,
            chief_arbiter=form.chief_arbiter.data,
            deputy_arbiter=form.deputy_arbiter.data,
            organizer=current_user.id,
            categories=form.categories.data,
            information=form.information.data
        )
        db.session.add(tournament)
        db.session.commit()
        redirect(url_for('tournaments'))
    return render_template('create_tournament.html', title='Create Tournament', form=form)


@app.route('/join_tournament', methods=['POST'])
@login_required
def join_tournament():
    tournament_id = request.form["join"]
    registration = Registration(user_id=current_user.id,
                                tournament_id=tournament_id,
                                status="Ok"
                                )
    db.session.add(registration)
    db.session.commit()
    return redirect(url_for('my_tournaments'))


@app.route('/export', methods=['POST'])
@login_required
def export():
    tournament_id = request.form["export"]
    tournament = Tournament.query.get(tournament_id)

    metadata = "name,place,fede,start,end,rounds,system,move_rate,chief,deputy,categories\n"
    metadata_contents = [
        tournament.name,
        tournament.place,
        tournament.federation_initials(),
        tournament.start_date,
        tournament.end_date,
        str(tournament.rounds),
        tournament.play_system,
        tournament.move_rate,
        tournament.chief_arbiter,
        tournament.deputy_arbiter,
        tournament.categories
    ]
    stringio = StringIO()
    writer = csv.writer(stringio)
    writer.writerow(metadata_contents)
    metadata_contents = stringio.getvalue()
    metadata += metadata_contents
    metadata += "name,birth,fide_num,fide_rating,fede,fede_num,fede_rating"

    lines = [metadata]
    for registration in tournament.participants:
        participant = User.query.get(registration.user_id)
        fide_num, fide_rating = participant.get_fide_info()
        federation, federation_num, federation_rating = participant.get_federation_info(tournament.federation_initials())
        line_contents = [
            participant.name,
            str(participant.birth),
            fide_num,
            fide_rating,
            federation,
            federation_num,
            federation_rating
        ]
        stringio = StringIO()
        writer = csv.writer(stringio)
        writer.writerow(line_contents)
        line = stringio.getvalue()
        lines.append(line)

    content = "\n".join(lines)

    content_disposition = "attachment;filename=" + str(tournament_id) + ".csv"
    return Response(content,
                    mimetype="text/plain",
                    headers={"Content-Disposition": content_disposition})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
