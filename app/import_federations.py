from app import db
from app.models import User
from app.import_fide import import_fide


def import_federations():
    anonymous_user = User.query.get(0)
    if anonymous_user is None:
        anonymous_user = User(id=0, name="Anonymous", email="anon", birth=0000)
        anonymous_user.set_password("anon")
        db.session.add(anonymous_user)
        db.session.commit()

    import_fide(anonymous_user)
