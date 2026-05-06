from fastapi import FastAPI, Response
import requests
import io
import zipfile

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
            "width": w, "height": h, "scale": 5,
            "sampler": "k_euler_ancestral", "steps": 28,
            "n_samples": 1, "uc": "lowres, bad quality"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            # NovelAI присылает ZIP. Распаковываем его в памяти.
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # Берем первый файл из архива (это и есть наша картинка)
                file_name = zip_file.namelist()[0]
                with zip_file.open(file_name) as img_file:
                    return Response(content=img_file.read(), media_type="image/png")
        else:
            return Response(content=f"NAI Error: {response.status_code} - {response.text}", media_type="text/plain")
            
    except Exception as e:
        return Response(content=f"Extraction Error: {str(e)}", media_type="text/plain")
