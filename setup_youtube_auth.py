"""
YouTube OAuth Refresh Token Generator
Run this script once locally to generate the YOUTUBE_REFRESH_TOKEN for GitHub Secrets.

Usage:
1. Download OAuth 2.0 Client Secrets JSON from Google Cloud Console (YouTube Data API v3 enabled)
2. Save it in this directory as 'client_secret.json'
3. Run: python setup_youtube_auth.py
4. Copy the printed Refresh Token into GitHub Secrets: YOUTUBE_REFRESH_TOKEN
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def main():
    try:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

        print("\n" + "="*60)
        print("AUTHENTICATION SUCCESSFUL!")
        print("="*60)
        print("\nPaste these into your GitHub Repository Secrets:\n")
        print("1. Secret Name: YOUTUBE_REFRESH_TOKEN")
        print(f"Value:\n{creds.refresh_token}\n")

        with open("client_secret.json", "r", encoding="utf-8") as f:
            secret_content = f.read()

        print("2. Secret Name: YOUTUBE_CLIENT_SECRET_JSON")
        print(f"Value:\n{secret_content}\n")
        print("="*60)
    except FileNotFoundError:
        print("\n[ERROR] 'client_secret.json' file not found!")
        print("Please place your downloaded Google Cloud OAuth JSON file here as 'client_secret.json' and re-run.")

if __name__ == "__main__":
    main()
