import os
import pyaudio # Handles audio input/output.
from vosk import Model, KaldiRecognizer # speech recognition framework
import requests  # pip install requests
import pyttsx3  # Converts text to speech
import json  # Parses JSON data
import datetime
from time import sleep
import random
import pyjokes
# import vlc

# =========================================
# Change line 82 if using external AI API
# =========================================

# ~~~~~~~~~~~~~~ Name Settings ~~~~~~~~~~~~
user = "Maker"                            # User Name
SN = "pAI"                            # Device Name
greetings = ['Hi', 'Yes?', 'Hello', 'How may I help?', 'Whats on',
             f'Anything for You {user}!']


# sound_start_lis = vlc.MediaPlayer("audio/computerbeep_44.mp3")
# sound_stop_lis = vlc.MediaPlayer("audio/computerbeep_43.mp3")
# sound_open = vlc.MediaPlayer("audio/computerbeep_44.mp3")

# ~~~~~~~~~~~~~~ Chatbot Settings ~~~~~~~~~~~~

# model files, OG: qwen2:0.5b, tinydolphin, deepseek-r1:1.5b..... CUSTOM: c100
ai_model = "deepseek-r1:1.5b"
# ai_model = "c100"
# ai_model = "qwen2:0.5b"
# ai_model = "tinydolphin"

message = [
    {
        "role": "system",
        "content": """
        You are a friendly Robot named C1-00
        """
    },
    {
        "role": "user",
        "content": """
        Please introduce yourself and do not add
        'how can I help you today?' at
        the end of the response
        """
    }
]

today = datetime.date.today()


# Load Vosk model for offline speech recognition
def load_vosk_model():
    model_path = "models/EN"
    if not os.path.exists(model_path):
        raise FileNotFoundError("Vosk model not found! Download and place it in the 'models' directory.")
    return Model(model_path)


# Load Vosk model
model = load_vosk_model()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ STT Setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Listen to microphone input and transcribe using Vosk
def listen_and_transcribe(model):
    rec = KaldiRecognizer(model, 16000)  # Vosk model and a sample rate of 16000 Hz
    audio = pyaudio.PyAudio() # Initializes the PyAudio instance for handling audio input/output.
    stream = audio.open(
        format=pyaudio.paInt16, # Opens an audio input stream
        channels=1, # Indicates mono audio (single channel).
        rate=16000, # The sample rate
        input=True, # Specifies that this stream is for audio input.
        frames_per_buffer=8192 # Sets the size of the buffer that holds audio data before being processed.
        )
    stream.start_stream()  # Begins the audio stream

    # speak_text("... Awaiting Input...")
    while True:
        data = stream.read(8096, exception_on_overflow=False) # Reads 4096 bytes of audio data (half of the buffer size)
        if rec.AcceptWaveform(data):   # Processes the audio chunk Returns True if the audio chunk is sufficient
            result = rec.Result()  # Retrieves the transcription result as a JSON string.
            text = eval(result).get('text', '')  # Converts the JSON string into a Python dictionary
            if text:
                return text


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Ollama Setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Send the transcribed text to Ollama and get a response
def query_ollama(input_text):
    url = "http://localhost:11434/api/generate"

    payload = {"model": ai_model, "prompt": input_text}  # The input prompt provided by the user.
    try:

        response = requests.post(url, json=payload, stream=True)  # Stream the response incrementally instead of loading it all at once.
        response.raise_for_status() # Raises an exception

        full_response = ""    # Accumulates the complete response from the API.
        done = False

        # Iterate over the response in chunks
        for line in response.iter_lines(decode_unicode=True):  # It reads the response line by line
            if line:
                data = json.loads(line) # function takes a JSON-formatted string (the line) and converts it into a Python dictionary
                full_response += data.get("response", "")
                if data.get("done", False):   # Checks if the "done" field in the JSON is True, signaling the end of the response.
                    done = True
                    break

        if done:
            return full_response
        else:
            return "Ollama could not generate a valid response."

    except Exception as e:
        return f"Error: {e}"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TTS Setup ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Convert Ollama's response to speech
def speak_text(text):
    engine = pyttsx3.init()

    rate = engine.getProperty('rate')  # getting details of current speaking rate
    engine.setProperty(rate, 198)  # speed of speech

    voices = engine.getProperty("voices")
    engine.setProperty(voices, voices[0].id)

    engine.say(text)
    # The say() method takes the string passed as an argument (in this case, text)
    # and adds it to the speech queue.
    engine.runAndWait() # tells the engine to start processing the queued text and actually speak it out loud.


def greet():
    # sound_open.play()
    # sleep(2)
    speak_text(random.choice(greetings))
    speak_text(f"{SN}. Running Checks..")
    hour = datetime.datetime.now().hour
    if (hour >= 0) and (hour < 12):
        speak_text(f"Good Morning Daniel, It is " +
               datetime.datetime.now().strftime("%H:%M"))
    elif (hour >= 12) and (hour < 18):
        speak_text(f"Good afternoon, It is " +
               datetime.datetime.now().strftime("%H:%M"))
    elif (hour >= 18) and (hour < 24):
        speak_text(f"Good Evening, It is " +
               datetime.datetime.now().strftime("%H:%M"))


def weather():
    city = "Exeter"
    res = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=16f0afad2fd9e18b7aee9582e8ce650b&units=metric").json()
    temp1 = res["weather"][0]["description"]
    temp2 = res["main"]["temp"]
    speak_text(f"Temperature in {city} is {format(temp2)} degrees Celsius and it is {format(temp1)}")


def chatting():
    # speak_text("...Processing...")
    user_input = listen_and_transcribe(model)
    print(f"You said: {user_input}")

    # Query Ollama API
    response = query_ollama(user_input)
    print(datetime.datetime.now().strftime("@ %H:%M"), end=', ')
    print(f"{SN}: {response}")

    # Speak Ollama's response
    print(datetime.datetime.now().strftime("@ %H:%M"), end=', ')
    speak_text(response)


# Main function to integrate all components
def main():
    try:
        greet()

        while True:
            # Listen to user input
            print(datetime.datetime.now().strftime("@ %H:%M"), end=', ')

            user_input = listen_and_transcribe(model)
            print(f"You said: {user_input}")
            # speak_text("...Processing...")

            if "hello" in user_input:
                speak_text("Hello! How are you doing?")

            if "time" in user_input:
                speak_text("It is currently " +
                       datetime.datetime.now().strftime("%H:%M"))

            if "date" in user_input:
                print(datetime.datetime.now().strftime("@ %H:%M"), end=', ')
                speak_text(f"... Today is the {today}")
                print(f"... Today is the {today}")

            if "weather" in user_input:
                weather()

            if "tell me a joke" in user_input:
                speak_text(pyjokes.get_joke())

            if "restart" in user_input:
                # sleep(2)
                speak_text("Ok ... Re-starting now...")
                sleep(2)  # 1 second delay
                os.system("python c100.py")
                exit()

            if "shut down" in user_input:
                hour = datetime.datetime.now().hour
                if (hour > 21) and (hour < 6):
                    # sleep(2)
                    speak_text(f"... Good Night {user}! Have a nice Sleep...")
                    sleep(2)
                else:
                    # sleep(2)
                    speak_text(f"Ok ... Shutting down now..")
                    sleep(2)
                quit()

            if "huh" in user_input:
                pass

            else:
                if " " in user_input:
                    speak_text(f"... Processing Request...")
                    chatting()

            # Query Ollama API - MOVED TO CHATTING FUNCTION
            # response = query_ollama(user_input)
            # print(datetime.datetime.now().strftime("@ %H:%M"), end=', ')
            # print(f"Ollama: {response}")
            #
            # # Speak Ollama's response
            # print(datetime.datetime.now().strftime("@ %H:%M"), end=', ')
            # speak_text(response)

    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
