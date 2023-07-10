# Voice-Control-Assistant

I used several different models in my project
For image generation: "runwayml/stable-diffusion-v1-5"
  I found it HuggingFace models and implemented it into my project.
  I used BingAI for internet searching,I used EdgeGPT library for access Bing.
  I used AWS Text-to-Speech software to read answers (Polly).

# How model works
It prints "Waiting for a command!" and listens for a command.
It listens and saves to audio.wav, after that, we load model 'tiny' and transcribe the audio.
We print what model heard as "You said: {phrase}"
Now, we try to find any command in the audio.wav file,
If we find,program does its work,if not,it listens again.

# Commands
This is my control assistant. You can control it by some commands.
* For wake up the Bing AI, say "Hello!"
* For make Bing sleep, say "Close!"
* For let Assistant turn the volume down or up, say "Volume down/up!"
* For let Assistant mute the volume, simply say "Mute!"
* And it is my favourite command, say "Generate!" and wait for Assistant to speak. After that you can tell Assistant what you want to generate as image.It will generate and save the image as png.
