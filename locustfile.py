import random
from locust import task, between, HttpUser
import json
from genUser import gen, emails

post_session_called = False

BEARER_TOKEN = 'Bearer token here'  # Add your Bearer token here

sessionIds = []  # 사용자 세션을 저장, 여러 함수에서 사용해야 하므로, 전역 변수로 설정


# class 는 1user 이다.
class WebsiteUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = None
        global sessionIds
        self.sessionIds = sessionIds  # Assign the global sessionIds list to the instance variable
        print({"세션 ID 리스트 체크 ": self.sessionIds})

    host = "https://yourwebsite.com"  # Add your website URL here
    wait_time = between(1, 2)

    def on_start(self):
        global post_session_called
        if not post_session_called:
            for email in emails:
                self.email = email  # Store email in an instance variable
                self.post_session()
            post_session_called = True

    # ✅ : 세션 정보를 가져오기 위한 최초 수행 함수!
    @task
    def post_session(self):
        global post_session_called
        if post_session_called:
            return
        url = "/api/v1/session"  # Add the endpoint to create a session here
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        data = gen(self.email)  # Use the stored email
        response = self.client.post(url, headers=headers, json=data)
        # print(response.text)
        if response.text:
            try:
                json_response = response.json()
                if 'data' in json_response and 'sessionId' in json_response['data']:
                    sessionId = json_response['data']['sessionId']  # Update the global sessionId
                    print("누규의 세션 아이디 일까?:", sessionId)  # Print sessionId
                    self.sessionIds.append(sessionId)  # Append sessionId to the sessionIds list
                    print({"저장된 세션 ID 리스트 체크!!!": self.sessionIds})
                    self.client.headers.update({"x-session-id": sessionId})
                    return sessionId
                else:
                    print("The server didn't return a sessionId.")
                    return None
            except json.JSONDecodeError:
                print("The server didn't return a valid JSON response.")

    post_session_called = True

    # ✅ : 정상 조회 됨! 사용자 목록 조회
    @task
    def get_users(self):
        if not self.sessionIds:  # Check if sessionIds list is empty
            print("No sessionIds available.")
            return

        url = "/api/v1/admin/users"
        headers = {
            'accept': '*/*',
            'Authorization': BEARER_TOKEN,
            'x-session-id': random.choice(self.sessionIds)  # Use a random sessionId from the sessionIds list
        }
        print('Users 의 x-session-id:', random.choice(self.sessionIds))
        response = self.client.get(url, headers=headers)

        response_lines = response.text.split('},')  # Split the response text into lines
        top_3_lines = response_lines[:3]  # Get the first 3 lines
        for line in top_3_lines:
            print(line)  # Print each of the top 3 lines

        print("중간 실행 users")
        if response.text:
            try:
                json_response = response.json()
                if 'data' in json_response:
                    return json_response['data']
                else:
                    print("The server didn't return a sessionId.")
                    return None
            except json.JSONDecodeError:
                print("The server didn't return a valid JSON response.")
        return response
