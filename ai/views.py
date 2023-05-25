from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import torch
import clip
from PIL import Image
import numpy as np
from ai.serializers import ImageSerializer


# Create your views here.
class Imageclip(APIView):
    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            img_root = serializer.validated_data['image']

            ## 분류를 하는 모델

            ingredients = ["a carrot", "a rice", "a tomato", "a onion", "a eggs", "a meat", "milk", "garlic","mushroom","apple"]

            device = "cuda" if torch.cuda.is_available() else "cpu"
            model, preprocess = clip.load("ViT-B/32", device=device)

            image = preprocess(Image.open(img_root)).unsqueeze(0).to(device)
            text = clip.tokenize(ingredients).to(device)

            with torch.no_grad():
                image_features = model.encode_image(image)
                text_features = model.encode_text(text)
                
                logits_per_image, logits_per_text = model(image, text)
                probs = logits_per_image.softmax(dim=-1).cpu().numpy()

            print("Label probs:", probs)  # prints: [[0.9927937  0.00421068 0.00299572]]

            formatted_probs = np.round(probs, 2)
            # print(formatted_probs)

            max_index = np.argmax(probs)
            target_ingredient = ingredients[max_index]
            print(target_ingredient)
            return Response({"name":target_ingredient})
        else:
            return Response(serializer.errors, status=400)

