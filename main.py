import moviepy.editor as mp, os, pyloudnorm as pln, soundfile as sf, json, sys, random, signal

if sys.platform == 'win32':
    from moviepy.config import change_settings

    change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

OUT = 'Generated'
VIDEO_OUTPUT = OUT + '/Videos'
AUDIO_OUTPUT = OUT + '/Audios'
DOWNLOADS = OUT + '/Downloads'

def FileName(file):
    return os.path.splitext(file)[0]


def CreateAudio(file):
    if os.path.exists(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3'):
        return
    
    audio = mp.AudioFileClip(DOWNLOADS + '/' + file).subclip(0, 30) \
        .audio_fadeout(2)
    audio.write_audiofile(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3', verbose=False, logger=None)
    audio.close()
    
    data, rate = sf.read(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3')
    meter = pln.Meter(rate)
    loundness = meter.integrated_loudness(data)
    loundness_norm = pln.normalize.loudness(data, loundness, -15.0)
    sf.write(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3', loundness_norm, rate)
    
    
def createVideo(dif, file, data):
    if os.path.exists(VIDEO_OUTPUT + '/' + FileName(file) + '.mp4'):
        return
    
    CreateAudio(file)
    
    print('Creating video for ' + file)
    
    anime, num, author, song = ' / '.join(data.get('animes', [])), ' / '.join(data.get('numbers', [])), ' / '.join(data.get('artists', [])), ' / '.join(data.get('songs', []))
    
    clip = mp.VideoFileClip(DOWNLOADS + '/' + file, target_resolution=(720, 1280)).subclip(20, 30)
    timer = mp.VideoFileClip('src/timer.mp4').subclip(10, 30)
    
    txt_clip = mp.TextClip(dif, fontsize=40, font='Impact', color='white', align='west') \
        .set_pos(('center','top')).set_duration(20)
    timer = mp.CompositeVideoClip([timer, txt_clip])
    
    txt = ' ' + anime + ' - ' + num + '\n ' + author + '\n ' + song 
    txt_clip = mp.TextClip(txt, fontsize=40, font='Impact', color='white', align='west')
    txt_clip = txt_clip.on_color(size=(txt_clip.w + 10, txt_clip.h + 10), pos=(0,0), col_opacity=0.4) \
        .set_pos(('left','bottom')).set_duration(10)
    clip = mp.CompositeVideoClip([clip, txt_clip])
    
    clip = mp.concatenate_videoclips([timer, clip])
    audio = mp.AudioFileClip(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3')
    clip.set_audio(audio) \
        .write_videofile(VIDEO_OUTPUT + '/' + FileName(file) + '.mp4', fps=24, preset='medium', verbose=False, logger=None, threads=1)
    
    clip.close()
    audio.close()
    timer.close()
        
    print('Done creating video for ' + file)

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


if __name__ == '__main__':
    FOLDERS = [OUT, VIDEO_OUTPUT, AUDIO_OUTPUT, DOWNLOADS]
    for folder in FOLDERS:
        if not os.path.exists(folder):
            os.mkdir(folder)
    
    import fetcher
    
    print('\nDone fetching, starting to create videos')
    
    configs = json.load(open('src/config.json')) 
    order = configs.get('order', [])
    
    categories = configs.get('animes', {})
    category = next(iter(categories))
    
    if len(sys.argv) > 1 and sys.argv[1].lower() in map(lambda x: x.lower(), categories.keys()):
        category = next(iter(filter(lambda x: x.lower() == sys.argv[1].lower(), categories.keys())))
    
    data = json.load(open('Generated/songs.json'))
    files, songs = [], []
    for dif in categories[category].keys():
        files += map(lambda x: FileName(x), categories[category][dif])
        songs += map(lambda x: (dif, x, data[x]), categories[category][dif])
    
    from multiprocessing import Pool, cpu_count
    pool = Pool(processes=max(cpu_count() - 2, 1), initializer=init_worker)
    try:
        for song in songs:
            pool.apply_async(createVideo, args=song)
        
        pool.close()
        pool.join()
        
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        
        todelete = filter(lambda x: os.path.splitext(x)[1] == '.mp3' ,os.listdir('./'))
        for file in todelete:
            file = os.path.splitext(file)[0].split('TEMP_MPY')[0]
            if os.path.exists(VIDEO_OUTPUT + '/' + file + '.mp4'):
                os.remove(VIDEO_OUTPUT + '/' + file + '.mp4')
            
            if os.path.exists(AUDIO_OUTPUT + '/' + file + '.mp3'):
                os.remove(AUDIO_OUTPUT + '/' + file + '.mp3')
                
            if os.path.exists(file + 'TEMP_MPY_wvf_snd.mp3'):
                os.remove(file + 'TEMP_MPY_wvf_snd.mp3')
        exit(0) 
        
    print('\nDone creating videos, starting to concatenate them')   
    random.shuffle(files)
    
    reverse = {}
    for dif in categories[category]:
        for song in categories[category][dif]:
            reverse[FileName(song)] = dif
            
    maximums = configs.get('maximums', {}) 
    new = []
    for file in files:
        cat = reverse[file]
        
        if cat in maximums and maximums[cat] > 0:
            maximums[cat] -= 1
            new.append(file)   
    files = new
    
    files = sorted(files, key=lambda file: order.index(reverse[file]))
    
    clips = [mp.VideoFileClip(VIDEO_OUTPUT + '/' + file + '.mp4') for file in files]
    
    mp.concatenate_videoclips(clips) \
        .write_videofile(OUT + '/final.mp4', fps=24, preset='medium', threads=(max(cpu_count() - 2, 1)))
