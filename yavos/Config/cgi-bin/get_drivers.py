#!/usr/bin/env python3
import os, sys, cgi, time, json, importlib

def get_voices(stt_or_tts, lm_flag, service_names):
    auth_key = None
    voice = None
    service_models = {}
    for indx in range(0,len(service_names)):
        service = service_names[indx]
        mod_str = f"{stt_or_tts}.{lm_flag}.{service}.{stt_or_tts.lower()[1:]}_driver"
        if stt_or_tts == 'YSTT':
            mod = importlib.import_module(mod_str)
            service_models[service] = mod.STTDriver.model_names
        else:
            mod = importlib.import_module(mod_str)
            service_models[service] = mod.TTSDriver.voices

    return service_models

def get_drivers():
    tts_local_drivers = os.listdir("../YTTS/Local")
    tts_remote_drivers = os.listdir("../YTTS/Remote")
    stt_local_drivers = os.listdir("../YSTT/Local")
    stt_remote_drivers = os.listdir("../YSTT/Remote")

    rez = {
            'tts_local': tts_local_drivers,
            'tts_remote': tts_remote_drivers,
            'stt_local': stt_local_drivers,
            'stt_remote': stt_remote_drivers,
            }

    # get each drivers supported models/voices
    final_result = {}

    final_result['tts_local'] = get_voices('YTTS', 'Local', rez['tts_local'])
    final_result['tts_remote'] = get_voices('YTTS', 'Remote', rez['tts_remote'])
    final_result['stt_local'] = get_voices('YSTT', 'Local', rez['stt_local'])
    final_result['stt_remote'] = get_voices('YSTT', 'Remote', rez['stt_remote'])

    return final_result

response_obj = {"result":"fail", "reason":"bad json", "data":""}

response_obj['result'] = "success"
response_obj['reason'] = "updated"
response_obj['data'] = get_drivers()

res_json = json.dumps(response_obj)
print("Content-Type: application/json\n")
print(res_json)

