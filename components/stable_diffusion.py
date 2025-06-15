from io import BytesIO
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, StreamingResponse
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, StableDiffusionPipeline
from fastapi.staticfiles import StaticFiles
import torch
from PIL import Image
import cv2
import numpy as np
import uuid
import os
from typing import Optional

app = FastAPI()

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

# ControlNet setup
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-scribble", torch_dtype=dtype
).to(device)

controlnet_pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=dtype
).to(device)

# Text-to-Image pipeline setup
try:
    # Try primary model first
    text2img_pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=dtype,
        safety_checker=None,
        requires_safety_checker=False
    ).to(device)
    print("Text-to-image pipeline loaded successfully with SD 1.5")
except Exception as e:
    print(f"Error loading SD 1.5: {e}")
    try:
        # Fallback to alternative model
        text2img_pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False
        ).to(device)
        print("Text-to-image pipeline loaded successfully with SD 1.4")
    except Exception as e2:
        print(f"Error loading fallback model: {e2}")
        text2img_pipe = None

# Only enable xformers if GPU is available
if device == "cuda":
    try:
        controlnet_pipe.enable_xformers_memory_efficient_attention()
        if text2img_pipe:
            text2img_pipe.enable_xformers_memory_efficient_attention()
        print("XFormers memory optimization enabled")
    except Exception as e:
        print(f"XFormers not available: {e}")
else:
    print(f"Using device: {device}")

def preprocess_scribble(image: Image.Image) -> Image.Image:
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2
    )
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(edges_rgb)
