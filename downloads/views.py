import os
import boto3
import urllib
import json
import random
import string
import time
import ffmpeg
import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from moviepy.video.io import ffmpeg_tools
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path
from .forms import EmailForm, NewUserForm
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from moviepy.editor import *
from botocore.exceptions import NoCredentialsError


class AWSTranscribe(APIView):
    def post(self, request, format=None):
        url = request.data['url']

        s3_url = self.upload_file_s3(url)
        result = self.speech_to_text(s3_url)

        content = {
            "status": "Success",
            "result": result
        }
        return Response(content, status=status.HTTP_201_CREATED)

    def speech_to_text(self, url):
        AWS_ACCESS_KEY_ID = 'AKIA4QQVBFBJWMYTMXTR'
        AWS_SECRET_ACCESS_KEY = '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'
        job_name = self.getRandomText()
        job_uri = url
        transcribe = boto3.client('transcribe', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
        transcribe.start_transcription_job(TranscriptionJobName=job_name, Media={'MediaFileUri': job_uri},
                                           MediaFormat='mp4', LanguageCode='en-US')
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Not ready yet...")
            time.sleep(2)
        print(status)

        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            response = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            data = json.loads(response.read())
            # text = data['results']['transcripts'][0]['transcript']
        return data

    def upload_file_s3(self, url):
        AWS_ACCESS_KEY_ID = 'AKIA4QQVBFBJWMYTMXTR'
        AWS_SECRET_ACCESS_KEY = 'DuXuCv2yuoj54w83wiH8vwbmTwruojJCauyAbmMS'
        file_name = self.getRandomText() + ".mp4"
        download_path = "media/" + file_name
        upload_path = "samples/" + file_name
        bucket_name = 'webtalkxscript'

        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        urllib.request.urlretrieve(url, download_path)
        try:
            s3.upload_file(download_path, bucket_name, upload_path)
            pull_upload_path = "https://webtalkxscript.s3.amazonaws.com/" + upload_path
            print("Upload Successful")
            if os.path.exists(download_path):
                os.remove(download_path)
            else:
                print("The file does not exist")
            return pull_upload_path
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def getRandomText(self):
        char_set = string.ascii_uppercase + string.digits
        random_text = ''.join(random.sample(char_set * 6, 6))
        return random_text


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


@csrf_protect
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("r_success")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="downloads/register.html", context={"register_form": form})


def login_request(request):
    full_path = os.path.realpath(__file__)
    print(os.path.join(os.path.dirname(full_path), "templates", "file.txt"))
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("l_success")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()

    return render(request=request, template_name="downloads/login.html", context={"login_form": form})


def register_success(request):
    return render(request=request, template_name="downloads/register_success.html")


def login_success(request):
    return render(request=request, template_name="downloads/login_success.html")


def logout_request(request):
    logout(request)
    return redirect("login")
