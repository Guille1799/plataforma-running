import requests, json, time
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:8000/api/v1'
timestamp = int(time.time())
email = f'test_{timestamp}@example.com'

# Register
resp = requests.post(f'{BASE_URL}/auth/register', json={'name': 'Test User', 'email': email, 'password': 'TestPass123'})
print(f'[REGISTER] {resp.status_code}')

# Login
resp = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': 'TestPass123'})
token = resp.json().get('access_token')
print(f'[LOGIN] {resp.status_code}')

# Test Training Plans
headers = {'Authorization': f'Bearer {token}'}
payload = {
    'goal_type': 'marathon',
    'goal_date': (datetime.now() + timedelta(days=120)).date().isoformat(),
    'current_weekly_km': 50,
    'weeks': 12,
    'notes': 'Test'
}
resp = requests.post(f'{BASE_URL}/training-plans/generate', json=payload, headers=headers)
print(f'[TRAINING PLANS] {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    plan_name = data.get('plan', {}).get('plan_name', 'Unknown')
    print(f'[SUCCESS] Plan: {plan_name}')
else:
    print(f'[ERROR] {resp.text[:300]}')
