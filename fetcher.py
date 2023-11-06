import requests, json, sys, os, json

DOWNLOAD = 'Generated/Downloads'
VIDEO_URL = "https://v.animethemes.moe"

def FileName(file):
    return os.path.splitext(file)[0]

def checkDoubles(type, anime):
    songs = []
    multiples = False
    
    for key in anime[type].keys():
        for song in anime[type][key]:
            song = FileName(song)
            song = song.split('-')[0] + '-' + song.split('-')[1].split('v')[0]
            if song in songs:
                print("Song: " + song + " appears multiple times")
                multiples = True
            else:
                songs.append(song)
    if multiples:
        print("Multiple songs with the same name, please fix the json file")
        exit(1)  

def download(song):
    if os.path.exists(DOWNLOAD + "/" + song):
        print("Skipping: " + song)
        return
    
    print("Downloading: " + song)
    r = requests.get(VIDEO_URL + "/" + song, stream=True)
    length = r.headers.get('content-length')
    if length is None:
        with open(DOWNLOAD + "/" + song, "wb") as f:
            f.write(r.content)
    else:
        dl = 0
        length = int(length)
        total = b''
        for data in r.iter_content(chunk_size=1024*1024):
            dl += len(data)
            done = int(50 * dl / length)
            total += data
            
            sys.stdout.write("\r[%s%s] %s/%sMB" % ('=' * done, ' ' * (50-done), round(dl/(1024*1024), 2), round(length/(1024*1024), 2)))
            sys.stdout.flush()
                
        with open(DOWNLOAD + "/" + song, "wb") as f:
            f.write(total)
        print()

anime = json.load(open("src/config.json", "r"))['animes']

for type in anime.keys():
    checkDoubles(type, anime)

if not os.path.exists(DOWNLOAD):
    os.makedirs(DOWNLOAD)

for type in anime.keys():
    for key in anime[type].keys():
        for song in anime[type][key]:
            download(song)
            
API = "https://api.animethemes.moe/"
if not os.path.exists("Generated/songs.json"):
    json.dump({}, open("Generated/songs.json", "w"))
        
saved = json.load(open("Generated/songs.json", "r"))

songs = [song for type in anime.keys() for key in anime[type].keys() for song in anime[type][key] if song not in saved.keys()]

for song in songs:
    r = requests.get(API + 'video/' + song + '?include=animethemeentries.animetheme.anime')
    
    if r.status_code != 200:
        print("Error while fetching: " + song)
        continue
    
    data = r.json()['video']

    print("Fetching: " + song)

    saved[song] = {
        "numbers" : [d['animetheme']['slug'] for d in data['animethemeentries']],
    }
    
    name = None
    
    for data['animethemeentries'] in data['animethemeentries']:
        
        r = requests.get(API + 'animetheme/' + str(data['animethemeentries']['animetheme']['id']) + '?include=song.artists')
        
        if r.status_code != 200:
            print("Error while fetching artists + song name for " + song)
            continue
        
        data2 = r.json()['animetheme']

        for artist in data2['song']['artists']:
            if artist['name'] not in saved[song].get('artists', []):
                saved[song]['artists'] = saved[song].get('artists', []) + [artist['name']]
                
        if data2['song']['title'] not in saved[song].get('songs', []):
            saved[song]['songs'] = saved[song].get('songs', []) + [data2['song']['title']]
            
        r = requests.get(API + 'anime/' + str(data['animethemeentries']['animetheme']['anime']['slug']) + '?include=animesynonyms')
        
        if r.status_code != 200:
            print("Error while fetching anime name for " + song)
            continue
        
        synomyms = r.json()['anime']['animesynonyms']
        synomyms.append({'text' : data['animethemeentries']['animetheme']['anime']['name']})
        
        for synomym in synomyms:
            if name is None or len(name) > len(synomym['text']):
                name = synomym['text']
                
    if len(name) > 20 and ':' in name:
        name = name.split(':')[0]
    
    saved[song]['anime'] = name
    if len(name) > 35:
        print("Anime name is too long for " + name)
                    
with open("Generated/songs.json", "w") as f:
    json.dump(saved, f)