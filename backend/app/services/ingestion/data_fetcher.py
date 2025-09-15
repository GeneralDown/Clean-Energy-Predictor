"""
DataFetcher class for retrieving environmental and grid data.
"""

import json
import csv
import aiohttp
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Handles fetching environmental and grid data from various sources.
    Currently supports mock data files and HTTP APIs.
    """
    
    def __init__(self, mock_data_path: Optional[str] = None):
        """
        Initialize DataFetcher.
        
        Args:
            mock_data_path: Path to mock data directory. Defaults to app/data/mock/
        """
        if mock_data_path is None:
            # Default to mock data directory relative to this file
            current_dir = Path(__file__).parent.parent.parent
            self.mock_data_path = current_dir / "data" / "mock"
        else:
            self.mock_data_path = Path(mock_data_path)
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_environmental_data(self, source: str = "mock") -> List[Dict[str, Any]]:
        """
        Fetch environmental data from specified source.
        
        Args:
            source: Data source type ("mock", "api", or URL)
            
        Returns:
            List of environmental data records
            
        Raises:
            FileNotFoundError: If mock data file doesn't exist
            aiohttp.ClientError: If HTTP request fails
        """
        if source == "mock":
            return await self._fetch_mock_environmental_data()
        elif source == "api" or source.startswith("http"):
            return await self._fetch_api_environmental_data(source)
        else:
            raise ValueError(f"Unsupported data source: {source}")
    
    async def fetch_grid_data(self, source: str = "mock") -> List[Dict[str, Any]]:
        """
        Fetch grid data from specified source.
        
        Args:
            source: Data source type ("mock", "api", or URL)
            
        Returns:
            List of grid data records
            
        Raises:
            FileNotFoundError: If mock data file doesn't exist
            aiohttp.ClientError: If HTTP request fails
        """
        if source == "mock":
            return await self._fetch_mock_grid_data()
        elif source == "api" or source.startswith("http"):
            return await self._fetch_api_grid_data(source)
        else:
            raise ValueError(f"Unsupported data source: {source}")
    
    async def _fetch_mock_environmental_data(self) -> List[Dict[str, Any]]:
        """Fetch environmental data from mock JSON file."""
        file_path = self.mock_data_path / "environmental_data.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Mock environmental data file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Fetched {len(data)} environmental records from mock data")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing environmental mock data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading environmental mock data: {e}")
            raise
    
    async def _fetch_mock_grid_data(self) -> List[Dict[str, Any]]:
        """Fetch grid data from mock JSON file."""
        file_path = self.mock_data_path / "grid_data.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Mock grid data file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Fetched {len(data)} grid records from mock data")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing grid mock data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading grid mock data: {e}")
            raise
    
    async def _fetch_api_environmental_data(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch environmental data from HTTP API.
        
        Args:
            url: API endpoint URL
            
        Returns:
            List of environmental data records
        """
        if not self.session:
            raise RuntimeError("DataFetcher must be used as async context manager for API calls")
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                logger.info(f"Fetched {len(data)} environmental records from API: {url}")
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching environmental data from API {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching environmental data: {e}")
            raise
    
    async def _fetch_api_grid_data(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch grid data from HTTP API.
        
        Args:
            url: API endpoint URL
            
        Returns:
            List of grid data records
        """
        if not self.session:
            raise RuntimeError("DataFetcher must be used as async context manager for API calls")
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                logger.info(f"Fetched {len(data)} grid records from API: {url}")
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching grid data from API {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching grid data: {e}")
            raise
    
    async def fetch_csv_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Fetch data from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of data records
        """
        try:
            data = []
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"Fetched {len(data)} records from CSV: {file_path}")
            return data
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise