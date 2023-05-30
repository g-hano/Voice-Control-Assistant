import asyncio
import re
import speech_recognition as sr
import whisper
from EdgeGPT import Chatbot, ConversationStyle
import boto3
import pydub
from pydub import playback
import pyautogui

from imageGenerator import image_Generator as ig

# Commands
BING_WAKE = "hello"
BING_SLEEP = "close"
VOLUME_UP = "volume up"
VOLUME_DOWN = "volume down"
VOLUME_MUTE = "mute"
GENERATE = "generate"

recognizer = sr.Recognizer()


def is_generate(phrase):
    if GENERATE in phrase.lower():
        return True
    else:
        return False


def volume_mute_action():
    pyautogui.press("volumedown", presses=50)


def is_volume_mute(phrase):
    if VOLUME_MUTE in phrase.lower():
        return True
    else:
        return False


def is_volume_up(phrase):
    if VOLUME_UP in phrase.lower():
        return True
    else:
        return False


def volume_up_action():
    pyautogui.press("volumeup", presses=10)


def is_volume_down(phrase):
    if VOLUME_DOWN in phrase.lower():
        return True
    else:
        return False


def volume_down_action():
    pyautogui.press("volumedown", presses=10)


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
    bot = Chatbot()
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Waiting for a command!")
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
                    volume_mute = is_volume_mute(phrase)
                    generate = is_generate(phrase)
                    
                    # Detect commands
                    if wake_word is not None:
                        print("Wake word detected!")
                        while True:
                            with sr.Microphone() as source:
                                print("Speak a prompt...")
                                audio = recognizer.listen(source)

                                try:
                                    with open("audio_prompt.wav", "wb") as f:
                                        f.write(audio.get_wav_data())
                                    model = whisper.load_model("base")
                                    result = model.transcribe("audio_prompt.wav")
                                    user_said = result["text"]
                                    print(f"You said: {user_said}")
                                    if sleep_word == BING_SLEEP:
                                        await bot.close()
                                        break
                                except Exception as e:
                                    print("Error transcribing audio: {0}".format(e))
                                    continue
                                response = await bot.ask(prompt=user_said,
                                                         conversation_style=ConversationStyle.creative)
                                for message in response["item"]["messages"]:
                                    if message["author"] == "bot":
                                        bot_response = message["text"]
                                # remove unwanted punctuations
                                bot_response = re.sub('\[\^\d+\^\]', '', bot_response)
                                print("Bot's response: ", bot_response)
                                synthesize_speech(bot_response, 'response.mp3')
                                play_audio('response.mp3')

                    elif sleep_word is not None:
                        system_message = "Sleep word detected! Exiting..."
                        synthesize_speech(system_message, 'response.mp3')
                        play_audio('response.mp3')
                        return  # in this case I used 'return' because we need to exit the code

                    elif volume_up:
                        system_message = "Volume up!"
                        synthesize_speech(system_message, 'response.mp3')
                        play_audio('response.mp3')
                        volume_up_action()
                        break

                    elif volume_down:
                        system_message = "Volume down!"
                        synthesize_speech(system_message, 'response.mp3')
                        play_audio('response.mp3')
                        volume_down_action()
                        break

                    elif volume_mute:
                        system_message = "Mute!"
                        synthesize_speech(system_message, 'response.mp3')
                        play_audio('response.mp3')
                        volume_mute_action()
                        break

                    elif generate:
                        system_message = "Listening for image idea!"
                        synthesize_speech(system_message, 'response.mp3')
                        play_audio('response.mp3')

                        audio = recognizer.listen(source)

                        try:
                            with open("audio_prompt.wav", "wb") as f:
                                f.write(audio.get_wav_data())
                                idea = model.transcribe("audio_prompt.wav")
                                user_said = idea["text"]
                                print(f"You said: {user_said}")
                                ig(idea)
                                system_message = "Image is generating, please wait a second!"
                                synthesize_speech(system_message, 'response.mp3')
                                play_audio('response.mp3')

                        except Exception as e:
                            print("Error transcribing audio: {0}".format(e))
                            continue

                        system_message = "Image is generated and saved, you can check it out!"
                        synthesize_speech(system_message, 'response.mp3')
                        play_audio('response.mp3')
                        break

                    else:
                        print("Command not detected!")
                        audio = recognizer.listen(source, timeout=5)

                except Exception as e:
                    print("Error transcribing audio: {0}".format(e))
                    continue


if __name__ == "__main__":
    asyncio.run(main())
