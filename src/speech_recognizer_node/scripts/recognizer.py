#! /usr/bin/env python

import rospy
import pyaudio as pa
import wave
import speech_recognition as sr
import os
from std_msgs.msg import String
from speech_recognizer_node.srv import *
from os.path import expanduser
from pocketsphinx import Pocketsphinx, get_model_path, get_data_path

def construct_wav_file(request):

    user = expanduser("~")
    path = user + "/DTAI_Internship/src/speech_recognizer_node/audio/audio_in.wav"	

    p = pa.PyAudio()

    wf = wave.open(path, 'wb')
    wf.setnchannels(request.channels)
    wf.setsampwidth(p.get_sample_size(request.sample_format))
    wf.setframerate(request.frequency)
    wf.writeframes(b''.join(request.frames))
    wf.close()

    return path

def transform_audio_to_text(filename):

    user = expanduser("~")
    path = user + "/DTAI_Internship/src/speech_recognizer_node/data/"

    lm_file = path + "generated_language_model.lm"
    dict_file = path + "generated_dictionary.dic"

    hmm_file = user + "/.local/lib/python2.7/site-packages/pocketsphinx/model/en-us"

    model_path = get_model_path()
    data_path = get_data_path()

    config = {
            'hmm': os.path.join(model_path, 'en-us'),
            'lm': os.path.join(model_path, lm_file),
            'dict': os.path.join(model_path, dict_file)
    }

    ps = Pocketsphinx(**config)
    ps.decode(
            audio_file=os.path.join(data_path, filename),
            buffer_size=2048,
            no_search=False,
            full_utt=False
    )

    text = ps.hypothesis()

    print(text)

    return text

def handle_recognize_speech(request):

    print("Constructing WAV file...")
    audiofilename = construct_wav_file(request)
    print("WAV file constructed")

    user = expanduser("~")
    path = user + "/DTAI_Internship/src/speech_recognizer_node/audio/audio.wav"

    #text = transform_audio_to_text(path)
    text = transform_audio_to_text(audiofilename)
    
    return AudioToTextResponse(text)

def recognize_speech_server():

    print("Initializing speech_recognizer_node")
    rospy.init_node('speech_recognizer_node', anonymous=True)

    service = rospy.Service('speech_recognizer_service', AudioToText, handle_recognize_speech)
    print("Speech recognizer service is now online")
    rospy.spin()

if __name__ == "__main__":
    recognize_speech_server()


