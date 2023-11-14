import moviepy.editor as mp, os, pyloudnorm as pln, soundfile as sf, json, sys, random, signal, Song, MultiThreading
from multiprocessing import cpu_count

OUT = 'Generated'
VIDEO_DIR = OUT + '/Videos'
AUDIO_DIR = OUT + '/Audios'
DOWNLOADS = OUT + '/Downloads'

def getAnime(song):
    return FileName(song).split('-')[0]

def cleanup():
    todelete = filter(lambda x: os.path.splitext(x)[1] == '.mp3' ,os.listdir('./'))
    for file in todelete:
        file = os.path.splitext(file)[0].split('TEMP_MPY')[0]   
        if os.path.exists(VIDEO_DIR + '/' + file + '.mp4'):
            os.remove(VIDEO_DIR + '/' + file + '.mp4')
        
        if os.path.exists(AUDIO_DIR + '/' + file + '.mp3'):
            os.remove(AUDIO_DIR + '/' + file + '.mp3')
            
        if os.path.exists(file + 'TEMP_MPY_wvf_snd.mp3'):
            os.remove(file + 'TEMP_MPY_wvf_snd.mp3')
    exit(0) 

if __name__ == '__main__':
    FOLDERS = [OUT, VIDEO_DIR, AUDIO_DIR, DOWNLOADS]
    for folder in FOLDERS:
        if not os.path.exists(folder):
            os.mkdir(folder)
    
    print('\nDone fetching, starting to create videos')
    
    configs = json.load(open('src/config.json')) 
    order = configs.get('order', [])
    
    categories = configs.get('animes', {})
    category = next(iter(categories))
    
    if len(sys.argv) > 1 and sys.argv[1].lower() in map(lambda x: x.lower(), categories.keys()):
        category = next(iter(filter(lambda x: x.lower() == sys.argv[1].lower(), categories.keys())))
    
    #data = json.load(open('Generated/songs.json'))
    songs = []
    for dif in categories[category].keys():
        songs += map(lambda x: Song.Song(dif, x, configs.get('starting time', {}).get(x, 0)), categories[category][dif])
    
    for song in songs:
        song.fetch()
    
    '''
    from multiprocessing import Pool, cpu_count
    pool = Pool(processes=max(round(cpu_count() / 2) - 2, 1), initializer=init_worker)
    try:
        for song in songs:
            pool.apply_async(create_video_wrapper, (song,))
        
        pool.close()
        pool.join()
        
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        
        todelete = filter(lambda x: os.path.splitext(x)[1] == '.mp3' ,os.listdir('./'))
        for file in todelete:
            file = os.path.splitext(file)[0].split('TEMP_MPY')[0]   
            if os.path.exists(VIDEO_DIR + '/' + file + '.mp4'):
                os.remove(VIDEO_DIR + '/' + file + '.mp4')
            
            if os.path.exists(AUDIO_DIR + '/' + file + '.mp3'):
                os.remove(AUDIO_DIR + '/' + file + '.mp3')
                
            if os.path.exists(file + 'TEMP_MPY_wvf_snd.mp3'):
                os.remove(file + 'TEMP_MPY_wvf_snd.mp3')
        exit(0) 
    '''
    
    if MultiThreading.multi_thread(Song.Song.create_video, songs, 1):
        cleanup()
        
    print('\nDone creating videos, starting to concatenate them')   
    #random.shuffle(files)
    
    '''
    doubles = json.load(open('Generated/doubles.json'))
    doubled = []
    
    reverse = {}
    for dif in categories[category]:
        for song in categories[category][dif]:
            reverse[os.path.splitext(song)[0]] = dif
            
    maximums = configs.get('maximums', {}) 
    new = []
    for file in files:
        if getAnime(file) in doubles:
            double = False
            for song in doubles[getAnime(file)]:
                if song in files:
                    double = True
                    break
            if double:
                continue
        if getAnime(file) in doubled:
            continue
        else:
            doubled.append(getAnime(file))
        
        cat = reverse[file]
        
        if cat in maximums and maximums[cat] > 0:
            maximums[cat] -= 1
            new.append(file)   
    files = new
    
    files = sorted(files, key=lambda file: order.index(reverse[file]))
    
    clips = [mp.VideoFileClip(VIDEO_DIR + '/' + file + '.mp4') for file in files]
    
    mp.concatenate_videoclips(clips, method='chain') \
        .write_videofile(OUT + '/final.mp4', fps=24, preset='medium', threads=(max(cpu_count() - 2, 1)))
    '''