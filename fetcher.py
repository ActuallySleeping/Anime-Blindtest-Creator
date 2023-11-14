
import Song, os, requests, json, sys, random, re

OUT = 'Generated'
VIDEO_OUTPUT = OUT + '/Videos'
AUDIO_OUTPUT = OUT + '/Audios'
DOWNLOADS = OUT + '/Downloads'

VIDEO_URL = "https://v.animethemes.moe"
API = "https://api.animethemes.moe/"

class Fetcher :
    
    @staticmethod
    def check_for_doubles(songs):
        checked = []
        multiples = False
        
        for song in songs:
            song = os.path.splitext(song)[0]
            song = song.split('-')[0] + '-' + song.split('-')[1].split('v')[0] 
            
            if song in checked:
                print("Song: " + song + " appears multiple times")
                multiples = True
            else:
                checked.append(song)
                    
        if multiples:
            print("Multiple songs with the same name, please fix the json file")
            exit(1)  
    
    """Fetches the songs from a list of given song files.
    
    Example: ["PandoraHearts-OP1.webm", "Tonikawa-OP1.webm", "SteinsGate-OP1.webm"]
    @param songs: A list of song files.
    @type songs: list
    """
    def __init__(self, source):
        self.source = source
        
    def fetch(self) :
        print("Fetching: " + self.source)
        
        r = requests.get(API + 'video/' + self.source + '?include=animethemeentries.animetheme.anime')
        
        if r.status_code != 200:
            print("Error while fetching: " + self.source)
            return
        
        animethemeentries = r.json().get('video', {}).get('animethemeentries', [])
    
        number = animethemeentries[0]['animetheme']['slug']
        name = animethemeentries[0]['animetheme']['anime']['name']
        artists = []
        titles = []
        
        for animethemeentrie in animethemeentries:
            
            r = requests.get(API + 'animetheme/' + str(animethemeentrie['animetheme']['id']) + '?include=song.artists')
            
            if r.status_code != 200:
                print("Error while fetching artists + song name for " + self.source)
                continue
            
            data2 = r.json()['animetheme']

            for artist in data2['song']['artists']:
                if artist['name'] not in artists:
                    artists.append(artist['name'])
                    
            if data2['song']['title'] not in titles:
                titles.append(data2['song']['title'])
                
            r = requests.get(API + 'anime/' + str(animethemeentrie['animetheme']['anime']['slug']) + '?include=animesynonyms')
            
            if r.status_code != 200:
                print("Error while fetching anime name for " + self.source)
                continue
            
            synomyms = r.json()['anime']['animesynonyms']
            synomyms.append({'text' : animethemeentrie['animetheme']['anime']['name']})
            synomyms = filter(lambda x: re.search(r'[^A-Za-z0-9\s]',x['text']) is None, synomyms)
            synomyms = filter(lambda x: len(x['text']) > 8, synomyms)
            
            for synomym in synomyms:
                if name is None or len(name) > len(synomym['text']):
                    name = synomym['text']
                    
        if len(name) > 20 and ':' in name:
            name = name.split(':')[0]
        
        if len(name) > 35:
            print("Anime name is too long for " + name)
        
        name = name + ' - ' + number
        
        return {
            'name': name,
            'artists': artists,
            'titles': titles
        }

    def download(self):
        if os.path.exists(DOWNLOADS + "/" + self.source):
            return
        
        print("Downloading: " + self.source)
        r = requests.get(VIDEO_URL + "/" + self.source, stream=True)
        length = r.headers.get('content-length')
        if length is None:
            with open(DOWNLOADS + "/" + self.source, "wb") as f:
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
                    
            with open(DOWNLOADS + "/" + self.source, "wb") as f:
                f.write(total)
            print()