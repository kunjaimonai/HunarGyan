import components.local_sarvam as local_sarvam
from fastapi import FastAPI, Form, HTTPException
import json
from PIL import Image
from fastapi.responses import Response
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from faster_whisper import WhisperModel
import tempfile
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import components.pdf_module as pdf_module
import uuid
from typing import Optional, Union, Dict, List
from io import BytesIO
#import components.stable_diffusion
#from components.stable_diffusion import preprocess_scribble, controlnet_pipe, text2img_pipe

class HelpRequest(BaseModel):
    inputMessage: str

class DocuRequest(BaseModel):
    username: str
    steps: Union[Dict[str, str], List[str]]

model_size = "medium"
model = WhisperModel("Systran/faster-whisper-medium", compute_type="int8", local_files_only=True)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def increase_document(): 
    with open("totals.json", "r") as f:
        data = json.load(f)

    data["crafts"] += 1

    with open("totals.json", "w") as f:
        json.dump(data, f)

@app.post('/document-text')
async def document_text(request: DocuRequest):
    try:
        print(f"Received request: username={request.username}, steps type={type(request.steps)}")
    
        username = "HunarGyan"
        steps_data = request.steps

        steps_text = '\n'.join(steps_data)

        try:
            generated_content = local_sarvam.generate_document(username, steps_text)
            print(f"Generated content length: {len(generated_content) if generated_content else 0}")
        except Exception as e:
            print(f"Error in generate_document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating document: {str(e)}")

        try:
            pdf_bytes = pdf_module.convert_markdown_to_pdf(
                generated_content, 
                document_title=f"{username}_craft_documentation"
            )
            print(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        except Exception as e:
            print(f"Error in convert_markdown_to_pdf: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
        
        # Return proper FastAPI Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={username}_craft_documentation.pdf",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error in document_text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class MarkRequest(BaseModel):
    steps: str

@app.post('/marketingcontent')
def marketing_content(request: MarkRequest):
    prompt = request.steps
    with open("totals.json", "r") as f:
        data = json.load(f)

    data["marketing"] += 1

    with open("totals.json", "w") as f:
        json.dump(data, f)

    # Do the sarvam.ai stuff
    e = local_sarvam.ask(prompt)
    print(e)
    return {
        "result": e  # Changed from "message" to "result"
    }


@app.get('/total-crafts')
def total_crafts():
    with open("totals.json", "r") as f:
        data = json.load(f)
    return {
        "message": data['crafts']
    }

@app.get('/total-market')
def total_market():
    with open("totals.json", "r") as f:
        data = json.load(f)
    return {
        "message": data['marketing']
    }

@app.get('/total-ideas')
def total_ideas():
    with open("totals.json", "r") as f:
        data = json.load(f)
    return {
        "message": data['design']
    }

@app.post('/help')
def help(request: HelpRequest):
    e= local_sarvam.generate_help(request.inputMessage)
    return e


@app.post("/document-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        segments, _ = model.transcribe(tmp_path, language=None, beam_size=5)
        result = " ".join([seg.text for seg in segments])
        return JSONResponse({"transcription": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        os.remove(tmp_path)


@app.post("/generate-controlnet/")
async def generate_controlnet_image(
    file: UploadFile = File(...),
    prompt: str = Form("detailed artistic sketch"),
    negative_prompt: Optional[str] = Form(""),
    num_inference_steps: int = Form(30),
    guidance_scale: float = Form(7.5)
):
    """Generate image from sketch using ControlNet with custom parameters"""
    contents = await file.read()
    sketch = Image.open(BytesIO(contents)).convert("RGB")
    processed = preprocess_scribble(sketch)

    # Generate with ControlNet
    result = controlnet_pipe(
        prompt=prompt,
        negative_prompt=negative_prompt if negative_prompt else None,
        image=processed,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale
    )
    out_img = result.images[0]

    # Convert to response
    buf = BytesIO()
    out_img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.post("/generate-text2img/")
async def generate_text_to_image(
    prompt: str = Form(...),
    negative_prompt: Optional[str] = Form(""),
    width: int = Form(512),
    height: int = Form(512),
    num_inference_steps: int = Form(30),
    guidance_scale: float = Form(7.5),
    num_images: int = Form(1)
):
    """Generate image from text prompt only"""
    if text2img_pipe is None:
        return {"error": "Text-to-image pipeline not available. Please check model loading."}
    
    try:
        # Generate with text-to-image pipeline
        result = text2img_pipe(
            prompt=prompt,
            negative_prompt=negative_prompt if negative_prompt else None,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            num_images_per_prompt=num_images
        )
        
        if num_images == 1:
            # Return single image
            out_img = result.images[0]
            buf = BytesIO()
            out_img.save(buf, format="PNG")
            buf.seek(0)
            return StreamingResponse(buf, media_type="image/png")
        else:
            # Save multiple images and return file paths
            os.makedirs("outputs", exist_ok=True)
            file_paths = []
            for i, img in enumerate(result.images):
                out_path = f"outputs/{uuid.uuid4().hex}_text2img_{i}.png"
                img.save(out_path)
                file_paths.append(out_path)
            
            return {"message": f"Generated {num_images} images", "file_paths": file_paths}
    
    except Exception as e:
        return {"error": f"Generation failed: {str(e)}"}