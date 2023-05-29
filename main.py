import asyncio
import re
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import speech_recognition as sr
import whisper
from EdgeGPT import Chatbot, ConversationStyle
import boto3
import pydub
from pydub import playback

# Commands
BING_WAKE = "hello"
BING_SLEEP = "close"
VOLUME_UP = "volume up"
VOLUME_DOWN = "volume down"

recognizer = sr.Recognizer()

# Get default audio device using PyCAW
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

def is_volume_up(phrase):
    return VOLUME_UP in phrase.lower()

def is_volume_down(phrase):
    return VOLUME_DOWN in phrase.lower()

def get_wake_word(phrase):
    return BING_WAKE if BING_WAKE in phrase.lower() else None

def get_sleep_word(phrase):
    return BING_SLEEP if BING_SLEEP in phrase.lower() else None

def synthesize_speech(text, output_filename):
    polly = boto3.client('polly', region_name='us-east-1')
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Ruth',
        Engine='neural'
    )
    with open(output_filename, 'wb') as f:
        f.write(response['AudioStream'].read())

def play_audio(file):
    sound = pydub.AudioSegment.from_file(file, format="mp3")
    playback.play(sound)

async def main():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Waiting for wake word")
            audio = recognizer.listen(source)

            while True:
                try:
                    with open("audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    model = whisper.load_model("tiny")
                    result = model.transcribe("audio.wav")
                    phrase = result["text"]
                    print(f"You said: {phrase}")

                    wake_word = get_wake_word(phrase)
                    sleep_word = get_sleep_word(phrase)
                    volume_up = is_volume_up(phrase)
                    volume_down = is_volume_down(phrase)

                # Detect commands
                    if wake_word is not None:
                        print("Wake word detected!")
                        break
                    elif sleep_word is not None:
                        print("Sleep word detected! Exiting...")
                        return
                    elif volume_up is not None:
                        print("Volume up!")
                        current_volume = volume.GetMasterVolumeLevel()
                        volume.SetMasterVolumeLevel(current_volume + 6.0, None)
                    elif volume_down is not None:
                        print("Volume down!")
                        current_volume = volume.GetMasterVolumeLevel()
                        volume.SetMasterVolumeLevel(current_volume - 6.0, None)
                    else:
                        print("Wake word not detected!")
                        audio = recognizer.listen(source, timeout=5)
                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue

        bot = Chatbot()
        while True:
            with sr.Microphone() as source:
                print("Speak a prompt...")
                audio = recognizer.listen(source)

                try:
                    with open("audio_prompt.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    model = whisper.load_model("base")
                    result = model.transcribe("audio_prompt.wav")
                    user_input = result["text"]
                    print(f"You said: {user_input}")
                    if sleep_word == BING_SLEEP:
                        await bot.close()
                        break
                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue


                if wake_word == BING_WAKE:
                    response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.creative)

                    for message in response["item"]["messages"]:
                        if message["author"] == "bot":
                            bot_response = message["text"]

                    # remove unwanted punctuations
                    bot_response = re.sub('\[\^\d+\^\]', '', bot_response)

                print("Bot's response: ", bot_response)
                synthesize_speech(bot_response, 'response.mp3')
                play_audio('response.mp3')

if __name__ == "__main__":
    asyncio.run(main())