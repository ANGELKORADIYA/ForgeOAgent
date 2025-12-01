from .content_fetcher import test_fetch_content_images

# Example usage
API_KEYS = ["AIzaSyD3IKFXcKGbh8oX6yWz3zkk41iefTMf5z8"]
title = "The Beauty of Nature"
description = "Exploring the wonders of the natural world through stunning imagery."

result = test_fetch_content_images(
    title=title,
    description=description,
    api_keys=API_KEYS,
    convert_to_base64=True,
)
import json
print(json.dumps(result, indent=2))
with open("output.json", "w") as f:
    json.dump(result, f, indent=2)