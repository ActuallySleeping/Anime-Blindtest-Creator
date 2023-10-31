import moviepy.editor as mp
import os, re, pyloudnorm as pln, soundfile as sf, json, sys

OUTPUT = 'Videos'

def FileName(file):
    return os.path.splitext(file)[0]


def CreateAudio(folder, dif, file):
    start = 0
    try :
        start = int(file.split('_')[4])
    except:
        start = 0
        
    mp.AudioFileClip(folder + '/' + dif + '/' + file).subclip(start, 30 + start) \
        .audio_fadeout(2) \
        .write_audiofile(FileName(file) + '.mp3', verbose=False, logger=None)
    
    data, rate = sf.read(FileName(file) + '.mp3')
    meter = pln.Meter(rate)
    loundness = meter.integrated_loudness(data)
    loundness_norm = pln.normalize.loudness(data, loundness, -15.0)
    sf.write(FileName(file) + '.mp3', loundness_norm, rate)
    
    
def createVideo(folder, dif, file, data):
    if os.path.exists(OUTPUT + '/' + file):
        return
    
    CreateAudio(folder, dif, file)
    
    split = file.split('.mp4')[0].split('_')
    anime, num, author, song = ' / '.join(data['animes']), ' / '.join(data['numbers']), ' / '.join(data['artists']), ' / '.join(data['songs'])
    start = 0
    try :
        start = int(split[4])
    except:
        start = 0
        
    clip = mp.VideoFileClip(folder + '/' + dif + '/' + file, target_resolution=(720, 1280)).subclip(20 + start, 30 + start)
    timer = mp.VideoFileClip('src/timer.mp4').subclip(10, 30)
    
    txt = ' ' + anime + ' - ' + num + '\n ' + author + '\n ' + song 
    txt_clip = mp.TextClip(txt, fontsize=40, font='Impact', color='white', align='west')
    txt_clip = txt_clip.on_color(size=(txt_clip.w + 10, txt_clip.h + 10), pos=(0,0), col_opacity=0.4) \
        .set_pos(('left','bottom')).set_duration(10)
    clip = mp.CompositeVideoClip([clip, txt_clip])
    
    clip = mp.concatenate_videoclips([timer, clip])
    audio = mp.AudioFileClip(FileName(file) + '.mp3')
    clip.set_audio(audio) \
        .write_videofile(OUTPUT + '/' + file, fps=24, preset='ultrafast', threads=24, verbose=False, logger=None)
        
    os.remove(FileName(file) + '.mp3')


if __name__ == '__main__':
    import fetcher
    
    print('\nDone fetching, starting to create videos')
        
    folder = 'Openings'
    if len(sys.argv) > 1 and sys.argv[1] == 'ending':
        folder = 'Endings'
    
    from multiprocessing import Pool
    
    difficulties = os.listdir(folder)
    songs = []
    data = json.load(open('OUT/songs.json'))
    
    for d in difficulties :
        
        if not os.path.isdir(folder + '/' + d) :
            continue

        files = os.listdir(folder + '/' + d)
        songs += [(folder, d, f, data[f]) for f in files]
     
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)
    
    with Pool(24) as p:
        p.starmap(createVideo, [song for song in songs])
        p.close()
        p.join()
        
    print('\nDone creating videos, starting to concatenate them')
        
    files = os.listdir(OUTPUT)
    # sort the files by the order of the categories befined in src/config.json
    configs = json.load(open('src/config.json'))
    order = configs['order']
    categories = configs['animes']['Openings' if folder == 'Openings' else 'Endings']
    
    reverse = {}
    for cat in categories.keys():
        for song in categories[cat]:
            reverse[song] = cat
    
    files = sorted(files, key=lambda file: order.index(reverse[file]))
    
    clips = [mp.VideoFileClip(OUTPUT + '/' + file) for file in files]
    
    mp.concatenate_videoclips(clips) \
        .write_videofile('OUT/final.mp4', fps=24, preset='ultrafast', threads=24)
        
