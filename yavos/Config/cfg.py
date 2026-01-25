import os, yaml

# simple yaml based config class
class Config:
    # minimal yaml based config file support class
    config_defaults = {
            'AudioInBus':'public',
            'AudioInPort':'none',
            'AudioOutBus':'public',
            'AudioOutPort':'none',
            'BargeIn': 'false',
            'FfmpegCmd': 'ffmpeg',
            'LocalSPKR':'false',
            'LogLevel': 'i',
            'MicLocal': 'true',
            'MicLevelCmd':'pactl set-source-volume $(pactl info | grep "Default Source" | cut -d " " -f3) %s',
            'MicRemote': 'false',
            'MicVad': 'loose',
            'MinConf': 6.5,
            'MsgBus':'public',
            'MsgBusPort':'4000',
            'PlayWavCmd': 'aplay',
            'RecordWavCmd': 'arecord',
            'RemoteSPKR':'false',
            'SpkrLevelCmd':'amixer -D pulse sset Master %s',
            'STT': 'local',
            'STTKey': 'none',
            'STTModel': 'tiny.en',
            'STTService': 'whisper',
            'STTUseGPU': 'false',
            'TTS':'local',
            'TTSKey': 'none',
            'TTSService':'piper',
            'TTSVoice':'en_US-lessac-medium',
            'Skills':[
              'Volume',
              ]
        }

    def __init__(self, cfg_dir):
        self.config_file = cfg_dir + 'yavos.yml'

        self.cfg = None
        try:
            self.cfg = self.load_cfg()
        except:
            pass

        # if not exists create
        if self.cfg is None:
            self.cfg = self.config_defaults
            self.save_cfg()
            self.cfg = self.load_cfg()

    def load_cfg(self):
        with open(self.config_file, "r") as ymlfile:
            return yaml.safe_load(ymlfile)

    def save_cfg(self):
        with open(self.config_file, 'w') as yamlfile:
            data = yaml.dump(self.cfg, yamlfile, width=200)

