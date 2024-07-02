from flask import Flask, request, send_file, jsonify
from gtts import gTTS
import speech_recognition as sr
from langdetect import detect
from pydub import AudioSegment
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/tts', methods=['POST'])
def tts():
    text = request.form['text']
    lang = request.form['lang']
    tts = gTTS(text, lang=lang)
    tts.save("output.mp3")
    return send_file("output.mp3", as_attachment=True)

@app.route('/stt', methods=['POST'])
def stt():
    audio_file = request.files['file']
    audio_format = audio_file.filename.split('.')[-1]
    
    if audio_format not in ['wav', 'aiff', 'flac']:
        # Convert to WAV format
        audio = AudioSegment.from_file(audio_file)
        audio.export("temp.wav", format="wav")
        audio_file = "temp.wav"
    else:
        audio_file.save("temp." + audio_format)
        audio_file = "temp." + audio_format

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        lang = detect(text)
        
    os.remove(audio_file)  # Clean up temporary file
    return jsonify(text=text, lang=lang)

if __name__ == "__main__":
    app.run(debug=True)
