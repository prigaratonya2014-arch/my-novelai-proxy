from fastapi import FastAPI, Response
import requests
import json

app = FastAPI()

@app.get("/generate")
def generate(prompt: str, token: str, aspect: str = "1:1"):
    sizes = {"1:1": (1024, 1024), "2:3": (832, 1216), "3:2": (1216, 832)}
    w, h = sizes.get(aspect, (1024, 1024))

    # Новый актуальный URL
    url = "https://image.novelai.net/ai/generate-image"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "accept": "image/png"
    }
    
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
            "params_version": 1
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            return Response(content=response.content, media_type="image/png")
        else:
            # Если ошибка — отдаем её как текст, чтобы ты могла её прочитать в браузере
            return Response(content=f"Status: {response.status_code} - {response.text}", media_type="text/plain")
            
    except Exception as e:
        return Response(content=f"Local Error: {str(e)}", media_type="text/plain")
