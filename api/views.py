

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


