import requests
from datetime import date
import json
import subprocess
import whisper

username = 'REPLACE WITH YOUR BROADCASTIFY USERNAME'
password = 'REPLACE WITH YOUR BROADCASTIFY PASSWORD'
#Replace feedID with feed of your interest
feedID = '34786'

downloadedDict = {}

# Start a session
session = requests.Session()

archive_url = 'https://www.broadcastify.com/archives/downloadv2/'
login_url = 'https://www.broadcastify.com/login/'
credentials = {
    'username': username,
    'password': password,
    'action': 'auth',
    'redirect': '/'
}

while True:
    #check if we are logged in, cookie hasn't expired
    response = session.get(login_url)
    if response.ok and username not in response.text:
        print('Not logged in. Attempting new login')
        response = session.post(login_url, data=credentials)
        if response.ok and username in response.text:
            print('Login successful')
        else:
            print('Login failed')
            break

        # Get ID numbers for sound files
    currentDay = date.today()
    today = currentDay.strftime("%m/%d/%y")
    ajax_url = 'https://www.broadcastify.com/archives/ajax.php?feedId=' + feedID + '&date=' + today
    response = session.get(ajax_url)
    if response.ok and 'data' in response.text:
        print('Recordings JSON list downloaded')
    else:
        print('Failed to download JSON list')
        break

    #print(response.json())
    #data = json.loads(response.text)
    data = response.json()
    for i in data['data']:
        #print(i)
        mp3number = i[0]
        startTime = i[1]
        stopTime = i[2]
        if mp3number in downloadedDict:
            next
        downloadedDict[mp3number] = 1
        print('Downloading mp3 for ' + mp3number)
        download_url = archive_url + mp3number

        startTime = startTime.replace(' ', '')
        startTime = startTime.replace(':', '')
        stopTime = stopTime.replace(' ', '')
        stopTime = stopTime.replace(':', '')
        rawFile = mp3number + "_" + currentDay.strftime('%m-%d-%Y') + "_" + startTime + "_" + stopTime
        mp3File = rawFile + ".mp3"
        wavFile = rawFile + ".wav"
        textFile = rawFile + ".txt"
        trimmedFile = rawFile + "_trimmed.wav"

        response = session.get(download_url, allow_redirects=True)
        open(mp3File, 'wb').write(response.content)
        print('File saved to: ' + mp3File)

        print('Converting mp3 to wav file')
        convertMp3ToWav = subprocess.run(['lame', '--decode', mp3File, wavFile])
        if convertMp3ToWav.returncode != 0:
            print('Lame conversion failed')
            break

        print('Trimming silence from wav file')
        removeWavSilence = subprocess.run(['sox', wavFile, trimmedFile, 'silence', '-l', '1', '0.1', '0%', '-1', '1.0', '0%'])
        if removeWavSilence.returncode != 0:
            print('Sox trimming failed')
            break

        print('Transcribing audio file with Whisper')
        model = whisper.load_model("small")
        transcription = model.transcribe(trimmedFile, fp16 = False)
        f = open(textFile, 'w')
        f.write(transcription["text"])
        f.close()


        print('Removing original sound files')
        cleanUp = subprocess.run(['rm', mp3File, wavFile])

    break
    #time.sleep(300)
    



        


