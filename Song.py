import moviepy.editor as mp, os, pyloudnorm as pln, soundfile as sf, json, sys, random, signal, Fetcher

OUT = 'Generated'
VIDEO_DIR = OUT + '/Videos'
AUDIO_DIR = OUT + '/Audios'
DOWNLOADS = OUT + '/Downloads'

RESOLUTION = (720, 1280)
FPS = 24

class Song :

    def __init__(self, difficulty, source, starting_time = 0):
        self.difficulty = difficulty
        self.source = source
        self.starting_time = starting_time
        
    """ This method fetches the song's information from the API of animethemes.moe
    If the song is not from animethemes.moe, nothing will be fetched.
    """
    def fetch(self):
        if self.source.startswith('http'):
            return
        
        fetcher = Fetcher.Fetcher(self.source)
        
        fetcher.download()
        
        infos = fetcher.fetch()
        
        self.anime = infos.get('anime', 'Unknown')
        self.artists = infos.get('artists', [])
        self.titles = infos.get('titles', [])
        
    def __str__(self):
        return ' ' + self.anime + '\n ' + ', '.join(self.artists) + '\n ' + ', '.join(self.titles)
        
    def difficulty_txt_clip(self):
        return mp.TextClip(self.difficulty, fontsize=40, font='Impact', color='white', align='west') \
            .set_pos(('center','top')).set_duration(20)
        
    def song_txt_clip(self):
        txt_clip = mp.TextClip(self.__str__(), fontsize=40, font='Impact', color='white', align='west')
        return txt_clip.on_color(size=(txt_clip.w + 10, txt_clip.h + 10), pos=(0,0), col_opacity=0.4) \
            .set_pos(('left','bottom')).set_duration(10)
            
    def create_audio(self):
        output = AUDIO_DIR + '/' + os.path.splitext(self.source)[0] + '.mp3'
        
        if os.path.exists(output):
            return
        
        audio = mp.AudioFileClip(DOWNLOADS + '/' + self.source).subclip(self.starting_time + 0, self.starting_time + 30) \
            .audio_fadeout(2)
        audio.write_audiofile(output, verbose=False, logger=None)
        audio.close()
        
        data, rate = sf.read(output)
        loundness = pln.Meter(rate).integrated_loudness(data)
        loundness_norm = pln.normalize.loudness(data, loundness, -15.0)
        sf.write(output, loundness_norm, rate)
            
    def create_video(self):
        output = VIDEO_DIR + '/' + os.path.splitext(self.source)[0] + '.mp4'
        
        if os.path.exists(output):
            return
        
        self.create_audio()
        
        print('Creating video for ' + self.source)
        
        clip = mp.VideoFileClip(DOWNLOADS + '/' + self.source, target_resolution=RESOLUTION).subclip(self.starting_time + 20, self.starting_time + 30)
        timer = mp.VideoFileClip('src/timer.mp4').subclip(10, 30)
        
        timer = mp.CompositeVideoClip([timer, self.difficulty_txt_clip()])
        clip = mp.CompositeVideoClip([clip, self.song_txt_clip()])
        
        clip = mp.concatenate_videoclips([timer, clip])
        audio = mp.AudioFileClip(AUDIO_DIR + '/' + os.path.splitext(self.source)[0] + '.mp3')
        clip.set_audio(audio) \
            .write_videofile(output, fps=FPS, preset='medium', verbose=False, logger=None, threads=2)
        
        for f in [clip, audio, timer]:
            f.close()
            
        print('Done creating video for ' + self.source)
        
        return True