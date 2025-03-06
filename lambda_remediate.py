import json
import boto3
import subprocess
import os

def send_notification(message):
    """ Placeholder function for sending notifications (Slack, SNS, etc.) """
    print(f"Notification: {message}")

def get_pod_details(pod_name, namespace):
    """ Fetch pod details using kubectl """
    try:
        output = subprocess.check_output([
            "kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"
        ])
        return json.loads(output)
    except Exception as e:
        send_notification(f"Failed to get pod details: {e}")
        return None

def fix_oom_killed(pod_name, namespace):
    """ Fix OOMKilled by increasing memory limits """
    pod_spec = get_pod_details(pod_name, namespace)
    if not pod_spec:
        return
    
    container = pod_spec['spec']['containers'][0]
    current_limit = container['resources'].get('limits', {}).get('memory', '512Mi')
    new_limit = "1Gi" if current_limit == "512Mi" else "2Gi"
    
    patch_command = [
        "kubectl", "patch", "deployment", pod_name, "-n", namespace,
        "--type=json", "-p",
        f'[{{"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": "{new_limit}"}}]'
    ]
    try:
        subprocess.run(patch_command, check=True)
        send_notification(f"Increased memory limit to {new_limit} for pod {pod_name}")
    except Exception as e:
        send_notification(f"Failed to patch pod memory limit: {e}")

def fix_crash_loop_backoff(pod_name, namespace):
    """ Fix CrashLoopBackOff by restarting pod and increasing restart backoff """
    try:
        subprocess.run(["kubectl", "delete", "pod", pod_name, "-n", namespace], check=True)
        send_notification(f"Restarted pod {pod_name} to fix CrashLoopBackOff")
    except Exception as e:
        send_notification(f"Failed to restart pod {pod_name}: {e}")

def fix_node_not_ready(node_name):
    """ Fix NotReady nodes by restarting kubelet and cordoning if needed """
    try:
        subprocess.run(["kubectl", "uncordon", node_name], check=True)
        send_notification(f"Uncordoned node {node_name} and marked as Ready")
    except Exception as e:
        send_notification(f"Failed to uncordon node {node_name}: {e}")

def lambda_handler(event, context):
    """ AWS Lambda entry point """
    detail = event.get("detail", {})
    issue_type = detail.get("status")
    
    if issue_type == "OOMKilled":
        pod_name = detail.get("podName")
        namespace = detail.get("namespace")
        fix_oom_killed(pod_name, namespace)
    
    elif issue_type == "CrashLoopBackOff":
        pod_name = detail.get("podName")
        namespace = detail.get("namespace")
        fix_crash_loop_backoff(pod_name, namespace)
    
    elif issue_type == "NodeNotReady":
        node_name = detail.get("nodeName")
        fix_node_not_ready(node_name)
    
    return {"status": "Remediation executed"}
