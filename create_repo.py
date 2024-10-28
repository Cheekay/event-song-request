import os
import requests

def create_github_repo():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GitHub token not found in environment variables")

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Create repository
    data = {
        'name': 'event-song-request',
        'description': 'A Flask-based web application for real-time song requests with WebSocket support',
        'private': False,
        'has_issues': True,
        'has_projects': True,
        'has_wiki': True
    }

    response = requests.post('https://api.github.com/user/repos', json=data, headers=headers)
    if response.status_code == 201:
        repo_info = response.json()
        return repo_info['clone_url'], repo_info['owner']['login']
    else:
        print(f"Failed to create repository: {response.status_code}")
        print(response.json())
        return None, None

if __name__ == "__main__":
    repo_url, username = create_github_repo()
    if repo_url:
        print(f"REPO_URL={repo_url}")
        print(f"USERNAME={username}")
