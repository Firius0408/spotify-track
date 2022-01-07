import spotifywebapi
import sys
import json
import datetime
import os
from concurrent.futures import ThreadPoolExecutor, wait

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID') 
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

if CLIENT_ID or CLIENT_SECRET:
    pass
else:
    print('Missing env variable!', file=sys.stderr)
    exit(1)

def runUser(us):
    print('Starting user %s' % us)
    while True:
        try:
            user = sp.getUser(us)
        except:
            print('Error with user %s: %s' % (us, sys.exc_info()[1]), file=sys.stderr)
            print('Retrying...', file=sys.stderr)
            continue
        try:
            playlists = sp.getUserPlaylists(user)
        except:
            print('Error with user %s playlists: %s' % (us, sys.exc_info()[1]), file=sys.stderr)
            print('Retrying...', file=sys.stderr)
        else:
            break

    print('Finished pulling playlists for user %s' % us)
    playlist_snapshot_ids = {playlist['name']: playlist['snapshot_id'] for playlist in playlists}
    oldplaylist_snapshot_ids = oldplaylists[us]
    updated_playlists = []
    new_playlists = []
    if isinstance(oldplaylist_snapshot_ids, dict):
        for name, snapshot_id in playlist_snapshot_ids.items():
            if name in oldplaylist_snapshot_ids:
                if snapshot_id != oldplaylist_snapshot_ids[name]:
                    updated_playlists.append(name)
            else:
                new_playlists.append(name)
                updated_playlists.append(name)
    else:
        updated_playlists = playlist_snapshot_ids.keys()

    data['playlists'][us] = playlist_snapshot_ids
    tempplaylists[us] = new_playlists
    futures = []
    usertemptracks = {}
    for playlist in playlists:
        if playlist['name'] not in updated_playlists or "Top Songs " in playlist['name'] or playlist['owner']['id'] != us:
            continue

        futures.append(executor.submit(addTrackUris, playlist, usertemptracks))

    wait(futures)
    temptracks[us] = usertemptracks
    print('Finished pulling tracks for user %s' % us)

def addTrackUris(playlist, usertemptracks):
    while True:
        try:
            tracks = sp.getTracksFromItem(playlist)
        except spotifywebapi.SpotifyError as err:
            print(err, file=sys.stderr)
            print('Retrying addTrackUris for playlist %s' % playlist['name'], file=sys.stderr)
        else:
            usertemptracks[playlist['name']] = tracks
            return

if __name__ == '__main__':
    with open(sys.path[0] + '/data.json', 'r') as f:
        data = json.load(f)
else:
    with open('./data.json', 'r') as f:
        data = json.load(f)

if __name__ == '__main__':
    print('Starting at %s ' % datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        offset = datetime.datetime.fromisoformat(data['timestamp'])
    except KeyError:
        print('No timestamp found in data.json, setting offset and exiting...', file=sys.stderr)
        data['timestamp'] = datetime.datetime.utcnow().isoformat()
        if __name__ == '__main__':
            with open(sys.path[0] + '/data.json', 'w') as f:
                json.dump(data, f, indent=4, separators=(',', ': '))
        else:
            with open('./data.json', 'w') as f:
                json.dump(data, f, indent=4, separators=(',', ': '))
        exit(1)
    except ValueError:
        print('Incorrectly formatted timestamp found in data.json, exiting...', file=sys.stderr)
        exit(1)

    print('Using UTC offset %s' % offset.strftime("%Y-%m-%d %H:%M:%S"))
    data['timestamp'] = datetime.datetime.utcnow().isoformat()
    try:
        users = data['users']
    except KeyError:
        print("Could not find 'users' in data.json, exiting...", file=sys.stderr)
        exit(1)

    try:
        oldplaylists = data['playlists']
    except KeyError:
        print("Could not find 'playlists' in data.json, exiting...", file=sys.stderr)
        exit(1)

    sp = spotifywebapi.Spotify(CLIENT_ID, CLIENT_SECRET)
    executor = ThreadPoolExecutor()
    futures = []
    tempplaylists = {}
    temptracks = {}
    for user in users:
        futures.append(executor.submit(runUser, user))

    wait(futures)
    print('Finished pulling data')
    executor.shutdown()
    realplaylists = {}
    for us, newuserplaylists in tempplaylists.items():
        if newuserplaylists:
            realplaylists[us] = newuserplaylists

    realtracks = {}
    for us, value in temptracks.items():
        for name, tracks in value.items():
            tracknames = [track['track']['name'] for track in tracks if datetime.datetime.strptime(track['added_at'], '%Y-%m-%dT%H:%M:%SZ') > offset and track['track'] is not None and track['track']['id'] is not None]
            if tracknames:
                if us not in realtracks.keys():
                    realtracks[us] = {}
                if name not in realtracks[us].keys():
                    realtracks[us][name] = []
                realtracks[us][name] = tracknames

    for us, value in realplaylists.items():
        print('\n')
        for playlist in value:
            print('New playlist {} detected for user {}'.format(playlist, us))

    for us, value in realtracks.items():
        print('\n%s:\n' % us)
        for name, tracks in value.items():
            print('%s:' % name)
            print('{}\n'.format('\n'.join(tracks)))

    if not realplaylists and not realtracks:
        print('\nNo change')

    if __name__ == '__main__':
        with open(sys.path[0] + '/data.json', 'w') as f:
            json.dump(data, f, indent=4, separators=(',', ': '))
    else:
        with open('./data.json', 'w') as f:
            json.dump(data, f, indent=4, separators=(',', ': '))

    print('\nFinished at %s\n' % datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
