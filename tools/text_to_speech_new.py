#!/usr/bin/env python3

# Converts text into spoken language saved to an mp3 file.


import base64, json, os, subprocess, sys
try:
    import urllib.request
except ImportError:
    print("WARNING: It looks like you are using an old version of Python. Please use Python 3 if you intend to use Google Text to Speech.")

sayVoiceByLang = {
    'de': 'Anna',
    'en': 'Samantha',
    'fr': 'Thomas',
    'nl': 'Xander',
    'es': 'Monica',
    'cz': 'Zuzana',
    'it': 'Alice',
    'sk': 'Laura'
}


googleVoiceByLang = {
    'de': { 'languageCode': 'de-DE', 'name': 'de-DE-Wavenet-C' },
    'en': { 'languageCode': 'en-US', 'name': 'en-US-Wavenet-D' },
    'fr': { 'languageCode': 'fr-FR', 'name': 'fr-FR-Neural2-A' },
    'nl': { 'languageCode': 'nl-NL', 'name': 'nl-NL-Wavenet-A' },
    'es': { 'languageCode': 'es-ES', 'name': '' },
    'cz': { 'languageCode': 'cs-CZ', 'name': 'cs-CZ-Wavenet-A' },
    'it': { 'languageCode': 'it-IT', 'name': 'it-IT-Standard-B' },
    'sk': { 'languageCode': 'sk-SK', 'name': 'sk-SK-Wavenet-A' }
}


amazonVoiceByLang = {
    # See: https://docs.aws.amazon.com/de_de/polly/latest/dg/voicelist.html
    'de': 'Vicki',
    'en': 'Joanna',
    'fr': 'Léa',
    'nl': 'Lotte',
    'es': 'Lucia',
    'it': 'Carla'
}


coquiVoiceByLang = {
    # Available language models: 'tts --list_models'
    # Audio examples: https://www.youtube.com/watch?v=Vnjv2L31eyQ
    'de': 'tts_models/de/thorsten/tacotron2-DDC', #See https://www.thorsten-voice.de/
    'en': 'tts_models/en/ljspeech/vits',
    'cz': 'tts_models/cs/cv/vits',
    'sk': 'tts_models/sk/cv/vits'
}


def checkLanguage(dictionary, lang):
    if lang not in dictionary:
        print('ERROR: Language is not supported by selected text-to-speech engine\n')


def textToSpeech(text, targetFile, lang='en', useAmazon=False, useGoogleKey=None, useCoqui=False):
    print('\nGenerating: ' + targetFile + ' - ' + text)
    if useAmazon:
        response = subprocess.check_output(['aws', 'polly', 'synthesize-speech', '--output-format', 'mp3',
            '--engine','neural',
            '--voice-id', amazonVoiceByLang[lang], '--text-type', 'ssml',
            '--text', '<speak><amazon:effect name="drc"><prosody rate=\"+10%\">' + text + '</prosody></amazon:effect></speak>',
            targetFile])
    elif useGoogleKey:
        responseJson = postJson(
            'https://texttospeech.googleapis.com/v1/text:synthesize?key=' + useGoogleKey,
            {
                'audioConfig': {
                    'audioEncoding': 'MP3',
                    'speakingRate': 1.0,
                    'pitch': 2.0,  # Default is 0.0
                    'sampleRateHertz': 44100,
                    'effectsProfileId': [ 'small-bluetooth-speaker-class-device' ]
                },
                'voice': googleVoiceByLang[lang],
                'input': { 'text': text }
            }
        )

        mp3Data = base64.b64decode(responseJson['audioContent'])

        with open(targetFile, 'wb') as f:
            f.write(mp3Data)
            
    elif useCoqui:
        subprocess.call([ 'tts', '--model_name', coquiVoiceByLang[lang], '--out_path', 'temp.wav', '--text',text ])
        subprocess.call([ 'ffmpeg', '-y', '-i', 'temp.wav', '-acodec', 'libmp3lame', '-ab', '128k', '-ac', '1', targetFile ])
        os.remove('temp.wav')
        # From version 0.10.0 there is also a python based API (https://www.youtube.com/watch?v=MYRgWwis1Jk)

    else:
        subprocess.call([ 'say', '-v', sayVoiceByLang[lang], '-o', 'temp.aiff', text ])
        subprocess.call([ 'ffmpeg', '-y', '-i', 'temp.aiff', '-acodec', 'libmp3lame', '-ab', '128k', '-ac', '1', targetFile ])
        os.remove('temp.aiff')


def postJson(url, postBody, headers = None):
    if headers is None:
        headers = {}
    headers['Content-Type'] = 'application/json; charset=utf-8'
    data = json.dumps(postBody).encode('utf-8')
    try:
        request = urllib.request.Request(url, data, headers)
        with urllib.request.urlopen(request) as req:
            response_data=req.read()
        return json.loads(response_data.decode())
    except Exception as e:
        print(e)
        quit()