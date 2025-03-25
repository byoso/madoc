# #! /usr/bin/env python3

# import base64, re
# import mimetypes
# from typing import Optional

# from madoc.silly_engine.text_tools import c
# from madoc.silly_engine.logger import Logger

# logger = Logger("base64 converter")
# image_pattern = r"!\[(.*?)\]\((.*?)\)"


# def encode_image_to_base64(image_path: str) -> Optional[str]:
#     """Encodes an image file to a base64 string with the correct MIME type."""
#     mime_type, _ = mimetypes.guess_type(image_path.strip())
#     if not mime_type:
#         mime_type = "application/octet-stream"  # Default if type is unknown

#     try:
#         with open(image_path.strip(), "rb") as image_file:
#             base64_string = base64.b64encode(image_file.read()).decode("utf-8")
#             return f"data:{mime_type};base64,{base64_string}"
#     except FileNotFoundError:
#         logger.warning(f"the file '{image_path}' was not found, it was then left as it is (not converted to base64).")
#         return None  # Return None if file is not found

# def replace_images_with_base64(text: str) -> str:
#     """Replaces all image file paths with their Base64 encoding, but keeps original if not found."""
#     pattern: str = r"!\[(.*?)\]\((.*?)\)"  # Matches ![image_name](image_file)

#     def replacer(match: re.Match) -> str:
#         image_name: str
#         image_file: str
#         image_name, image_file = match.groups()

#         base64_string: Optional[str] = encode_image_to_base64(image_file)
#         if base64_string:
#             return f"![{image_name}]({base64_string})"
#         else:
#             return match.group(0)  # Keep the original text if the file is not found

#     return re.sub(pattern, replacer, text)


import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re
import base64
import mimetypes
import requests
from typing import Optional


def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Encodes an image file (local or web) to a Base64 string with the correct MIME type."""
    try:
        if image_path.startswith(("http://", "https://")):
            # Download the image from the web
            response = requests.get(image_path, timeout=5)
            if response.status_code == 200:
                mime_type = response.headers.get("Content-Type", "application/octet-stream")
                base64_string = base64.b64encode(response.content).decode("utf-8")
                return f"data:{mime_type};base64,{base64_string}"
            else:
                return None  # Keep the original URL if the download fails
        else:
            # Handle local file
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            with open(image_path, "rb") as image_file:
                base64_string = base64.b64encode(image_file.read()).decode("utf-8")
                return f"data:{mime_type};base64,{base64_string}"
    except (FileNotFoundError, requests.RequestException):
        return None  # Return None if file not found or request fails

class ImageBase64Processor(Preprocessor):
    """Custom Preprocessor to replace image paths with Base64, but ignore code blocks."""

    def __init__(self, md):
        super().__init__(md)
        self.in_code_block = False
        self.image_md_pattern = re.compile(r"!\s*\[\s*(.*?)\s*\]\s*\(\s*(.*?)\s*\)")  # Matches ![alt](image)
        self.image_html_pattern = re.compile(r'<img\s+[^>]*?\bsrc\s*=\s*["\'](.*?)["\'][^>]*?/?>', re.IGNORECASE)  # Matches <img src="image">

    def run(self, lines):
        processed_lines = []

        for line in lines:
            # Toggle in_code_block when encountering ```
            if line.strip().startswith(("```", "~~~")):
                self.in_code_block = not self.in_code_block
                processed_lines.append(line)
                continue

            if not self.in_code_block:
                # Replace Markdown images
                line = self.image_md_pattern.sub(self.replace_md_image, line)

                # Replace HTML images
                line = self.image_html_pattern.sub(self.replace_html_image, line)

            processed_lines.append(line)

        return processed_lines

    def replace_md_image(self, match):
        """Replaces Markdown image paths with Base64."""
        alt_text, image_path = match.groups()
        base64_str = encode_image_to_base64(image_path)
        return f"![{alt_text}]({base64_str})" if base64_str else match.group(0)

    def replace_html_image(self, match):
        """Replaces HTML image paths with Base64."""
        image_path = match.group(1)
        base64_str = encode_image_to_base64(image_path)
        return match.group(0).replace(image_path, base64_str) if base64_str else match.group(0)

class ImageBase64Extension(Extension):
    """Markdown extension to replace images with Base64 outside of code blocks."""

    def extendMarkdown(self, md):
        md.preprocessors.register(ImageBase64Processor(md), 'image_base64_processor', 25)

def convert_images_to_base64(markdown_text: str) -> str:
    """Replaces Markdown and HTML images with Base64 encoding, but ignores images inside code blocks."""
    md = markdown.Markdown(extensions=[ImageBase64Extension()])
    return md.convert(markdown_text)

# Example Markdown with local & web images
markdown_text = """
# Example Markdown

Local image (should convert):
![Local](images/picture.jpg)

Web image (should convert if downloadable):
![Web Image](https://example.com/image.png)

HTML image from the web:
<img src="https://example.com/photo.jpg" alt="Photo">
"""