from fastapi import FastAPI, Response
import requests

app = FastAPI()

@app.get("/generate")
def generate(prompt: str, token: str, aspect: str = "1:1"):
    # Настройки размеров под NovelAI
    sizes = {"1:1": (1024, 1024), "2:3": (832, 1216), "3:2": (1216, 832)}
    w, h = sizes.get(aspect, (1024, 1024))

    # Ссылка самого NovelAI (тот самый POST запрос)
    url = "https://api.novelai.net/ai/generate-image"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "input": prompt,
        "model": "nai-diffusion-3",
        "parameters": {"width": w, "height": h, "steps": 28, "sampler": "k_euler_ancestral"}
    }

    # Делаем магию
    response = requests.post(url, json=data, headers=headers)
    
    # Отдаем картинку обратно в Tavo
    return Response(content=response.content, media_type="image/png")
