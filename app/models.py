from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Federation(db.Model):
    __tablename__ = "federation"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    initials = db.Column(db.String(8), index=True)
    tournaments = db.relationship("Tournament")
    rankings = db.relationship("Ranking")


class Registration(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournament.id"), primary_key=True)
    status = db.Column(db.String(64))

    def tournament(self):
        return Tournament.query.get(self.tournament_id)

    def federation_initials(self):
        tournament = Tournament.query.get(self.tournament_id)
        return Federation.query.get(tournament.federation).initials

    def formatted_date(self):
        return str(self.tournament().start_date)


class Ranking(db.Model):
    __tablename__ = "ranking"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    federation = db.Column(db.Integer, db.ForeignKey('federation.id'), index=True)
    player_id = db.Column(db.String, index=True)
    elo = db.Column(db.Integer)

    def federation_initials(self):
        return Federation.query.get(self.federation).initials


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    birth = db.Column(db.Integer, index=True, default=0)
    rankings = db.relationship("Ranking")
    registrations = db.relationship("Registration")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def birth_repr(self):
        return str(self.birth)

    def get_registration_status(self, tournament_id):
        registration = Registration.query\
            .filter(Registration.user_id == self.id)\
            .filter(Registration.tournament_id == tournament_id)\
            .one_or_none()
        if registration is None:
            return ""
        return registration.status

    def get_all_federations(self):
        federations = []
        for ranking in self.rankings:
            federations.append(ranking.federation)
        return federations

    def get_fide_info(self):
        for ranking in self.rankings:
            if ranking.federation_initials() == "FID":
                return ranking.player_id, str(ranking.elo)
        return "", ""

    def get_federation_info(self, initials):
        for ranking in self.rankings:
            if ranking.federation_initials() == initials:
                return initials, ranking.player_id, str(ranking.elo)
        return "", "", ""

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Tournament(db.Model):
    __tablename__ = "tournament"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    place = db.Column(db.String(64))
    federation = db.Column(db.Integer, db.ForeignKey("federation.id"))

    start_date = db.Column(db.String())
    end_date = db.Column(db.String())
    rounds = db.Column(db.Integer())
    play_system = db.Column(db.String(64))

    move_rate = db.Column(db.String(128))
    chief_arbiter = db.Column(db.String(128))
    deputy_arbiter = db.Column(db.String(256))

    organizer = db.Column(db.Integer, db.ForeignKey("user.id"))
    categories = db.Column(db.String(128))
    information = db.Column(db.String(1024))

    participants = db.relationship("Registration")

    def federation_initials(self):
        return Federation.query.get(self.federation).initials
