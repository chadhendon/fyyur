#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]

  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  for city in cities:
      venuesCity = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(Venue.state == city[1])
      data.append({
        "city": city[0],
        "state": city[1],
        "venues": venuesCity
      })

  return render_template('pages/venues.html', areas=data);

# Search Venues
#-----------------------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
    data = []

    for venue in venues:
        num_upcoming_shows = 0
        shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id)
        for show in shows:
            if (show.start_time > datetime.now()):
                num_upcoming_shows += 1;

        data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
        })

    response={
        "count": len(venues),
        "data": data
     }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Show Venue
#-----------------------------------------------------------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
    if not venue:
        return render_template('errors/404.html')

    listShows = db.session.query(Show).filter(Show.venue_id == venue_id)
    upcoming_shows = []
    past_shows = []

    for show in listShows:
      artist = db.session.query(Show).join(artist_id).filter(Artist.id == show.artist_id).one()
      show_add = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
          }
      if (show.start_time < datetime.now()):
          past_shows.append(show_add)

      else:
          upcoming_shows.append(show_add)

          data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
            }
          return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        #genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        #website = form.website.data,
        #seeking_talent = form.seeking_talent.data,
        #seeking_description = form.seeking_description.data
    )
    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        # on unsuccessful db insert, flash an error instead
        flash('An error occurred. Venue ' + form.name.data+ ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

# Edit Venue
# --------------------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

    updatedVenue = {
        name: form.name.data,
        city: form.city.data,
        stat: form.state.data,
        address: form.address.data,
        phone: form.phone.data,
        genres: form.genres.data,
        image_link: form.image_link.data,
        facebook_link: form.facebook_link.data,
        website: form.website.data,
        seeking_talent: form.seeking_talent.data,
        seeking_description: form.seeking_description.data
    }
    try:
        db.session.query(Venue).filter(Venue.id == venue_id).update(updatedVenue)
        db.session.commit()
        flash('Venue' + form.name.data + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

# Delete Venue
#----------------------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        db.session.query(Venue).filter(Venue.id == venue_id).delete()
        db.session.commit()
        flash('Venue was successfully deleted!')
    except:
        flash('An error occurred. Venue could not be deleted.')
    finally:
        db.session.close()
    return redirect(render_template('pages/home.html'))

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    artist = Artist.query.order_by(Artist.id, Artist.name).all()

    return render_template('pages/artists.html', artists=artist)

# Search Artist
#---------------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
    data = []

    for artist in artists:
        num_upcoming_shows = 0
        shows = db.session.query(Show).filter(Show.artist_id == artist.id)
        for show in shows:
            if(show.start_time > datetime.now()):
                num_upcoming_shows += 1;
        data.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming_shows
        })
    response={
        "count": len(artists),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


# Show Artist
#--------------------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_query = db.session.query(Artist).filter(Artist.id == artist_id).one()

    if not artist_query:
        return render_template('errors/404.html')

    upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist_id)
    upcoming_shows = []
    past_shows = []

    for show in upcoming_shows:
        artist = db.session.query(Artist.name).filter(Artist.id == show.artist_id).one()
        show_add = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        if (show.start_time < datetime.now()):
            past_shows.append(show_add)
        else:
            upcoming_shows.append(show_add)
            data = {
                    "id": artist.id,
                    "name": artist.name,
                    "genres": artist.genres,
                    "city": artist.city,
                    "state": artist.state,
                    "phone": artist.phone,
                    "website": artist.website,
                    "facebook_link": artist.facebook_link,
                    "seeking_venue": artist.seeking_venue,
                    "seeking_description": artist.seeking_description,
                    "image_link": artist.image_link,
                    "past_shows": past_shows,
                    "upcoming_shows": upcoming_shows,
                    "past_shows_count": len(past_shows),
                    "upcoming_shows_count": len(upcoming_shows),
                }
        return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

    updatedArtist = {
        name: form.name.data,
        city: form.city.data,
        state: form.state.data,
        phone: form.phone.data,
        genres: form.genres.data,
        facebook_link: form.facebook_link.data,
        image_link: form.image_link.data,
        website: form.website.data,
        seeking_venue: form.seeking_venue.data,
        seeking_description: form.seeking_description.data,
    }

    try:
        db.session.query(Artist).filter(Artist.id == artist_id).updated(updatedArtist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + form.name.data + ' was successfully listed!')

    except:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


 # DELETE Artist
 # ----------------------------------------------------------------------------
@app.route('/artist/<artist_id>', methods=['DELETE'])
def deleteArtist(artist_id):
    try:
        db.session.query(Artist).filter(Artist.id == artist_id).delete()
        db.session.commit()
        flash('Artist was deleted successful!')

    except:
        flash('An error occurred. Artist could not be deleted.')

    finally:
        db.session.close()

    return redirect(ur_for('artist'))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        #website = form.website.data,
        #seeking_venue = form.seeking_venue.data,
        #seeking_description = form.seeking_description.data,
    )

    try:
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + form.name.data + ' was successfully listed!')

    except:
        db.session.rollback()
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()

    for show in shows:
        data.append({
                "venue_id": show.venue_id,
                "artist_id": show.artist_id,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })

        return render_template('pages/shows.html', shows=data)


# Create shows
#----------------------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    show = Show(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data,
    )

    try:
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        # on unsuccessful db insert, flash an error instead
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
