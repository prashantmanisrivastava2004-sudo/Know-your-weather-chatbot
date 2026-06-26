from app import app

client = app.test_client()
response = client.post(
    '/',
    json={
        'queryResult': {
            'parameters': {'city': 'London'},
            'queryText': 'What is the weather in London?'
        }
    }
)
print(response.status_code)
print(response.get_json())
