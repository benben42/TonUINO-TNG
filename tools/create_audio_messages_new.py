#!/usr/bin/env python3

# Creates the audio messages needed by TonUINO.


import os, re, shutil, text_to_speech_new

language = 'sk'
audioMessagesFile = 'audio_messages_{}.txt'.format(language)
targetDir = 'sd-card-test'
skip_numbers = True
only_new = True

if __name__ == '__main__':    
    if not os.path.isfile(audioMessagesFile):
        print('Input file does not exist: ' + os.path.abspath(audioMessagesFile))
        quit()

    if os.path.isdir(targetDir):
        print("Directory `" + targetDir + "` already exists.")
    else:
        os.mkdir(targetDir)
        os.mkdir(targetDir + '/advert')
        os.mkdir(targetDir + '/mp3')


    if not skip_numbers == True:
        for i in range(1,256):
            targetFile1 = '{}/mp3/{:0>4}.mp3'.format(targetDir, i)
            targetFile2 = '{}/advert/{:0>4}.mp3'.format(targetDir, i)
            text_to_speech_new.textToSpeech(text='{}'.format(i), targetFile=targetFile1, lang=language)
            shutil.copy(targetFile1, targetFile2)

    with open(audioMessagesFile) as f:
        lineRe = re.compile('^([^|]+)\\|(.*)$')
        for line in f:
            match = lineRe.match(line.strip())
            if match:
                fileName = match.group(1)
                if only_new and os.path.isfile(targetDir + "/" + fileName):
                    continue
                text = match.group(2)
                text_to_speech_new.textToSpeech(text=text, targetFile=targetDir + "/" + fileName, lang=language, useCoqui=True)
