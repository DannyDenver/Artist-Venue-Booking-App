#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
import sys
from sqlalchemy import func


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import Artist, Venue, Area, InfoShort, Show 


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
  unique_locations = []
  areas = []

  for venue in Venue.query.all():
    if [venue.city, venue.state] not in unique_locations:
      unique_locations.append([venue.city, venue.state])
      venuesInLoc = Venue.query.filter_by(city=venue.city).filter_by(state=venue.state)
      vnShort = []
      for vn in venuesInLoc:
        vnShort.append(InfoShort(vn.id, vn.name, vn.upcoming_shows_count))
      areas.append(Area(venue.city, venue.state, vnShort))

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term')
  venues=Venue.query.filter(func.lower(Venue.name).contains(func.lower(search_term))).all()

  venuesShort = []
  for vn in venues:
    venuesShort.append(InfoShort(vn.id, vn.name, vn.upcoming_shows_count))

  response={
    "count": len(venuesShort),
    "data": venuesShort
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  return render_template('pages/show_venue.html', venue=Venue.query.get(venue_id))

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  form.validate_on_submit()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  print(request.form)

  venueForm = VenueForm(request.form)
  if not venueForm.validate():
    return render_template('forms/new_venue.html', form=venueForm)

  duplicate = Venue.query.filter(func.lower(Venue.name)==func.lower(request.form['name'])).first()
  print(duplicate)
  if duplicate:
    print('duplicate venue')
    flash('Venue already created. Duplicate venue not added.', 'error')
    return render_template('pages/home.html')

  try:
    venue=Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'], website=request.form['website'], genres=request.form.getlist('genres'), facebook_link=request.form['facebook_link'], image_link=request.form['image_link'])
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form["name"] + ' could not be listed.', 'error')
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    db.session.query(Venue).filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term')
  artists=Artist.query.filter(func.lower(Artist.name).contains(func.lower(search_term))).all()

  artistInfo = []
  for art in artists:
    artistInfo.append(InfoShort(art.id, art.name, art.upcoming_shows_count))
  
  response={
    "count": len(artistInfo),
    "data": artistInfo
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist=Artist.query.get(artist_id)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artistForm = ArtistForm(request.form)

  if not artistForm.validate():
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=artistForm, artist=artist)

  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    print(sys.exc_info)
    print("Eeeech!")
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venueForm = VenueForm(request.form)

  if not venueForm.validate():
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=venueForm, venue=venue)

  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    print(sys.exc_info)
    print("Eeeech! Venue edits not saved")
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  form.validate_on_submit()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  print(request.form)

  artistForm = ArtistForm(request.form)
  print(artistForm.errors)
  if not artistForm.validate():
    return render_template('forms/new_artist.html', form=artistForm)

  duplicate = Artist.query.filter(func.lower(Artist.name)==func.lower(request.form['name'])).first()
  print(Artist.query.filter(func.lower(Artist.name)==func.lower(request.form['name'])).first())
  if duplicate:
    print("duplicate")
    print(duplicate)
    flash('Artist already created. Duplicate artist with same name not added.', 'error')
    return render_template('pages/home.html')

  try:
    artist=Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'], phone=request.form['phone'], genres=request.form.getlist('genres'), facebook_link=request.form['facebook_link'], image_link=request.form['image_link'])
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()  

  if error:
    flash('An error occurred. Artist ' + request.form["name"] + ' could not be listed.', 'error')
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    db.session.query(Artist).filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  return render_template('pages/shows.html', shows=Show.query.all())

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  print(request.form)

  showForm = ShowForm(request.form)
  if not showForm.validate():
    return render_template('forms/new_show.html', form=showForm)

  duplicate = Show.query.filter_by(venue_id=request.form['venue_id']).filter_by(artist_id=request.form['artist_id']).filter_by(start_time=request.form['start_time']).first()
  if duplicate:
    flash('Show already created. Duplicate show was not added.', 'error')
    return render_template('pages/home.html')

  try:
    show = Show(venue_id=request.form['venue_id'], artist_id=request.form['artist_id'], start_time=request.form['start_time'])
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  
  if error:
    flash('An error occurred. Show could not be listed.', 'error')
  if not error:
    flash('Show was successfully listed!')
  
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

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 80))
#     app.run(host='0.0.0.0', port=port)