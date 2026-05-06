from fastapi import FastAPI, Response
import requests

app = FastAPI()

@app.get("/generate")
def generate(prompt: str, token: str, aspect: str = "1:1"):
    sizes = {"1:1": (1024, 1024), "2:3": (832, 1216), "3:2": (1216, 832)}
    w, h = sizes.get(aspect, (1024, 1024))

    url = "https://image.novelai.net/ai/generate-image"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
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
            "n_samples": 1,
            "uc": "lowres, bad quality",
            "params_version": 1
        }
    }

    try:
        # Ставим stream=True, чтобы выкачать чистый файл
        response = requests.post(url, json=payload, headers=headers, timeout=60, stream=True)
        
        if response.status_code == 200:
            # Возвращаем тело ответа как поток байтов
            return Response(content=response.raw.read(), media_type="image/png")
        else:
            return Response(content=f"NAI Error: {response.status_code} - {response.text}", media_type="text/plain")
            
    except Exception as e:
        return Response(content=f"System Error: {str(e)}", media_type="text/plain")
