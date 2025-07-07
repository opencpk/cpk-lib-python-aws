# -*- coding: utf-8 -*-
"""AWS client management for SSO auditing - extends shared base."""

import logging
from typing import Any, Dict

from ..shared import AWSBaseClient
from .config import Config
from .exceptions import AWSClientError, SSOInstanceNotFoundError

logger = logging.getLogger(__name__)


class AWSClientManager(AWSBaseClient):
    """Manages AWS clients specific to SSO auditing."""

    def __init__(self, config: Config):
        """Initialize AWS clients with SSO-specific configuration."""
        super().__init__(region=config.aws_region, profile=config.aws_profile)
        self.config = config

        # SSO-specific clients
        self.sso_admin_client = None
        self.identitystore_client = None
        self.organizations_client = None

        # SSO instance information
        self.sso_instance = None
        self.identity_store_id = None
        self.instance_arn = None

        self._initialize_sso_clients()

    def _initialize_sso_clients(self) -> None:
        """Initialize SSO-specific AWS clients."""
        try:
            # Initialize AWS clients
            self.sso_admin_client = self.session.client("sso-admin")
            self.identitystore_client = self.session.client("identitystore")
            self.organizations_client = self.session.client("organizations")

            logger.info("SSO-specific AWS clients initialized successfully")

            # Discover SSO instance
            self._discover_sso_instance()

        except Exception as e:
            logger.error("Failed to initialize SSO clients: %s", e)
            raise AWSClientError(f"Error initializing SSO clients: {e}") from e

    def _discover_sso_instance(self) -> None:
        """Discover and validate SSO instance."""
        try:
            response = self.sso_admin_client.list_instances()
            if not response["Instances"]:
                raise SSOInstanceNotFoundError("No SSO instances found in this AWS account")

            self.sso_instance = response["Instances"][0]
            self.identity_store_id = self.sso_instance["IdentityStoreId"]
            self.instance_arn = self.sso_instance["InstanceArn"]

            logger.info("SSO instance discovered: %s", self.instance_arn)

        except Exception as e:
            if "No SSO instances found" in str(e):
                raise
            logger.error("Failed to discover SSO instance: %s", e)
            raise SSOInstanceNotFoundError(f"Failed to get SSO instance: {e}") from e

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about configured SSO clients."""
        base_info = {
            "region": self.region,
            "profile": self.profile,
            "caller_identity": self.get_caller_identity(),
        }

        sso_info = {
            "sso_instance_arn": self.instance_arn,
            "identity_store_id": self.identity_store_id,
            "has_sso_admin": self.sso_admin_client is not None,
            "has_identity_store": self.identitystore_client is not None,
            "has_organizations": self.organizations_client is not None,
        }

        return {**base_info, **sso_info}
