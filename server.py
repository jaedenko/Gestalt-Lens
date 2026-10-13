import os
import base64
import json

from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)


PRINCIPLES = [
    "Proximity",
    "Similarity",
    "Continuity",
    "Closure",
    "Figure-Ground",
    "Common Fate",
    "Common Region",
    "Connectedness",
    "Symmetry/Order"
]


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():


    if "image" not in request.files:
        return jsonify({
            "error": "No image was uploaded."
        }), 400

    image = request.files["image"]
    raw = image.read()

    if not raw:
        return jsonify({
            "error": "The image is empty."
        }), 400

    mime = image.mimetype or "image/jpeg"
    encoded = base64.b64encode(raw).decode("utf-8")

    prompt = f"""
Analyze this image for Gestalt principles in visual design.

Choose ONE primary principle from exactly this list:

{", ".join(PRINCIPLES)}

Do NOT automatically choose Proximity.
Actually inspect the image and determine which principle is most strongly
demonstrated by the visible composition.

If multiple principles apply, choose the strongest one as the primary
principle and list up to two alternatives.

Return ONLY valid JSON:

{{
    "principle": "Proximity",
    "reason": "A short explanation of why the image demonstrates this principle.",
    "confidence": 85,
    "other": ["Similarity", "Common Region"]
}}

Rules:
- "principle" must be one of the listed principles.
- "reason" must be one short, student-friendly sentence.
- "confidence" must be an integer from 0 to 100.
- "other" can contain zero, one, or two alternatives.
- Do not include Markdown.
- Do not include anything outside the JSON.
"""

    try:
        response = client.responses.create(
            model="llmprism-ml/bonsai-27b",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime};base64,{encoded}"
                        }
                    ]
                }
            ]
        )

        text = response.output_text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        data = json.loads(text)

        if data["principle"] not in PRINCIPLES:
            raise ValueError("Invalid Gestalt principle returned.")

        data["confidence"] = max(
            0,
            min(100, int(data["confidence"]))
        )

        data["other"] = [
            x for x in data.get("other", [])
            if x in PRINCIPLES
            and x != data["principle"]
        ][:2]

        return jsonify(data)

    except Exception as e:
        print("ERROR:", e)

        error_text = str(e).lower()

        if (
            "connection refused" in error_text
            or "connecterror" in error_text
            or "connection error" in error_text
            or "localhost" in error_text
        ):
            return jsonify({
                "error": (
                    "Gestalt Lens can't connect to LM Studio.\n\n"
                    "Please open LM Studio, load Bonsai 27B, "
                    "and make sure the Local Server is running."
                )
            }), 503

        return jsonify({
            "error": "Gestalt Lens encountered an unexpected error: " + str(e)
        }), 500


if __name__ == "__main__":
    print()
    print("================================")
    print("       GESTALT LENS")
    print("================================")
    print()
    print("Open this in your browser:")
    print("http://localhost:3000")
    print()

    app.run(
        host="127.0.0.1",
        port=3000,
        debug=False
    )