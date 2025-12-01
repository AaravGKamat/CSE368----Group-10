
import base64
import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]


client = Mistral(api_key=api_key)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


image_path1 = "CSE368_Project/app_files/image.png"
base64_image1 = encode_image(image_path1)

image_path2 = "CSE368_Project/app_files/image2.jpg"
base64_image2 = encode_image(image_path2)

image_path3 = "CSE368_Project/app_files/image3.png"
base64_image3 = encode_image(image_path3)

image_path4 = "CSE368_Project/app_files/image4.jpg"
base64_image4 = encode_image(image_path4)

# ocr_response_1 = client.ocr.process(
#     model="mistral-ocr-latest",
#     document={
#         "type": "image_url",
#         "image_url": f"data:image/png;base64,{base64_image1}"
#     },
#     include_image_base64=True
# )

# ocr_response_2 = client.ocr.process(
#     model="mistral-ocr-latest",
#     document={
#         "type": "image_url",
#         "image_url": f"data:image/jpg;base64,{base64_image2}"
#     },
#     include_image_base64=True
# )

# ocr_response_3 = client.ocr.process(
#     model="mistral-ocr-latest",
#     document={
#         "type": "image_url",
#         "image_url": f"data:image/png;base64,{base64_image3}"
#     },
#     include_image_base64=True
# )

ocr_response_4 = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": f"data:image/jpg;base64,{base64_image4}"
    },
    include_image_base64=True
)


# print(ocr_response_1)
# print(ocr_response_2)
# print(ocr_response_3)
print(ocr_response_4)
