from kivy.config import Config

Config.read("kcGames.ini")
Config.write()
Config.getint('kivy', 'show_fps')