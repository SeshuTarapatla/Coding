import json
from sys import argv
from vosk import Model, KaldiRecognizer
import wave


file = argv[1]
