# llava_image_handler.py
"""Kilo image handler that uses LLaVA 1.5‑7B to generate captions.

This module registers a handler with Kilo's command registry. Whenever an image
is attached to a chat message, the handler loads the cached LLaVA model, runs
the image through the model, and returns the generated caption as a chat
response.

Dependencies
------------
* `torch`
* `transformers`
* `accelerate`
* `bitsandbytes`
* `hf_xet`
* `llaVA`

The model is expected to be cached at
```
C:/Users/mlesn/.cache/llava
```
If you have a different cache location, adjust the `MODEL_CACHE_DIR`.

Usage
-----
Add this file to your Kilo project and ensure it is imported during
initialisation. The handler will automatically be registered.
"""

from pathlib import Path

# Import the LLaVA package
from llaVA import LLaVA

# Path to the cached model
MODEL_CACHE_DIR = Path(r"C:/Users/mlesn/.cache/llava")

# Load the model once at import time (lazy loading if desired)
_llava_model = None


def get_llava_model() -> LLaVA:
    global _llava_model
    if _llava_model is None:
        _llava_model = LLaVA.from_pretrained(str(MODEL_CACHE_DIR))
    return _llava_model


# Kilo command registry import (placeholder)


def register_image_handler(handler):
    """Placeholder registration function. Replace with actual Kilo API."""
    print(f"Registered image handler: {handler.__name__}")


# Define the handler function
async def llava_caption_handler(image_path: str) -> str:
    """Generate a caption for the given image using LLaVA.

    Parameters
    ----------
    image_path: str
        Path to the image file attached in the chat.

    Returns
    -------
    str
        The generated caption.
    """
    model = get_llava_model()
    # LLaVA expects the image path and a prompt. We use a generic prompt.
    caption = model.generate(image_path, "Describe the image")
    return caption


# Register the handler with Kilo's image handling system
register_image_handler(llava_caption_handler)

# If you want to expose the handler as a command for manual invocation:
# register_command("llava_caption", llava_caption_handler)

# End of llava_image_handler.py
