import os, sys, time, json, torch
from Config.cfg import Config
from Bus.MsgBusClient import MsgBusClient

print("*** Initializing YAVOS ***")
sys_config = Config("Config/")
bus_id = 'start_yavos'

# if no input no assistant
mic_local = sys_config.cfg['MicLocal']
mic_remote = sys_config.cfg['MicRemote']
if not (mic_local or mic_remote):
    print("Error - no mic input configured!")
    quit()


# start the message bus
msg_bus = sys_config.cfg['MsgBus']
msg_bus_port = sys_config.cfg['MsgBusPort']
msg_bus_host = '0.0.0.0'
if msg_bus == 'private':
    msg_bus_host = 'localhost'
os.chdir('Bus')
os.system(f"python MsgBus.py {msg_bus_port} {msg_bus_host} &")
os.chdir('..')

time.sleep(3)

# if remote speaker is configured verify audio out bus is running
remote_audio_enabled = sys_config.cfg['RemoteSPKR']
audio_bus_out = 'localhost'
audio_bus_out_port = sys_config.cfg['AudioOutPort']
if remote_audio_enabled:
    print(f"Try to connect to audio bus out. {audio_bus_out}:{audio_bus_out_port}")
    mbc = MsgBusClient(bus_id, sync=False, host=audio_bus_out, port=audio_bus_out_port)
    # wait for connection
    to_ctr = 10
    while mbc.status != 'Connected' and to_ctr > 0:
        print(f"** [{to_ctr}]{bus_id} - {mbc.status} **")
        time.sleep(1)
        to_ctr -= 1

    mbc.exit()
    if to_ctr > 0:
        print(f"{bus_id} Connected!")
    else:
        print("Error - remote speaker configured but audio output bus is not running!")
        print("You must first open a separate terminal and run the following command")
        print(f"./Scripts/run_audio_bus_out.sh {audio_bus_out_port} {audio_bus_out}")
        quit()

# if remote mic is configured verify audio in bus is running
audio_bus_in = 'localhost'
audio_bus_in_port = sys_config.cfg['AudioInPort']
if mic_remote:
    #res = input("Remote Mic detected. Verify audio bus in server is running, then press <enter>")
    print(f"Try to connect to audio bus in. localhost:{audio_bus_in_port}")


    ab_ctr = 10   # will wait for audio bus in to come up
    while ab_ctr > 0:
        ab_ctr = ab_ctr - 1
        mbc = MsgBusClient(bus_id, sync=False, host='localhost', port=int(audio_bus_in_port))
        # wait for connection
        to_ctr = 10
        while mbc.status != 'Connected' and to_ctr > 0:
            print(f"** [{to_ctr}]{bus_id} - {mbc.status} **")
            time.sleep(1)
            to_ctr -= 1

        mbc.exit()
        if to_ctr > 0:
            print(f"{bus_id} Connected!")
            break
    if ab_ctr == 0:
        print("Error - you have a remote mic configured")
        print("But audio input bus is not running.")
        print("Start the audio input bus and retry.")
        print("./Scripts/run_audio_bus_in.sh")
        quit()

# clear out temp files
os.system("rm -f tmp/*")
os.system("rm -f Config/tts_out/*")

# start the wav to text (stt) transcriber
stt_model = sys_config.cfg['STTModel']

stt_auth_key = sys_config.cfg['STTKey']
use_gpu = sys_config.cfg['STTUseGPU']
stt_svc = sys_config.cfg['STTService']
xcriber = sys_config.cfg['STT']
lm_flag = 'Local'
if xcriber != 'local':
    lm_flag = 'Remote'

cmd = f"python -W ignore YSTT/stt.py {lm_flag} {stt_svc} {stt_model} {use_gpu} '{stt_auth_key}' &"
#print(cmd)
os.system(cmd)


## this is the output side of things

# start media svc
barge_in = sys_config.cfg['BargeIn']
local_speaker_enabled = sys_config.cfg['LocalSPKR']
cmd = f"python Media/media.py {barge_in} {local_speaker_enabled} None None &"
if remote_audio_enabled:
    cmd = f"python Media/media.py {barge_in} {local_speaker_enabled} {audio_bus_out} {audio_bus_out_port} &"
#print(cmd)
os.system(cmd)

# start simple tts svc with default voice
tts_auth_key = sys_config.cfg['TTSKey']
tts_voice = sys_config.cfg['TTSVoice']
if tts_auth_key == '':
    tts_auth_key = 'none'

tts_svc = sys_config.cfg['TTSService']
lm = sys_config.cfg['TTS']

lm_flag = 'Local'
if lm.lower() == 'remote':
    lm_flag = 'Remote'

cmd = f"python -W ignore YTTS/tts.py {lm_flag} {tts_svc} {tts_voice} '{tts_auth_key}' &"
#print(cmd)
os.system(cmd)

# give system a chance to stabilize
time.sleep(5)

# we turn the local rcognizer on last, if configured
vad_mode = sys_config.cfg["MicVad"]
if mic_local:
    print(f"Start local Mic, vad={vad_mode}")
    cmd = f"./Recognizer/Local/recognizer.sh {vad_mode} &"
    os.system(cmd)

time.sleep(2)

print("*** YAVOS Started ***")
print("*************************************************************")
print("* You can run the config server using the following command *")
print("* ./Scripts/run_config_server.sh from a separate terminal.  *")
print("*************************************************************")
print()

