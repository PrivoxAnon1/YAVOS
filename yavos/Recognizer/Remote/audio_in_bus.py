import os, sys, time, asyncio
from websockets.asyncio.server import serve
from Bus.MsgBusClient import MsgBusClient
from Bus.message_types import MSG_WAV_IN
""" open a websocket server and wait for binary
data from remote connected smart microphones. 
then convert the webm to a .wav file and notify
the system by sending a MSG_WAV_IN (value='wav') 
message on the message bus to the stt service. """

def sav_wav_data(dtype, out_dir, msg, ctr):
    input_filename = f"test{ctr}.webm"
    if dtype == 'WAV':
        input_filename = f"test{ctr}.wav"
    elif dtype == 'MP3':
        input_filename = f"test{ctr}.mp3"
    elif dtype == 'MP4':
        input_filename = f"test{ctr}.mp4"
    else:
        # else unsupported binary input file type so assume webm
        pass

    # note the privoice code uses io buffers and is a much better 
    # and faster implementation for converting and saving the wav
    # data to disk. 
    wav_filename = f"{out_dir}test{ctr}.wav"
    fh = open(input_filename, "wb")
    fh.write(msg)
    fh.close()
    # its important to not leak to stdout so the next line mught be necessary on some systems
    #cmd = f"ffmpeg -v quiet -loglevel panic -hide_banner -nostats -y -i {input_filename} -acodec pcm_s16le -ac 1 -ar 16000 {wav_filename}"
    cmd = f"ffmpeg -loglevel panic -i {input_filename} -y -acodec pcm_s16le -ac 1 -ar 16000 {wav_filename}"
    os.system(cmd)
    print(cmd)
    cmd = f"rm {input_filename}"
    os.system(cmd)
    return wav_filename

async def pr_serve(websocket):
    output_directory = "tmp/"
    current_directory = os.getcwd()
    ctr = 0
    final_wav_data = b''
    rcv_state = 'idle'
    dtype = ''
    async for message in websocket:
        """we assume only a binary webm is being communicated
        over this channel in this direction so here we 
        assemble wav data. the protocol is msg = "BIN"
        followed by binary messages until the msg "END" is
        received. messages received outside this protocol 
        are ignored. the text from wav (stt) is normally
        sent back but we just send back OK for now.
        state values are 'idle', 'wav' and 'completed'"""
        if rcv_state == 'idle':
            s = message[0] + message[1] + message[2]
            #if s == 'BIN':
            if message[0] == 'B' and message[1] == 'I' and message[2] == 'N':
                # formal header is BIN xxx where xxx is one of
                # WAV, WEB, MP3, MP4. this is always 7 bytes
                rcv_state = 'wav'
                dtype = message[4] + message[5] + message[6]
        else:
            if message[0] == 'Y' and message[1] == 'a' and message[2] == 'E' and message[3] == 'N' and message[4] == 'D' and message[5] == 'v' and message[6] == 'O':
                rcv_state = 'completed'
            else:
                final_wav_data += message

        if rcv_state == 'completed':
            rcv_state = 'idle'
            # we finally have our binary wav file data
            start_time = time.time()
            wav_filename = sav_wav_data(dtype, output_directory, final_wav_data, ctr)
            final_wav_data = b''
            await websocket.send("TXT1:" + "OK") # send back confirmation
            msg = {
                'error':'',
                'subtype':'speech',
                'skill_id':'stt_svc',
                'from_skill_id':bus_id,
                'filename': wav_filename,
                }
   
            mbc.send(MSG_WAV_IN, 'stt_svc', msg)
            print(f"sent msg {msg}")
            ctr += 1

async def main(host, port, bus_id, mbc):
    while True:
        print("Waiting for connections")
        try:
            async with serve(pr_serve, host, port) as server:     
                await server.serve_forever()
        except:
            print("Warning - audio_bus_in - Connection reset!")


if __name__ == "__main__":
    # usage audio_in_bus.py host port where host is either
    # public or private
    bus_id = 'remote_recognizer'
    mbc = ''

    while True:
        print("audio bus in - connecting to main message bus")
        mbc = MsgBusClient(bus_id, sync=False)
        ctr = 10
        while mbc.status != 'Connected' and ctr > 0:
            ctr = ctr - 1
            #print(f"** {bus_id}: {mbc.status} **")
            time.sleep(1)

        if ctr > 0:
            print("audio bus in - connected to main message bus")
            break

    host = sys.argv[1]
    port = int(sys.argv[2])
    host_address = 'localhost'
    if host.lower() == "public":
        host_address = '0.0.0.0'
    print(f"Remote wav saver [{bus_id}] running on {host_address}, port = {port}")
    asyncio.run(main(host_address, port, bus_id, mbc))

