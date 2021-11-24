import os
import random
import string
import time
import speech_recognition as sr
from moviepy.video.io import ffmpeg_tools
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk
from .forms import EmailForm
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render


class VideoDownloads(APIView):
    def post(self, request, format=None):
        url = request.data['url']
        file_path = self.addFile(url)
        if file_path:
            # text = self.get_large_audio_transcription(file_path)
            list_result = self.speech_recognize_continuous_from_file(file_path)

            if list_result:
                try:
                    text = self.listToString(list_result)
                    p = Path(file_path)
                    dir = p.parent
                    print(dir)
                    for f in os.listdir(dir):
                        os.remove(os.path.join(dir, f))
                    content = {
                        "status": "success",
                        "transcription_in_text": text,
                        "transcription_in_list": list_result,
                    }

                    return Response(content, status=status.HTTP_201_CREATED)
                except Exception as e:
                    content = {
                        "status": "failure",
                        "error": e,
                        "return": list_result
                    }
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
        content = {
            "status": "failure"
        }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    def getRandomText(self):
        char_set = string.ascii_uppercase + string.digits
        random_text = ''.join(random.sample(char_set * 6, 6))
        return random_text

    def addFile(self, url):
        try:
            file_path = "media/" + self.getRandomText() + ".wav"
            ffmpeg_tools.ffmpeg_extract_audio(url, file_path)
            return file_path
        except Exception as e:
            return False

    def speech_recognize_continuous_from_file(self, path):
        """performs continuous speech recognition with input from an audio file"""
        # <SpeechContinuousRecognitionWithFile>
        try:
            subscription_key = " 06a79298e24448b39ccca9d5d1ad8535"
            speech_region = "eastus"
            speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=speech_region)
            audio_config = speechsdk.audio.AudioConfig(filename=path)
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
            done = False

            def stop_cb(evt):
                """callback that signals to stop continuous recognition upon receiving an event `evt`"""
                print('CLOSING on {}'.format(evt))
                nonlocal done
                done = True

            all_results = []

            def handle_final_result(evt):
                all_results.append(evt.result.text)

            speech_recognizer.recognized.connect(handle_final_result)
            # Connect callbacks to the events fired by the speech recognizer
            speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
            speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
            speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
            speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
            speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
            # stop continuous recognition on either session stopped or canceled events
            speech_recognizer.session_stopped.connect(stop_cb)
            speech_recognizer.canceled.connect(stop_cb)

            # Start continuous speech recognition
            speech_recognizer.start_continuous_recognition()
            while not done:
                time.sleep(.5)

            speech_recognizer.stop_continuous_recognition()
            return all_results
        except Exception as e:
            return e

    # Python program to convert a list
    # to string using join() function

    # Function to convert
    def listToString(selt, s):
        # initialize an empty string
        str1 = " "
        # return string
        return (str1.join(s))

    def get_large_audio_transcription(self, path):
        """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
        """
        r = sr.Recognizer()
        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
                                  # experiment with this value for your target audio file
                                  min_silence_len=500,
                                  # adjust this per requirement
                                  silence_thresh=sound.dBFS - 14,
                                  # keep the silence for 1 second, adjustable as well
                                  keep_silence=500,
                                  )
        folder_name = "media"
        # create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            with sr.AudioFile(chunk_filename) as source:
                # r.adjust_for_ambient_noise(source)
                # audio_listened = r.listen(source)
                audio_listened = r.record(source)
                # try converting it to text
                try:
                    text = r.recognize_ibm(audio_listened)
                except sr.UnknownValueError as e:
                    print("Could not understand audio")
                    # print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text
        # return the text for all chunks detected
        return whole_text


def sendMail(request):
    # create a variable to keep track of the form
    messageSent = False
    # check if form has been submitted
    if request.method == 'POST':
        form = EmailForm(request.POST)
        # check if data from the form is clean
        if form.is_valid():
            cd = form.cleaned_data
            subject = "Sending an email with Django"
            message = cd['message']
            print(message)
            # send the email to the recipent
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [cd['recipient']])
            # set the variable initially created to True
            messageSent = True
    else:
        form = EmailForm()
    return render(request, 'index.html', {
        'form': form,
        'messageSent': messageSent,
    })
