"""Base AWS client management shared across packages."""

import boto3
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .exceptions import AWSError, CredentialsError

logger = logging.getLogger(__name__)


class AWSBaseClient(ABC):
    """Base class for AWS service clients with common functionality."""
    
    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        """Initialize base AWS client."""
        self.region = region
        self.profile = profile
        self.session = None
        self._initialize_session()
        
    def _initialize_session(self) -> None:
        """Initialize boto3 session with optional profile."""
        try:
            session_kwargs = {'region_name': self.region}
            if self.profile:
                session_kwargs['profile_name'] = self.profile
                
            self.session = boto3.Session(**session_kwargs)
            logger.info(f"AWS session initialized for region: {self.region}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS session: {e}")
            raise CredentialsError(f"Failed to initialize AWS session: {e}")
    
    def get_caller_identity(self) -> Dict[str, Any]:
        """Get current AWS caller identity."""
        try:
            sts_client = self.session.client('sts')
            return sts_client.get_caller_identity()
        except Exception as e:
            raise AWSError(f"Failed to get caller identity: {e}")