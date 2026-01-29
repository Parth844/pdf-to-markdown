import re
import os
import httpx
from llama_cloud import AsyncLlamaCloud

import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncLlamaCloud(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY")
)
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

if not os.getenv("LLAMA_CLOUD_API_KEY"):
    raise RuntimeError("LLAMA_CLOUD_API_KEY not set")

def is_page_screenshot(image_name: str) -> bool:
    return re.match(r"^page_(\d+)\.jpg$", image_name) is not None


async def parse_pdf(file_path: str):
    """
    Parses a PDF using Llama Cloud and returns:
    - markdown text
    - list of extracted image filenames
    """

    # Upload PDF
    file_obj = await client.files.create(
        file=file_path,
        purpose="parse"
    )

    # Parse document
    result = await client.parsing.parse(
        file_id=file_obj.id,
        tier="agentic",
        version="latest",
        expand=[
            "text",
            "items",
            "images_content_metadata"
        ],
    )

    markdown = ""
    images = []

    # ---------- TEXT ----------
    if result.text and result.text.pages:
        for page in result.text.pages:
            markdown += page.text + "\n\n"

    # ---------- IMAGES ----------
    if result.images_content_metadata:
        for image in result.images_content_metadata.images:
            if image.presigned_url and is_page_screenshot(image.filename):
                image_path = os.path.join(OUTPUT_DIR, image.filename)

                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get(image.presigned_url)

                with open(image_path, "wb") as img_file:
                    img_file.write(response.content)

                images.append(image.filename)

    return markdown.strip(), images