# Spotify Track

Simple python scripts to track users playlists for new song updates

## Setup

This project uses Python 3.9 and pipenv

Spotify API keys should be placed in `.env`:

`SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`

```python
python3 -m pip install pipenv
pipenv install
```

You can then pass in the usernames you want to track to setup.py like so:

`pipenv run python3 setup.py user1 user2 user3 ...`

And then initialize by running `track.py` as described below.

## Tracking

The `track.py` script scans for songs and playlists added or created since the last runtime:

`pipenv run python3 track.py`

Copyright © Brian Cheng 2021
