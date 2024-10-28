import os
import requests
import subprocess
import json

def setup_github():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GitHub token not found in environment variables")

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get user information first
    user_response = requests.get('https://api.github.com/user', headers=headers)
    if user_response.status_code != 200:
        return False, f"Failed to get user information: {user_response.status_code}"
    
    username = user_response.json()['login']

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
    
    if response.status_code == 201 or response.status_code == 422:  # 422 means repo already exists
        if response.status_code == 422:
            # If repo exists, get its info
            repo_response = requests.get(f'https://api.github.com/repos/{username}/event-song-request', headers=headers)
            if repo_response.status_code != 200:
                return False, "Repository exists but failed to fetch details"
            repo_info = repo_response.json()
        else:
            repo_info = response.json()
        
        clone_url = repo_info['clone_url']
        
        try:
            # Set git configuration
            subprocess.run(['git', 'config', '--global', 'user.email', f'{username}@users.noreply.github.com'])
            subprocess.run(['git', 'config', '--global', 'user.name', username])
            
            # Initialize repository
            subprocess.run(['git', 'init'])
            subprocess.run(['git', 'add', '.'])
            subprocess.run(['git', 'commit', '-m', 'Initial commit: Event Song Request App with WebSocket support'])
            
            # Remove existing remote if it exists
            subprocess.run(['git', 'remote', 'remove', 'origin'], stderr=subprocess.DEVNULL)
            
            # Set up remote and push
            remote_url = f'https://{username}:{token}@github.com/{username}/event-song-request.git'
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url])
            subprocess.run(['git', 'branch', '-M', 'main'])
            subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'])
            
            return True, f"Successfully created and pushed to GitHub repository: https://github.com/{username}/event-song-request"
        except subprocess.CalledProcessError as e:
            return False, f"Git operation failed: {str(e)}"
    else:
        error_msg = f"Failed to create repository: {response.status_code} - {response.json().get('message', '')}"
        return False, error_msg

if __name__ == "__main__":
    success, message = setup_github()
    print(message)
