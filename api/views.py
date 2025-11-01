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


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch, os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# model_path = os.path.normpath(os.path.join(BASE_DIR, "..", "TinyLlama"))

# tokenizer = AutoTokenizer.from_pretrained(model_path)
# model = AutoModelForCausalLM.from_pretrained(model_path)
# if torch.cuda.is_available():
#     model = model.to("cuda")

# class GenerateView(APIView):
#     def post(self, request):
#         prompt = request.data.get("prompt", "")

#         # Format for TinyLLaMA chat models
#         formatted_prompt = f"User: {prompt}\nAssistant:"

#         # Tokenize and move to GPU if available
#         inputs = tokenizer(formatted_prompt, return_tensors="pt")
#         if torch.cuda.is_available():
#             inputs = {k: v.to("cuda") for k, v in inputs.items()}

#         # Generate response
#         outputs = model.generate(
#             **inputs,
#             max_new_tokens=100,
#             do_sample=True,
#             temperature=0.7,
#             top_p=0.9,
#             pad_token_id=tokenizer.eos_token_id
#         )

#         # Decode response
#         text = tokenizer.decode(outputs[0], skip_special_tokens=True)

#         # Clean assistant output
#         if "Assistant:" in text:
#             text = text.split("Assistant:")[-1].strip()

#         return Response({"response": text})







# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# import requests,os
# from dotenv import load_dotenv

# load_dotenv()

# class GenerateView(APIView):
#     permissions_classes=[IsAuthenticated]
#     def post(self,request):
#         prompt=request.data.get("prompt","")
#         if not prompt:
#             return Response({"error":"Prompt is required."},status=400)
        
#         #cloudflare credentials
#         account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID")
#         api_token=os.getenv("CLOUDFLARE_API_TOKEN")
#         model=os.getenv("CLOUDFLARE_MODEL","@cf/meta/llama-3.2-1b-instruct")

#         url=f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
#         headers={
#             "Authorization":f"Bearer {api_token}",
#             "Content-Type":"application/json",

#         }
#         data = {"input": prompt}

#         try:
#             response = requests.post(url, headers=headers, json=data)
#             result = response.json()
#             text = result["result"]["response"]
#         except Exception as e:
#             print("⚠️ Cloudflare error:", e)
#             text = "⚠️ Cloudflare AI did not respond."

#         return Response({"response": text})


from django.http import JsonResponse
from rest_framework.views import APIView
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # 👈 this must come before reading env vars

class GenerateView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt", "")
        print("🟡 Prompt:", prompt)

        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        model = os.getenv("CLOUDFLARE_MODEL")

        print("🔹 Account ID:", account_id)
        print("🔹 Model:", model)

        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(url, json={"prompt": prompt}, headers=headers)
            print("🟢 Cloudflare status:", response.status_code)
            print("🟢 Cloudflare body:", response.text)

            data = response.json()
            if not data.get("success"):
                return JsonResponse({"response": f"⚠️ Cloudflare error: {data}"})

            result = data.get("result", {}).get("response", None)
            if not result:
                return JsonResponse({"response": "⚠️ No response text from Cloudflare."})
            
            return JsonResponse({"response": result})

        except Exception as e:
            print("🔴 Error contacting Cloudflare:", e)
            return JsonResponse({"response": f"⚠️ {str(e)}"})



# from django.http import JsonResponse
# from rest_framework.views import APIView
# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()  # Must come before reading env vars

# class GenerateView(APIView):
#     def post(self, request):
#         prompt = request.data.get("prompt", "")
#         print("🟡 Prompt:", prompt)

#         account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
#         api_token = os.getenv("CLOUDFLARE_API_TOKEN")
#         model = os.getenv("CLOUDFLARE_MODEL")

#         print("🔹 Account ID:", account_id)
#         print("🔹 Model:", model)

#         url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
#         headers = {
#             "Authorization": f"Bearer {api_token}",
#             "Content-Type": "application/json",
#         }

#         try:
#             response = requests.post(url, json={"prompt": prompt}, headers=headers)
#             print("🟢 Cloudflare status:", response.status_code)
#             print("🟢 Cloudflare body:", response.text)

#             data = response.json()
#             if not data.get("success"):
#                 return JsonResponse({"response": f"⚠️ Cloudflare error: {data}"})

#             result = data.get("result", {}).get("response", "")
#             if not result:
#                 return JsonResponse({"response": "⚠️ No response text from Cloudflare."})

#             # ✅ Limit output to 10 characters
#             short_result = result[:10]

#             return JsonResponse({"response": short_result})

#         except Exception as e:
#             print("🔴 Error contacting Cloudflare:", e)
#             return JsonResponse({"response": f"⚠️ {str(e)}"})
