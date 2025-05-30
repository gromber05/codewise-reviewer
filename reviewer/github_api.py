import requests
import os
import subprocess
from dotenv import load_dotenv
from dotenv import get_key

GITHUB_TOKEN = get_key("key.env", "GITHUB_TOKEN")

load_dotenv()

def get_local_repo_url():
    """
    Obtiene la URL del repositorio remoto configurado en el repositorio local.

    Returns:
        str or None: La URL del repositorio remoto como string, o None si no hay un repositorio configurado.
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        repo_url = result.stdout.strip()
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4] 
            repo_url = repo_url.split(":")
        return repo_url[1]
    except subprocess.CalledProcessError:
        print("No Git repository found or no remote URL configured.")
        return None

def get_next_pr_number():
    """
    Obtiene el siguiente número de Pull Request abierto en el repositorio.

    Returns:
        int or None: El número del primer Pull Request abierto como entero, o None si no hay PRs abiertos.
    """
    repo_url = get_local_repo_url()
    if not repo_url:
        print("No repository URL found. Skipping PR retrieval.")
        return None

    repo = repo_url.split("https://github.com/")[-1]
    if not repo:
        print("Invalid repository URL format.")
        return None

    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN is not set in the environment variables.")
        return None

    api_url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch PRs: {response.status_code} - {response.content}")
        return None

    prs = response.json()
    if not prs:
        print("No open Pull Requests found.")
        return None

    return prs[0]["number"]

def post_comment(comment):
    """
    Publica un comentario en el Pull Request.

    Args:
        comment (str): El contenido del comentario a publicar.
    """
    pr_number = get_next_pr_number()
    if not pr_number:
        print("No PR number available. Cannot post comment.")
        return

    repo_url = get_local_repo_url()
    if not repo_url:
        print("No repository URL found. Skipping comment posting.")
        return

    repo = repo_url.split("github.com/")[-1]
    api_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code != 201:
        print("Failed to post comment:", response.content)
    else:
        print(f"Comment posted successfully on PR #{pr_number}.")
