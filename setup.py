import sys
import json
import datetime

if __name__ == '__main__':
    users = sys.argv
    users.pop(0)
    data = {}
    data['users'] = users
    data['timestamp'] = datetime.datetime.utcnow().isoformat()
    playlists = {user: [] for user in users}
    data['playlists'] = playlists
    with open(sys.path[0] + '/data.json', 'w') as f:
        json.dump(data, f, indent=4, separators=(',', ': '))
