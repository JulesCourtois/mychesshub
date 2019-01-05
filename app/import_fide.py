import os
import urllib.request
import zipfile
from app import db
from app.models import Federation, Ranking


def import_fide(anonymous_user):
    temp_txt = "standard_rating_list.txt"
    url = "http://ratings.fide.com/download/standard_rating_list.zip"

    downloaded_zip, headers = urllib.request.urlretrieve(url)

    fide = db.session.query(Federation).filter(Federation.initials == "FID").one_or_none()
    if fide is None:
        fide = Federation(name="World Chess Federation", initials="FID")
        db.session.add(fide)
        db.session.commit()
        fide = db.session.query(Federation).filter(Federation.initials == "FID").one_or_none()

    with zipfile.ZipFile(downloaded_zip, 'r') as zip_ref:
        zip_ref.extractall()

    file = open(temp_txt)
    content = file.readlines()[1:]  # ignore first line (column names)

    rankings = []
    for line in content:
        player_id = line[0:9].strip()
        elo = int(line[113:117].strip())
        # name = line[15:75].strip()
        # federation_initials = line[76:79]
        # birth = int(line[126:130])
        ranking = db.session.query(Ranking)\
            .filter(Ranking.federation == fide.id)\
            .filter(Ranking.player_id == player_id)\
            .first()
        if ranking is None:
            ranking = Ranking(user_id=anonymous_user.id, federation=fide.id, player_id=player_id)
        ranking.elo = elo
        rankings.append(ranking)
    db.session.add_all(rankings)
    db.session.commit()

    file.close()
    os.remove(temp_txt)
    os.remove(downloaded_zip)
