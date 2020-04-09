from app import db


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    art_shows = db.Column(db.Integer, db.ForeignKey('artist.id'))


    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))
    upcoming_shows_count = db.Column(db.Integer, default = 0)
    past_shows_count = db.Column(db.Integer, default = 0)
    art_shows = db.Column(db.Integer, db.ForeignKey('venue.id'))


    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows', cascade="all,delete"))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade="all,delete"))
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return 'f<Venue {self.start_time}>'

db.create_all()
