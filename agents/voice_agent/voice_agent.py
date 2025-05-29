from fastapi import FastAPI, File, UploadFile, Form
from transformers import pipeline
from TTS.api import TTS
import tempfile
from fastapi.responses import FileResponse, JSONResponse
import os

app = FastAPI()

# STT Configuration
stt_model = pipeline("automatic-speech-recognition", model="openai/whisper-base")

# TTS Configuration
tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", progress_bar=False)

@app.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = stt_model(tmp_path)
        os.remove(tmp_path)
        return {"transcript": result["text"]}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/tts")
async def text_to_speech(text: str = Form(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            audio_path = tmp_out.name

        tts.tts_to_file(text=text, file_path=audio_path)
        return FileResponse(audio_path, media_type="audio/wav", filename="speech.wav")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
