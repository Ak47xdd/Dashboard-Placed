import requests

API = 'https://dashboard-app-zggs.onrender.com'

def test_cron():
    try :
        response = requests.get(f"{API}/cron-task")
        assert response.status_code == 200
        if response.status_code == 200:
            print("\n[200 OK] : Cron task executed successfully.")
    except requests.RequestException as e:
        print(f"Error : {e}")
        