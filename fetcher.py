import requests, json, sys, os, json

VIDEO_URL = "https://v.animethemes.moe"

def checkDoubles(type, anime):
    songs = []
    multiples = False
    
    for key in anime[type].keys():
        for song in anime[type][key]:
            if song in songs:
                print("Song: " + song + " appears multiple times")
                multiples = True
            else:
                songs.append(song)
    if multiples:
        print("Multiple songs with the same name, please fix the json file")
        exit(1)  

def download(song, type, key):
    if os.path.exists(type + "/" + key + "/" + song):
        print("Skipping: " + song)
        return
    
    print("Downloading: " + song)
    r = requests.get(VIDEO_URL + "/" + song, stream=True)
    length = r.headers.get('content-length')
    if length is None:
        with open(type + "/" + key + "/" + song, "wb") as f:
            f.write(r.content)
    else:
        dl = 0
        length = int(length)
        with open(type + "/" + key + "/" + song, "wb") as f:
            for data in r.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                sys.stdout.flush()
        print()
                
if __name__ == "__main__":

    with open("src/animes.json", "r") as f:
        anime = json.load(f)
        
        # Checking if they are songs that appear multiple times
        for type in anime.keys():
            checkDoubles(type, anime)
        
        # Downloading the songs
        for type in anime.keys():
            if not os.path.exists(type):
                os.makedirs(type)
            
            for key in anime[type].keys():
                if not os.path.exists(type + "/" + key):
                    os.makedirs(type + "/" + key)
                
                for song in anime[type][key]:
                    download(song, type, key)
                    
        # creating the json file with the file name, the opening/ending number, the author and the song title with the animethemes.moe API
        API = "https://api.animethemes.moe/"
        saved = {}
        
        for type in anime.keys():
            for key in anime[type].keys():
                for song in anime[type][key]:
                    r = requests.get(API + 'video/' + song + '?include=animethemeentries.animetheme.anime')
                    
                    if r.status_code != 200:
                        print("Error while fetching: " + song)
                        continue
                    
                    data = r.json()['video']
            
                    print("Fetching: " + song)
                    
                    print(data.keys())
            
                    saved[song] = {
                        "animes" : [d['animetheme']['anime']['name'] for d in data['animethemeentries']],
                        "numbers" : [d['animetheme']['slug'] for d in data['animethemeentries']],
                    }
                    
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
                        
        if not os.path.exists("OUT"):
            os.makedirs("OUT")
                        
        with open("OUT/songs.json", "w") as f:
            json.dump(saved, f, indent=4)