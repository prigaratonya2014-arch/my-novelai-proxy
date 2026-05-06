from fastapi import FastAPI, Response
import requests
import json

app = FastAPI()

@app.get("/generate")
def generate(prompt: str, token: str, aspect: str = "1:1"):
    # Определяем размеры
    sizes = {"1:1": (1024, 1024), "2:3": (832, 1216), "3:2": (1216, 832)}
    w, h = sizes.get(aspect, (1024, 1024))

    url = "https://api.novelai.net/ai/generate-image"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Формируем тело запроса именно так, как хочет NovelAI
    payload = {
        "input": prompt,
        "model": "nai-diffusion-3",
        "action": "generate",
        "parameters": {
            "width": w,
            "height": h,
            "scale": 5,
            "sampler": "k_euler_ancestral",
            "steps": 28,
            "seed": 0,
            "n_samples": 1,
            "ucPreset": 0,
            "uc": "lowres, {bad}, error, missing, extra, blurry, distorted, low quality, normal quality, worst quality, jpeg artifacts, multi",
            "add_bos_token": True,
            "sm": False,
            "sm_dyn": False,
            "dynamic_thresholding": False,
            "params_version": 1
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    # Если NovelAI вернул ошибку, мы отдадим её текст вместо картинки, чтобы понять, что не так
    if response.status_code != 200:
        return Response(content=f"Error from NAI: {response.text}", media_type="text/plain")

    return Response(content=response.content, media_type="image/png")
