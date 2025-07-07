# -*- coding: utf-8 -*-
"""Core AWS SSO auditing functionality."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from .aws_client_manager import AWSClientManager
from .config import Config
from .exceptions import AWSSSOAuditorError
from .utils import clean_aws_response, safe_get_nested

logger = logging.getLogger(__name__)


class NullOutputSink:
    """Null object pattern for output sink."""
    def progress(self, message): pass
    def debug_info(self, message): pass
    def warning(self, message): pass
    def info(self, message): pass
    def error(self, message): pass

class AWSSSOAuditor:
    """Main AWS SSO auditing class."""

    def __init__(self, config: Config = None, output_sink=None):
        """Initialize the AWS SSO Auditor."""
        self.config = config or Config()
        self.config.validate()

        # Initialize output sink
        self.output_sink = output_sink or NullOutputSink()

        # Initialize AWS clients
        self.output_sink.progress("Initializing AWS clients...")
        self.aws_manager = AWSClientManager(self.config)

        # Store frequently used references
        self.sso_admin_client = self.aws_manager.sso_admin_client
        self.identitystore_client = self.aws_manager.identitystore_client
        self.organizations_client = self.aws_manager.organizations_client
        self.identity_store_id = self.aws_manager.identity_store_id
        self.instance_arn = self.aws_manager.instance_arn

        # Show client info in debug mode
        if self.config.debug:
            client_info = self.aws_manager.get_client_info()
            logger.debug("AWS Client Info: %s", client_info)
            self.output_sink.debug_info(f"Connected to SSO instance: {self.instance_arn}")

        logger.info("AWS SSO Auditor initialized successfully")

    # pylint: disable=too-many-branches
    def audit_account(self, account_id: str) -> Dict[str, Any]:
        """Perform complete audit of SSO access for the given account."""
        logger.info("Starting AWS SSO audit for account: %s", account_id)
        self.output_sink.progress(f"Starting audit for account: {account_id}")

        try:
            # Get all account assignments (only for permission sets assigned to this account)
            self.output_sink.progress("Retrieving account assignments...")
            assignments = self.get_all_account_assignments(account_id)
            self.output_sink.debug_info(f"Found {len(assignments)} assignments")

            # Organize data
            groups_data = {}
            permission_sets_data = {}

            self.output_sink.progress("Processing assignments...")
            for assignment in assignments:
                principal_type = assignment["PrincipalType"]
                principal_id = assignment["PrincipalId"]
                permission_set_arn = assignment["PermissionSetArn"]

                if principal_type == "GROUP":
                    if principal_id not in groups_data:
                        self.output_sink.progress(f"Processing group: {principal_id}")
                        group_details = self.get_group_details(principal_id)
                        group_members = self.get_group_members(principal_id)
                        groups_data[principal_id] = {
                            **group_details,
                            "Members": group_members,
                            "PermissionSets": [],
                        }

                    # Get full permission set details for this group
                    permission_set_details = self.get_permission_set_details(permission_set_arn)
                    permission_set_policies = self.get_permission_set_policies(permission_set_arn)

                    permission_set_full_details = {
                        **permission_set_details,
                        "Policies": permission_set_policies,
                    }

                    groups_data[principal_id]["PermissionSets"].append(permission_set_full_details)

                # Collect permission set data (only for those with assignments to this account)
                if permission_set_arn not in permission_sets_data:
                    self.output_sink.progress(
                        f"Processing permission set: {permission_set_arn}"
                    )
                    permission_set_details = self.get_permission_set_details(permission_set_arn)
                    permission_set_policies = self.get_permission_set_policies(permission_set_arn)
                    permission_sets_data[permission_set_arn] = {
                        **permission_set_details,
                        "Policies": permission_set_policies,
                        "AssignedGroups": [],
                    }

                if principal_type == "GROUP":
                    if (
                        principal_id
                        not in permission_sets_data[permission_set_arn]["AssignedGroups"]
                    ):
                        permission_sets_data[permission_set_arn]["AssignedGroups"].append(
                            principal_id
                        )

            # Create simple lists for summary
            group_names = [group["DisplayName"] for group in groups_data.values()]
            permission_set_names = [
                ps.get("Name", "Unknown") for ps in permission_sets_data.values()
            ]

            self.output_sink.progress("Finalizing audit results...")

            # Build final result
            result = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "account_id": account_id,
                    "sso_instance_arn": self.instance_arn,
                    "identity_store_id": self.identity_store_id,
                    "auditor_version": "1.0.0",
                    "config": {
                        "aws_region": self.config.aws_region,
                        "output_formats": self.config.output_formats,
                    },
                },
                "sso_groups_summary": group_names,
                "sso_permission_sets_summary": permission_set_names,
                "sso_groups": list(groups_data.values()),
                "permission_sets": list(permission_sets_data.values()),
                "summary": {
                    "total_groups": len(groups_data),
                    "total_permission_sets": len(permission_sets_data),
                    "total_assignments": len(assignments),
                },
            }

            logger.info("Audit completed successfully for account %s", account_id)
            return result

        except Exception as e:
            logger.error("Audit failed for account %s: %s", account_id, e)
            raise AWSSSOAuditorError(f"Failed to audit account {account_id}: {e}") from e

    def get_permission_sets_for_account(self, account_id: str) -> List[str]:
        """Get only permission sets that are provisioned/assigned to the specific account."""
        try:
            permission_sets = []
            paginator = self.sso_admin_client.get_paginator(
                "list_permission_sets_provisioned_to_account"
            )

            for page in paginator.paginate(InstanceArn=self.instance_arn, AccountId=account_id):
                permission_sets.extend(page["PermissionSets"])

            logger.info(
                "Found %d permission sets provisioned to account %s",
                len(permission_sets),
                account_id,
            )
            return permission_sets
        except Exception as e:
            logger.error("Error getting permission sets for account %s: %s", account_id, e)
            return []

    def get_account_assignments_for_permission_set(
        self, permission_set_arn: str, account_id: str
    ) -> List[Dict[str, Any]]:
        """Get account assignments for a specific permission set and account."""
        try:
            assignments = []
            paginator = self.sso_admin_client.get_paginator("list_account_assignments")

            for page in paginator.paginate(
                InstanceArn=self.instance_arn,
                AccountId=account_id,
                PermissionSetArn=permission_set_arn,
            ):
                assignments.extend(page["AccountAssignments"])

            return assignments
        except Exception as e:
            logger.error(
                "Error getting account assignments for permission set %s: %s", permission_set_arn, e
            )
            return []

    def get_all_account_assignments(self, account_id: str) -> List[Dict[str, Any]]:
        """Get all account assignments for the given account.

        Only checks permission sets that are provisioned to this account.
        """
        all_assignments = []

        # Get only permission sets that are provisioned to this account
        permission_sets = self.get_permission_sets_for_account(account_id)

        # Then get assignments for each provisioned permission set
        for permission_set_arn in permission_sets:
            assignments = self.get_account_assignments_for_permission_set(
                permission_set_arn, account_id
            )
            all_assignments.extend(assignments)

        logger.info("Found %d total assignments for account %s", len(all_assignments), account_id)
        return all_assignments

    def get_group_details(self, group_id: str) -> Dict[str, Any]:
        """Get group details including name and description."""
        try:
            response = self.identitystore_client.describe_group(
                IdentityStoreId=self.identity_store_id, GroupId=group_id
            )
            return {
                "GroupId": response["GroupId"],
                "DisplayName": response["DisplayName"],
                "Description": response.get("Description", ""),
            }
        except Exception as e:
            logger.error("Error getting group details for %s: %s", group_id, e)
            return {"GroupId": group_id, "DisplayName": "Unknown", "Description": ""}

    def get_group_members(self, group_id: str) -> List[Dict[str, Any]]:
        """Get all members of a group."""
        try:
            members = []
            paginator = self.identitystore_client.get_paginator("list_group_memberships")

            for page in paginator.paginate(
                IdentityStoreId=self.identity_store_id, GroupId=group_id
            ):
                for membership in page["GroupMemberships"]:
                    user_id = membership["MemberId"]["UserId"]
                    user_details = self.get_user_details(user_id)
                    members.append(user_details)

            return members
        except Exception as e:
            logger.error("Error getting group members for %s: %s", group_id, e)
            return []

    def get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get user details including username and display name."""
        try:
            response = self.identitystore_client.describe_user(
                IdentityStoreId=self.identity_store_id, UserId=user_id
            )
            return {
                "UserId": response["UserId"],
                "UserName": response["UserName"],
                "DisplayName": response.get("DisplayName", response["UserName"]),
                "Email": safe_get_nested(response, ["Emails", 0, "Value"], ""),
            }
        except Exception as e:
            logger.error("Error getting user details for %s: %s", user_id, e)
            return {"UserId": user_id, "UserName": "Unknown", "DisplayName": "Unknown", "Email": ""}

    def get_permission_set_details(self, permission_set_arn: str) -> Dict[str, Any]:
        """Get permission set details."""
        try:
            response = self.sso_admin_client.describe_permission_set(
                InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
            )
            return clean_aws_response(response["PermissionSet"])
        except Exception as e:
            logger.error("Error getting permission set details for %s: %s", permission_set_arn, e)
            return {}

    def get_permission_set_policies(self, permission_set_arn: str) -> Dict[str, Any]:
        """Get all policies attached to a permission set."""
        policies = {"managed_policies": [], "customer_managed_policies": [], "inline_policy": None}

        try:
            # Get AWS managed policies
            managed_paginator = self.sso_admin_client.get_paginator(
                "list_managed_policies_in_permission_set"
            )
            for page in managed_paginator.paginate(
                InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
            ):
                policies["managed_policies"].extend(page["AttachedManagedPolicies"])

            # Get customer managed policies
            customer_paginator = self.sso_admin_client.get_paginator(
                "list_customer_managed_policy_references_in_permission_set"
            )
            for page in customer_paginator.paginate(
                InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
            ):
                for policy_ref in page["CustomerManagedPolicyReferences"]:
                    policy_details = self.get_customer_managed_policy_details(policy_ref)
                    policies["customer_managed_policies"].append(policy_details)

            # Get inline policy
            try:
                inline_response = self.sso_admin_client.get_inline_policy_for_permission_set(
                    InstanceArn=self.instance_arn, PermissionSetArn=permission_set_arn
                )
                if inline_response.get("InlinePolicy"):
                    policies["inline_policy"] = json.loads(inline_response["InlinePolicy"])
            except self.sso_admin_client.exceptions.ResourceNotFoundException:
                # No inline policy exists
                pass

        except Exception as e:
            logger.error("Error getting policies for permission set %s: %s", permission_set_arn, e)

        return policies

    def get_customer_managed_policy_details(self, policy_ref: Dict[str, Any]) -> Dict[str, Any]:
        """Get details for customer managed policy."""
        try:
            return {
                "Name": policy_ref["Name"],
                "Path": policy_ref.get("Path", "/"),
                "Type": "CustomerManaged",
                "Note": "Policy document not retrieved - requires target account access",
            }
        except Exception as e:
            logger.error("Error getting customer managed policy details: %s", e)
            return policy_ref
