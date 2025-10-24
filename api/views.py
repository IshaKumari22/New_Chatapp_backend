# from rest_framework.views import APIView
# from rest_framework.response import Response
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch

# # Load TinyLLaMA model from Hugging Face
# MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# class GenerateView(APIView):
#     def post(self, request):
#         prompt = request.data.get("prompt", "")
#         inputs = tokenizer(prompt, return_tensors="pt")
#         outputs = model.generate(
#             **inputs,
#             max_new_tokens=100,
#             temperature=0.7,
#             do_sample=True,
#         )
#         text = tokenizer.decode(outputs[0], skip_special_tokens=True)
#         return Response({"response": text})


from rest_framework.views import APIView
from rest_framework.response import Response
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.normpath(os.path.join(BASE_DIR, "..", "TinyLlama"))

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)
if torch.cuda.is_available():
    model = model.to("cuda")

class GenerateView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt", "")

        # Format for TinyLLaMA chat models
        formatted_prompt = f"User: {prompt}\nAssistant:"

        # Tokenize and move to GPU if available
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

        # Generate response
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

        # Decode response
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Clean assistant output
        if "Assistant:" in text:
            text = text.split("Assistant:")[-1].strip()

        return Response({"response": text})
