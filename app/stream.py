from flask import Blueprint, send_file, abort

from . import models

Stream = Blueprint('stream', __name__, url_prefix='/stream')

@Stream.route('/<stream_id>')
def stream(stream_id):
    track = models.Track.query.filter(models.Track.stream==stream_id).one()
    if not track:
        abort(404)

    filename = track.location
    return send_file(filename)
