import io
import os
import cv2
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from pymongo import MongoClient
from dotenv import load_dotenv
import openai
import numpy as np
import uvicorn

print("Starting FastAPI app...")

print("Imports successful")

load_dotenv()
print("Environment variables loaded")

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key:
    print("OpenAI API key loaded")
else:
    print("OpenAI API key not found")

client = MongoClient("mongodb+srv://tirthofficials:kP1j4r5MgI7egZit@cluster0.emajywl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.visually_impaired_app
collection = db.descriptions
print("Connected to MongoDB")

def process_image(image: Image.Image) -> str:
    # Convert image to numpy array and then to grayscale
    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    # Here we can add more complex image processing if needed
    # For simplicity, let's just return a placeholder description
    description = "a grayscale image"

    return description

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    print("Received request for /analyze")
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    print("Image loaded")

    # Process the image
    description = process_image(image)
    print("Image processed: ", description)

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Describe the following image: {description}",
        max_tokens=50
    )
    print("OpenAI response received")

    final_description = response.choices[0].text.strip()
    
    collection.insert_one({"description": final_description})
    print("Description inserted into MongoDB")

    return {"description": final_description}

if __name__ == "__main__":
    print("Running Uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
