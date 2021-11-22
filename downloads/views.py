import os
import random
import string
import speech_recognition as sr
from moviepy.video.io import ffmpeg_tools
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path


class VideoDownloads(APIView):
    def post(self, request, format=None):
        url = request.data['url']
        file_path = self.addFile(url)
        if file_path:
            text = self.get_large_audio_transcription(file_path)
            if text:
                p = Path(file_path)
                dir = p.parent
                print(dir)
                for f in os.listdir(dir):
                    os.remove(os.path.join(dir, f))
                content = {
                    "status": "success",
                    "Transcription": text
                }
                return Response(content, status=status.HTTP_201_CREATED)
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
                audio_listened = r.record(source)
                # try converting it to text
                try:
                    text = r.recognize_google(audio_listened)
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text
        # return the text for all chunks detected
        return whole_text
