import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# This lets your frontend communicate securely with this server script across the internet
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str
    platform: str

@app.post("/download")
async def download_video(request: DownloadRequest):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            links = []
            
            if 'url' in info:
                links.append({"label": f"Download Video ({info.get('format_note', 'Best Quality')})", "url": info['url']})
            elif 'formats' in info:
                for f in info['formats']:
                    if f.get('url') and f.get('vcodec') != 'none':
                        links.append({
                            "label": f"Quality: {f.get('format_note', 'Standard')} ({f.get('ext', 'mp4')})",
                            "url": f['url']
                        })
            
            if not links:
                raise HTTPException(status_code=404, detail="Could not find playable link streams.")
                
            return {"title": info.get('title', 'Video File'), "links": links}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # This automatically reads Render's dynamic port system ($PORT) 
    # or falls back to port 8000 if you run it locally on your computer
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
