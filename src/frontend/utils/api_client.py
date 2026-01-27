"""
API client for communicating with the backend.
"""

import requests
import streamlit as st
from typing import Optional, Dict, Any
import json

class TruthLensAPIClient:
    """Client for TruthLens backend API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 30
    
    def analyze_image(self, image_file, analysis_type: str = "standard") -> Optional[Dict[str, Any]]:
        """
        Send image for analysis.
        
        Args:
            image_file: Uploaded image file
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results or None if error
        """
        try:
            # Prepare the request
            files = {'file': (image_file.name, image_file.getvalue(), image_file.type)}
            data = {'analysis_type': analysis_type}
            
            # Make the request
            response = requests.post(
                f"{self.base_url}/api/analyze",
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    def get_history(self, limit: int = 50, offset: int = 0) -> Optional[Dict[str, Any]]:
        """
        Get analysis history.
        
        Args:
            limit: Number of results to return
            offset: Offset for pagination
            
        Returns:
            History data or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/history",
                params={'limit': limit, 'offset': offset},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """Test connection to the backend API."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# Singleton instance
api_client = TruthLensAPIClient()