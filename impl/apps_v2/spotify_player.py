import numpy as np, requests, math, time, threading
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

class SpotifyScreen:
    def __init__(self, config, modules, fullscreen):
        self.modules = modules

        self.font = ImageFont.truetype("fonts/tiny.otf", 5)

        self.canvas_width = config.getint('System', 'canvas_width', fallback=64)
        self.canvas_height = config.getint('System', 'canvas_height', fallback=32)
        self.title_color = (255,255,255)
        self.artist_color = (255,255,255)
        self.play_color = (102, 240, 110)

        self.full_screen_always = fullscreen

        self.current_art_url = ''
        self.current_art_img = None
        self.current_title = ''
        self.current_artist = ''

        self.title_animation_cnt = 0
        self.artist_animation_cnt = 0
        self.last_title_reset = math.floor(time.time())
        self.last_artist_reset = math.floor(time.time())
        self.scroll_delay = 4

        self.paused = True
        self.paused_time = math.floor(time.time())
        self.paused_delay = 5

        self.is_playing = False

        self.last_fetch_time = math.floor(time.time())
        self.fetch_interval = 1
        self.spotify_module = self.modules['spotify']

        self.response = None
        self.thread = threading.Thread(target=self.getCurrentPlaybackAsync)
        self.thread.start()

    def getCurrentPlaybackAsync(self):
        # delay spotify fetches
        time.sleep(3)
        while True:
            self.response = self.spotify_module.getCurrentPlayback()
            time.sleep(1)

    def generate(self):
        if not self.spotify_module.queue.empty():
            self.response = self.spotify_module.queue.get()
            self.spotify_module.queue.queue.clear()
        return self.generateFrame(self.response)

    def generateFrame(self, response):
        if response is not None:
            (artist, title, art_url, self.is_playing, progress_ms, duration_ms) = response

            if (self.current_title != title or self.current_artist != artist):
                self.current_artist = artist
                self.current_title = title
                self.title_animation_cnt = 0
                self.artist_animation_cnt = 0
            if self.current_art_url != art_url:
                self.current_art_url = art_url
                response = requests.get(self.current_art_url)
                img = Image.open(BytesIO(response.content))
                self.current_art_img = img.resize((self.canvas_height, self.canvas_height), resample=Image.LANCZOS)

            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)

            draw.line((38,15,58,15), fill=(100,100,100))
            draw.line((38,15,38+round(((progress_ms / duration_ms) * 100) // 5),15), fill=(180,180,180))

            title_len = self.font.getlength(self.current_title)
            if title_len > 31:
                spacer = "   "
                draw.text((34-self.title_animation_cnt, 0), self.current_title + spacer + self.current_title, self.title_color, font = self.font)
                self.title_animation_cnt += 1
                if self.title_animation_cnt == self.font.getlength(self.current_title + spacer):
                    self.title_animation_cnt = 0
            else:
                draw.text((34-self.title_animation_cnt, 0), self.current_title, self.title_color, font = self.font)

            artist_len = self.font.getlength(self.current_artist)
            if artist_len > 31:
                spacer = "     "
                draw.text((34-self.artist_animation_cnt, 7), self.current_artist + spacer + self.current_artist, self.artist_color, font = self.font)
                self.artist_animation_cnt += 1
                if self.artist_animation_cnt == self.font.getlength(self.current_artist + spacer):
                    self.artist_animation_cnt = 0
            else:
                draw.text((34-self.artist_animation_cnt, 7), self.current_artist, self.artist_color, font = self.font)

            draw.rectangle((32,0,33,32), fill=(0,0,0))

            if self.current_art_img is not None:
                frame.paste(self.current_art_img, (0,0))

            drawPlayPause(draw, self.is_playing, self.play_color)
            return (frame, self.is_playing)
        else:
            #not active
            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)

            self.current_art_url = ''
            self.is_playing = False
            self.title_animation_cnt = 0
            self.artist_animation_cnt = 0
            self.last_title_reset = math.floor(time.time())
            self.last_artist_reset = math.floor(time.time())
            self.paused = True
            self.paused_time = math.floor(time.time())

            return (None, self.is_playing)

def drawPlayPause(draw, is_playing, color):
    if not is_playing:
        draw.line((45,19,45,25), fill = color)
        draw.line((46,20,46,24), fill = color)
        draw.line((47,20,47,24), fill = color)
        draw.line((48,21,48,23), fill = color)
        draw.line((49,21,49,23), fill = color)
        draw.line((50,22,50,22), fill = color)
    else:
        draw.line((45,19,45,25), fill = color)
        draw.line((46,19,46,25), fill = color)
        draw.line((49,19,49,25), fill = color)
        draw.line((50,19,50,25), fill = color)
