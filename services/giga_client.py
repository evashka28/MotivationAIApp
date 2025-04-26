import base64
import uuid
import requests
import urllib3
from core.conf import CLIENT_ID, CLIENT_SECRET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GigaChatClient:
    def __init__(self):
        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError("Both CLIENT_ID and CLIENT_SECRET are required in environment variables")
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
            "RqUID": str(uuid.uuid4())
        }

        data = {
            "scope": "GIGACHAT_API_PERS"
        }

        response = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers=headers,
            data=data,
            verify=False  # ← отключаем проверку сертификата
        )

        print("Status code:", response.status_code)
        print("Response text:", response.text)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise RuntimeError(f"Ошибка при получении токена: {e}\nОтвет сервера: {response.text}")

        return response.json()["access_token"]

    def generate_response(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system",
                 "content": "Ты — мотивационный помощник, который оценивает привычки пользователя и даёт советы."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }

        response = requests.post(self.url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    def generate_alternative_habits(self, name: str, description: str) -> list[str]:
        prompt = (
            f"Привычка называется: '{name}'.\n"
            f"Описание: {description}\n\n"
            "Предложи три более простые альтернативные привычки, "
            "но из той же области (например, если это физическая активность — пусть останется физическая активность, но проще). В новых привычках не должно быть сравнения старой, просто их краткие описания.\n"
            "Ответ верни списком, без лишнего текста:\n"
            "1. Альтернатива 1\n"
            "2. Альтернатива 2\n"
            "3. Альтернатива 3"
        )
        print("PROMPT:", prompt)
        response = self.generate_response(prompt)
        print("RESPONSE FROM GIGACHAT:", repr(response))
        return self._parse_numbered_list(response)

    def _parse_numbered_list(self, text: str) -> list[str]:
        import re
        return re.findall(r"\d+\.\s*(.+)", text.strip())
