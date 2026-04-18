# -*- coding: utf-8 -*-
"""
RealE Tube - Google OAuth Helper
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from pathlib import Path

class GoogleAuthHelper:
    """Helper class for Google OAuth authentication"""

    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self, credentials_path: str):
        """
        Initialize Google Auth Helper

        Args:
            credentials_path: Path to OAuth client secrets JSON file
        """
        self.credentials_path = credentials_path
        self.token_path = Path(credentials_path).parent / 'token.pickle'
        self.creds = None

    def authenticate(self) -> Credentials:
        """
        Authenticate with Google APIs using OAuth 2.0.

        On first run (or after token deletion) this opens a browser for
        the OAuth consent flow. Subsequent runs load the saved token and
        refresh it silently when it expires.  If the refresh token itself
        has been revoked (e.g. by the user in their Google account), the
        saved pickle is deleted and the full browser flow is triggered again.
        """
        # Load existing token if available
        if self.token_path.exists():
            try:
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            except Exception:
                # Corrupted or incompatible pickle — start fresh
                print("Stored token is corrupted; re-authenticating...")
                self.token_path.unlink(missing_ok=True)
                self.creds = None

        # If no valid credentials, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    # Silent refresh — works as long as the refresh token is valid
                    self.creds.refresh(Request())
                except Exception as e:
                    # Refresh token revoked or network error — force full re-auth
                    print(f"Token refresh failed ({e}); deleting saved token and re-authenticating...")
                    self.token_path.unlink(missing_ok=True)
                    self.creds = None

            if not self.creds or not self.creds.valid:
                # Full OAuth consent flow — opens a browser tab once
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save token for future use
            try:
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
            except Exception as e:
                print(f"Warning: could not save token: {e}")

        return self.creds

    def get_youtube_service(self):
        """Get authenticated YouTube API service"""
        if not self.creds:
            self.authenticate()

        return build('youtube', 'v3', credentials=self.creds)

    def get_drive_service(self):
        """Get authenticated Google Drive API service"""
        if not self.creds:
            self.authenticate()

        return build('drive', 'v3', credentials=self.creds)

    def revoke_credentials(self):
        """Revoke and delete stored credentials"""
        if self.token_path.exists():
            self.token_path.unlink()
        self.creds = None
