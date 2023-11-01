import moviepy.editor as mp, os, pyloudnorm as pln, soundfile as sf, json, sys, random

VIDEO_OUTPUT = 'Videos'
AUDIO_OUTPUT = 'Audios'

def FileName(file):
    return os.path.splitext(file)[0]


def CreateAudio(folder, dif, file):
    if os.path.exists(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3'):
        return
    
    audio = mp.AudioFileClip(folder + '/' + dif + '/' + file).subclip(0, 30) \
        .audio_fadeout(2)
    audio.write_audiofile(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3', verbose=False, logger=None)
    audio.close()
    
    data, rate = sf.read(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3')
    meter = pln.Meter(rate)
    loundness = meter.integrated_loudness(data)
    loundness_norm = pln.normalize.loudness(data, loundness, -15.0)
    sf.write(AUDIO_OUTPUT + '/' + FileName(file) + '.mp3', loundness_norm, rate)
    
    
def createVideo(folder, dif, file, data):
    if os.path.exists(VIDEO_OUTPUT + '/' + FileName(file) + '.mp4'):
        return
    
    CreateAudio(folder, dif, file)
    
    print('Creating video for ' + file)
    
    anime, num, author, song = ' / '.join(data.get('animes', [])), ' / '.join(data.get('numbers', [])), ' / '.join(data.get('artists', [])), ' / '.join(data.get('songs', []))
    
    clip = mp.VideoFileClip(folder + '/' + dif + '/' + file, target_resolution=(720, 1280)).subclip(20, 30)
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


if __name__ == '__main__':
    import fetcher
    
    print('\nDone fetching, starting to create videos')
        
    folder = 'Openings'
    if len(sys.argv) > 1 and sys.argv[1] == 'ending':
        folder = 'Endings'
    
    from multiprocessing import Pool, cpu_count
    
    difficulties = os.listdir(folder)
    songs = []
    data = json.load(open('OUT/songs.json'))
    
    for d in difficulties :
        
        if not os.path.isdir(folder + '/' + d) :
            continue

        files = os.listdir(folder + '/' + d)
        songs += [(folder, d, f, data[f]) for f in files]
     
    if not os.path.exists(VIDEO_OUTPUT):
        os.mkdir(VIDEO_OUTPUT)
    if not os.path.exists(AUDIO_OUTPUT):
        os.mkdir(AUDIO_OUTPUT)
    
    with Pool(max(cpu_count() - 2, 1)) as p:
        p.starmap(createVideo, [song for song in songs])
        p.close()
        p.join()
        
    print('\nDone creating videos, starting to concatenate them')
       
    configs = json.load(open('src/config.json')) 
    order = configs.get('order', [])
    categories = configs['animes']['Openings' if folder == 'Openings' else 'Endings']
    
    files = []
    for cat in categories.keys():
        files += categories[cat]
    files = [FileName(file) for file in files]
    
    random.shuffle(files)

    reverse = {}
    for cat in categories.keys():
        for song in categories[cat]:
            reverse[FileName(song)] = cat
    
    files = sorted(files, key=lambda file: order.index(reverse[file]))
    
    clips = [mp.VideoFileClip(VIDEO_OUTPUT + '/' + file + '.mp4') for file in files]
    
    mp.concatenate_videoclips(clips) \
        .write_videofile('OUT/final.mp4', fps=24, preset='medium', threads=(max(cpu_count() - 2, 1)))
        
