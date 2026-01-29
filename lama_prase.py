import re
import os
import asyncio
import httpx
from llama_cloud import AsyncLlamaCloud

client = AsyncLlamaCloud(api_key="llx-sGavUzjyBxVdbyW46wpmZ38CXS47pgcJnrnx8i8C7mC8l33o")

def is_page_screenshot(image_name: str) -> bool:
    return re.match(r"^page_(\d+)\.jpg$", image_name) is not None


async def main():
    # Upload and parse document
    file_obj = await client.files.create(
        file="./canada.pdf",
        purpose="parse"
    )

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

    # ---------- TEXT ----------
    if result.text and result.text.pages:
        print("=== TEXT ===")
        print(result.text.pages[0].text)
    else:
        print("⚠️ No text content returned")

    # ---------- TABLES ----------
    if result.items and result.items.pages:
        for page in result.items.pages:
            for item in page.items:
                if hasattr(item, "rows"):
                    print(
                        f"Table found on page {page.page_number} "
                        f"with {len(item.rows)} rows"
                    )
    else:
        print("⚠️ No structured items returned")

    # ---------- IMAGES ----------
    if result.images_content_metadata:
        for image in result.images_content_metadata.images:
            if image.presigned_url and is_page_screenshot(image.filename):
                print(f"Downloading {image.filename}")

                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get(image.presigned_url)

                with open(image.filename, "wb") as img_file:
                    img_file.write(response.content)
    else:
        print("⚠️ No images returned")


if __name__ == "__main__":
    asyncio.run(main())