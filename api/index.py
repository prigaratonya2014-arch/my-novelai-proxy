import requests
import io
import zipfile
import hashlib
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_path = urlparse(self.path).query
        query = parse_qs(query_path)
        prompt = query.get('prompt', [''])[0]
        token = query.get('token', [''])[0]
        aspect = query.get('aspect', ['1:1'])[0]

        if not prompt or not token:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing prompt or token")
            return

        etag = hashlib.md5(query_path.encode()).hexdigest()
        if self.headers.get('If-None-Match') == etag:
            self.send_response(304)
            self.end_headers()
            return

        sizes = {"1:1": (1024, 1024), "2:3": (832, 1216), "3:2": (1216, 832)}
        w, h = sizes.get(aspect, (1024, 1024))
        
        url = "https://image.novelai.net/ai/generate-image"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "input": prompt,
            "model": "nai-diffusion-3",
            "action": "generate",
            "parameters": {
                "width": w, "height": h, "scale": 5,
                "sampler": "k_euler_ancestral", "steps": 28,
                "n_samples": 1, 
                "uc": "lowres, {bad anatomy}, {disfigured}, {deformed}, {mutated}, text, error, blurry",
                "sm": True, 
                "sm_dyn": True,
                "params_version": 1
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                    file_name = zip_file.namelist()[0]
                    img_data = zip_file.read(file_name)
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.send_header('ETag', etag)
                    self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
                    self.end_headers()
                    self.wfile.write(img_data)
            else:
                self.send_response(response.status_code)
                self.end_headers()
                self.wfile.write(f"NAI Error: {response.text}".encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
