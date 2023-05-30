from authtoken import auth_token
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

model_id = "runwayml/stable-diffusion-v1-5"
device = "cuda"
pipe = StableDiffusionPipeline.from_pretrained(model_id, revision="fp16", torch_dtype=torch.float16, use_auth_token=auth_token)
pipe.to(device)

def get_last_image_number():
    try:
        with open("last_image_number.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        update_last_image_number(0)
        return 0

def update_last_image_number(number):
    with open("last_image_number.txt", "w") as file:
        file.write(str(number))

def image_Generator(phrase=""):
    last_image_number = get_last_image_number()
    new_image_number = last_image_number + 1

    with autocast(device):
        image = pipe(phrase, guidance_scale=8.5).images[0]

    filename = f"generated_image_{new_image_number}.png"
    image.save(filename)
    print(f"Image generated: {filename}")

    update_last_image_number(new_image_number)
