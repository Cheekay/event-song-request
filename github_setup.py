import os
import requests
import subprocess

def setup_github():
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
        'has_wiki': True,
        'auto_init': False
    }

    response = requests.post('https://api.github.com/user/repos', json=data, headers=headers)
    
    if response.status_code == 201:
        repo_info = response.json()
        clone_url = repo_info['clone_url']
        username = repo_info['owner']['login']
        
        # Set git configuration
        subprocess.run(['git', 'config', '--global', 'user.email', 'replit@example.com'])
        subprocess.run(['git', 'config', '--global', 'user.name', 'Replit'])
        
        # Initialize repository
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Initial commit: Event Song Request App with WebSocket support'])
        
        # Set up remote and push
        remote_url = clone_url.replace('https://', f'https://{token}@')
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url])
        subprocess.run(['git', 'branch', '-M', 'main'])
        subprocess.run(['git', 'push', '-u', 'origin', 'main'])
        
        return True, "Successfully created and pushed to GitHub repository"
    else:
        error_msg = f"Failed to create repository: {response.status_code} - {response.json().get('message', '')}"
        return False, error_msg

if __name__ == "__main__":
    success, message = setup_github()
    print(message)
