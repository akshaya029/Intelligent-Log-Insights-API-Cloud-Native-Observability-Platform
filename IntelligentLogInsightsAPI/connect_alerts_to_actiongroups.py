from azure.identity import AzureCliCredential
from azure.mgmt.monitor import MonitorManagementClient

# ------------------ CONFIG ------------------
subscription_id = "de0268c5-7cb1-486d-b77b-cfdfeb844454"
resource_group = "IntelligentLogInsights"

# Mapping between alert rules and action groups
alert_to_actiongroup = {
    "CriticalErrorLogsAlert": "AG_SendToServiceBus_Critical",
    "ErrorLogsAlert": "AG_SendToServiceBus_Error",
    "LoginAnomalyAlert": "AG_SendToServiceBus_Security",
    "PerformanceWarningAlert": "AG_SendToServiceBus_Warning"
}

# ------------------ AUTH ------------------
# Use Azure CLI credentials for interactive environments
credential = AzureCliCredential()
monitor_client = MonitorManagementClient(credential, subscription_id)

# ------------------ FUNCTION ------------------
def link_alert_to_actiongroup(alert_name, actiongroup_name):
    # Full Action Group resource ID
    ag_resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/"
        f"providers/microsoft.insights/actionGroups/{actiongroup_name}"
    )

    print(f"\n🔗 Linking Alert Rule: {alert_name} → Action Group: {actiongroup_name}")

    try:
        # Get the existing alert rule
        alert_rule = monitor_client.scheduled_query_rules.get(resource_group, alert_name)

        # Modify the alert rule's actions
        alert_rule.actions = {
            "actionGroupIds": [ag_resource_id]
        }

        # Update the alert rule
        monitor_client.scheduled_query_rules.create_or_update(
            resource_group,
            alert_name,
            alert_rule
        )

        print(f"✅ Successfully linked {alert_name} to {actiongroup_name}")

    except Exception as e:
        print(f"❌ Failed for {alert_name}: {e}")

# ------------------ MAIN ------------------
for alert_name, ag_name in alert_to_actiongroup.items():
    link_alert_to_actiongroup(alert_name, ag_name)
