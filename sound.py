import math
import numpy
import pyaudio

p = pyaudio.PyAudio()

def sine(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    return numpy.sin(numpy.arange(length) * factor)


def play_tone(stream, frequency=440, length=1, rate=44100):
    chunks = []
    chunks.append(sine(frequency, length, rate))

    chunk = numpy.concatenate(chunks) * 0.25

    stream.write(chunk.astype(numpy.float32).tostring())


def emit_sound(freq=440):
    
    stream = p.open(format=pyaudio.paFloat32,channels=1, rate=44100, output=1)

    play_tone(stream,frequency=freq,length=0.3)

    stream.close()
