#!/usr/bin/env python3
"""
Update an ElevenLabs agent via PATCH, optionally on a specific branch.

Usage:
    python update_agent.py <agent_id> <payload.json> [--branch <branch_id>]

Requires:
    ELEVENLABS_API_KEY environment variable
    pip install requests
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.elevenlabs.io/v1"

PATCH_FIELDS = [
    "name", "conversation_config", "platform_settings", "workflow", "tags",
]


def update_agent(api_key: str, agent_id: str, payload: dict,
                 branch_id: str = None) -> dict:
    params = {}
    if branch_id:
        params["branch_id"] = branch_id

    body = {k: v for k, v in payload.items() if k in PATCH_FIELDS}

    response = requests.patch(
        f"{BASE_URL}/convai/agents/{agent_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        params=params,
        json=body,
        verify=True,
        timeout=60,
    )

    if not response.ok:
        error_detail = ""
        try:
            error_detail = json.dumps(response.json(), indent=2)
        except Exception:
            error_detail = response.text[:1000] if response.text else "No response body"
        raise Exception(f"{response.status_code} Error:\n{error_detail}")

    return response.json()


def main():
    if len(sys.argv) < 3:
        print("Usage: python update_agent.py <agent_id> <payload.json> [--branch <branch_id>]")
        print("\nExample:")
        print("  python update_agent.py agent_abc123 agents/tandem_v3.json")
        print("  python update_agent.py agent_abc123 agents/tandem_v3.json --branch agtbrch_xyz")
        sys.exit(1)

    agent_id = sys.argv[1]
    payload_file = sys.argv[2]

    branch_id = None
    if "--branch" in sys.argv:
        idx = sys.argv.index("--branch")
        if idx + 1 < len(sys.argv):
            branch_id = sys.argv[idx + 1]

    if not os.path.exists(payload_file):
        print(f"Error: File not found: {payload_file}")
        sys.exit(1)

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export ELEVENLABS_API_KEY='your-api-key-here'")
        sys.exit(1)

    with open(payload_file, "r") as f:
        payload = json.load(f)

    body = {k: v for k, v in payload.items() if k in PATCH_FIELDS}

    print(f"Agent:   {agent_id}")
    print(f"Payload: {payload_file}")
    print(f"Branch:  {branch_id or '(default)'}")
    print(f"Name:    {body.get('name', 'N/A')}")
    print(f"Fields:  {', '.join(body.keys())}")

    response = input("\nReady to PATCH. Continue? [y/N]: ").strip().lower()
    if response != "y":
        print("Aborted.")
        sys.exit(0)

    print("\nUpdating agent...")
    try:
        result = update_agent(api_key, agent_id, payload, branch_id)
        print("\n" + "=" * 50)
        print("SUCCESS! Agent updated.")
        print("=" * 50)
        print(f"\nAgent ID:   {result.get('agent_id')}")
        print(f"Version ID: {result.get('version_id')}")
        print(f"Branch ID:  {result.get('branch_id')}")
    except Exception as e:
        print(f"\nError updating agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
