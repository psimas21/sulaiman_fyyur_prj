#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(120), default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(120), default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable=False)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # venue_qry = Venue.query.all()
  venue_qry = db.session.query(Venue).order_by(Venue.id.desc()).limit(10)

  _venues = []
  for row in venue_qry:
    _venues += [{
    "city": row.city,
    "state": row.state,
    "venues": [{
      "id": row.id,
      "name": row.name,
      "num_upcoming_shows": len(row.shows),
      }]
    }]

  return render_template('pages/venues.html', areas=_venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  venue_search_qry = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%')).all()

  search_venue = {
    "count": 0,
    "data":[]
  }

  search_venue["count"] = len(venue_search_qry)
  for data in venue_search_qry:
    search_venue["data"] += [{
      "id": data.id,
      "name": data.name,
      "num_upcoming_shows": len(data.shows),
      }]

  return render_template('pages/search_venues.html', results=search_venue, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_qry = Venue.query.get(venue_id)

  past_shows = []
  upcoming_shows = []

  for data in venue_qry.shows:
    if data.start_time <= datetime.now():
      past_shows.append({
      "artist_id": data.artist.id,
      "artist_name": data.artist.name,
      "artist_image_link": data.artist.image_link,
      "start_time": data.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    })

    else:
      upcoming_shows.append({
      "artist_id": data.artist.id,
      "artist_name": data.artist.name,
      "artist_image_link": data.artist.image_link,
      "start_time": data.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    })

  venue_data = {
    "id": venue_qry.id,
    "name": venue_qry.name,
    "genres": venue_qry.genres,
    "address": venue_qry.address,
    "city": venue_qry.city,
    "state": venue_qry.state,
    "phone": venue_qry.phone,
    "website": venue_qry.website,
    "facebook_link": venue_qry.facebook_link,
    "seeking_talent": venue_qry.seeking_talent,
    "seeking_description": venue_qry.seeking_description,
    "image_link": venue_qry.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  db.session.close()

  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  create_venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data
  )

  try:
    db.session.add(create_venue)
    db.session.commit()
    flash('Venue '+ request.form['name'] +' was successfully listed!')

  except:
    flash('Oops! an error occurred,'+ request.form['name'] +' Venue could not be listed.')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_qry = db.session.query(Artist).order_by(Artist.id.desc()).limit(10)
  # artist_qry = Artist.query.all()

  _artists = []
  for row in artist_qry:
    _artists += [{
      "id": row.id,
      "name": row.name,
    }]

  return render_template('pages/artists.html', artists=_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  artist_search_qry = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%')).all()

  search_artist = {
    "count": 0,
    "data":[]
  }

  search_artist["count"] = len(artist_search_qry)
  for data in artist_search_qry:
    search_artist["data"] += [{
      "id": data.id,
      "name": data.name,
      "num_upcoming_shows": len(data.shows),
      }]

  return render_template('pages/search_artists.html', results=search_artist, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_qry = Artist.query.get(artist_id)

  past_shows = []
  upcoming_shows = []

  for data in artist_qry.shows:
    if data.start_time <= datetime.now():
      past_shows.append({
      "venue_id": data.venue.id,
      "venue_name": data.venue.name,
      "venue_image_link": data.venue.image_link,
      "start_time": data.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    })

    else:
      upcoming_shows.append({
      "venue_id": data.venue.id,
      "venue_name": data.venue.name,
      "venue_image_link": data.venue.image_link,
      "start_time": data.start_time.strftime('%m/%d/%Y, %H:%M:%S')
    })

  artist_data = {
    "id": artist_qry.id,
    "name": artist_qry.name,
    "genres": artist_qry.genres,
    "city": artist_qry.city,
    "state": artist_qry.state,
    "phone": artist_qry.phone,
    "website": artist_qry.website,
    "facebook_link": artist_qry.facebook_link,
    "seeking_venue": artist_qry.seeking_venue,
    "seeking_description": artist_qry.seeking_description,
    "image_link": artist_qry.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  edit_artist_qry = Artist.query.get(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=edit_artist_qry)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist_edit_qry = Artist.query.get(artist_id)

  try:
    artist_edit_qry.name = form.name.data
    artist_edit_qry.genres = form.genres.data
    artist_edit_qry.city = form.city.data
    artist_edit_qry.state = form.state.data
    artist_edit_qry.phone = form.phone.data
    artist_edit_qry.website = form.website_link.data
    artist_edit_qry.seeking_venue = form.seeking_venue.data
    artist_edit_qry.seeking_description = form.seeking_description.data
    artist_edit_qry.facebook_link = form.facebook_link.data
    artist_edit_qry.image_link = form.image_link.data
    db.session.commit()
    flash('artist ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. artist ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_edit_qry = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_edit_qry)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue_edit_qry = Venue.query.get(venue_id)

  try:
    venue_edit_qry.name = form.name.data
    venue_edit_qry.genres = form.genres.data
    venue_edit_qry.address = form.address.data
    venue_edit_qry.city = form.city.data
    venue_edit_qry.state = form.state.data
    venue_edit_qry.phone = form.phone.data
    venue_edit_qry.website = form.website_link.data
    venue_edit_qry.seeking_talent = form.seeking_talent.data
    venue_edit_qry.seeking_description = form.seeking_description.data
    venue_edit_qry.facebook_link = form.facebook_link.data
    venue_edit_qry.image_link = form.image_link.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)

  create_artist = Artist(
    name = form.name.data,
    genres = form.genres.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data
  )

  try:
    db.session.add(create_artist)
    db.session.commit()
    flash('Artist '+ request.form['name'] +' was successfully listed!')

  except:
    flash('Oops! an error occurred, Artist '+ request.form['name'] +' could not be listed.')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show_qry = Show.query.all()

  _show = []
  for row in show_qry:
    _show += [{
      "venue_id": row.venue.id,
      "venue_name": row.venue.name,
      "artist_id": row.artist.id,
      "artist_name": row.artist.name,
      "artist_image_link": row.artist.image_link,
      "start_time": row.start_time.strftime('%d/%m/%Y, %H:%M:%S'),
    }]

  return render_template('pages/shows.html', shows=_show)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  try:
    create_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(create_show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    flash('Oops! an error occurred, Show could not be listed')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

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
