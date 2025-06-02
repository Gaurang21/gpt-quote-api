from flask import Flask, request, jsonify
from openai import OpenAI
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

app = Flask(__name__)


@app.route('/')
def home():
    return jsonify({
        "message": "Motivational Quote Generator API",
        "endpoints": {
            "POST /generate": "Generate a motivational quote with image",
            "GET /generate": "Generate a motivational quote with image (browser friendly)"
        }
    })


@app.route('/generate', methods=['GET', 'POST'])
def generate_quote_image():
    # Step 1: Generate quote using OpenAI
    prompt = "Generate a short, one liner, bold motivational alpha male quote."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    quote = response.choices[0].message.content.strip()

    # Step 2: Create an image with the quote
    img = Image.new('RGB', (1080, 1920), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except OSError:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), quote, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1080 - text_width) / 2
    y = (1920 - text_height) / 2
    draw.text((x, y), quote, font=font, fill=(255, 255, 255))

    # Step 3: Convert image to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Step 4: Build and return JSON
    return jsonify({
        "quote_text": quote,
        "image_description": "Black background with bold white text",
        "filename": quote.lower().replace(" ", "-") + ".png",
        "image_base64": f"data:image/png;base64,{img_base64}"
    })
