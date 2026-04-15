#!/usr/bin/env python3
"""
Deploy an ElevenLabs agent with tools from a JSON payload file.

This script:
1. Optionally wires knowledge base refs from a manifest into the agent
2. Extracts inline tools from the agent JSON
3. Deploys each tool to ElevenLabs (as workspace tools)
4. Shares each tool with the workspace
5. Extracts MCP server configs and deploys them
6. Replaces inline tool definitions with tool_id references
7. Wires MCP server IDs into the agent config
8. Deploys the agent
9. Shares the agent with the workspace
10. Optionally creates agent tests and attaches them

Usage:
    python deploy_with_tools.py <payload.json> [--kb-manifest <manifest.json>] [--tests <tests.json>]

Requires:
    ELEVENLABS_API_KEY environment variable
    pip install requests python-dotenv
"""
import argparse
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.elevenlabs.io/v1"


def extract_tools(payload: dict) -> list:
    """Extract tools from conversation_config.agent.prompt.tools[]"""
    return payload.get("conversation_config", {}).get("agent", {}).get("prompt", {}).get("tools", [])


def create_tool(api_key: str, tool: dict) -> dict:
    """POST tool to /v1/convai/tools with tool_config wrapper, return response"""
    response = requests.post(
        f"{BASE_URL}/convai/tools",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json={"tool_config": tool},
        verify=True
    )
    
    if not response.ok:
        error_detail = ""
        try:
            error_detail = str(response.json())
        except:
            error_detail = response.text[:500] if response.text else "No response body"
        raise Exception(f"{response.status_code} Error: {error_detail}")
    
    return response.json()


def share_resource(api_key: str, resource_id: str, resource_type: str) -> bool:
    """Share resource with workspace (admin access for all members)"""
    response = requests.post(
        f"{BASE_URL}/workspace/resources/{resource_id}/share",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json={
            "role": "admin",
            "resource_type": resource_type,
            "group_id": "default"
        },
        verify=True
    )
    return response.ok


def extract_mcp_servers(payload: dict) -> list:
    """Extract MCP server configs from top-level mcp_servers[] array."""
    return payload.pop("mcp_servers", [])


def create_mcp_server(api_key: str, server_config: dict) -> dict:
    """POST MCP server to /v1/convai/mcp-servers, return response."""
    response = requests.post(
        f"{BASE_URL}/convai/mcp-servers",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json={"config": server_config},
        verify=True
    )

    if not response.ok:
        error_detail = ""
        try:
            error_detail = str(response.json())
        except Exception:
            error_detail = response.text[:500] if response.text else "No response body"
        raise Exception(f"{response.status_code} Error: {error_detail}")

    return response.json()


def wire_mcp_servers_into_payload(payload: dict, mcp_server_ids: list[str]) -> dict:
    """Add MCP server IDs to conversation_config.agent.prompt.mcp_server_ids."""
    prompt = payload.setdefault("conversation_config", {}).setdefault("agent", {}).setdefault("prompt", {})
    existing = prompt.get("mcp_server_ids", [])
    combined = list(set(existing + mcp_server_ids))
    prompt["mcp_server_ids"] = combined
    return payload


def replace_tools_with_refs(payload: dict, tool_mapping: dict) -> dict:
    """Replace inline tool defs with tool_id references.
    
    - System tools go in conversation_config.agent.prompt.built_in_tools
    - Webhook/client tool IDs go in conversation_config.agent.prompt.tool_ids[]
    - Remove tools[] array entirely to avoid conflict
    """
    
    prompt_config = payload.get("conversation_config", {}).get("agent", {}).get("prompt", {})
    global_tools = prompt_config.get("tools", [])
    
    # 1. Convert system tools to built_in_tools format
    built_in_tools = prompt_config.get("built_in_tools", {})
    for t in global_tools:
        if t.get("type") == "system":
            params = t.get("params", {})
            system_tool_type = params.get("system_tool_type")
            if system_tool_type:
                # Map system_tool_type to built_in_tools key
                built_in_tools[system_tool_type] = t
    
    if built_in_tools:
        payload["conversation_config"]["agent"]["prompt"]["built_in_tools"] = built_in_tools
    
    # 2. Remove tools[] array entirely to avoid "both tools and tool_ids" error
    if "tools" in payload["conversation_config"]["agent"]["prompt"]:
        del payload["conversation_config"]["agent"]["prompt"]["tools"]
    
    # 3. Add webhook/client tool IDs to tool_ids[]
    all_tool_ids = [tid for tid in tool_mapping.values() if tid]
    existing_tool_ids = prompt_config.get("tool_ids", [])
    combined_tool_ids = list(set(existing_tool_ids + all_tool_ids))
    if combined_tool_ids:
        payload["conversation_config"]["agent"]["prompt"]["tool_ids"] = combined_tool_ids
    
    # 4. Tool nodes - workflow.nodes.* where type="tool" (if any)
    nodes = payload.get("workflow", {}).get("nodes", {})
    for node_name, node in nodes.items():
        if node.get("type") == "tool" and "tools" in node:
            node_tools = node["tools"]
            new_node_tools = []
            for t in node_tools:
                tool_name = t.get("name") if isinstance(t, dict) else t
                if tool_name in tool_mapping:
                    new_node_tools.append({"tool_id": tool_mapping[tool_name]})
            node["tools"] = new_node_tools
    
    return payload


def create_agent(api_key: str, payload: dict) -> dict:
    """Create an ElevenLabs agent"""
    response = requests.post(
        f"{BASE_URL}/convai/agents/create",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=payload,
        verify=True
    )
    
    if not response.ok:
        error_detail = ""
        try:
            error_detail = str(response.json())
        except:
            error_detail = response.text[:500] if response.text else "No response body"
        raise Exception(f"{response.status_code} Error: {error_detail}")
    
    return response.json()


def validate_key(api_key: str) -> bool:
    """Validate the API key"""
    try:
        response = requests.get(
            f"{BASE_URL}/voices",
            headers={"xi-api-key": api_key},
            verify=True
        )
        return response.ok
    except:
        return False


def create_test(api_key: str, agent_id: str, test_def: dict) -> dict:
    """Create an agent test via POST /v1/convai/agent-testing/create"""
    test_payload = {**test_def, "agent_id": agent_id}
    response = requests.post(
        f"{BASE_URL}/convai/agent-testing/create",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=test_payload,
        verify=True
    )

    if not response.ok:
        error_detail = ""
        try:
            error_detail = str(response.json())
        except Exception:
            error_detail = response.text[:500] if response.text else "No response body"
        raise Exception(f"{response.status_code} Error: {error_detail}")

    return response.json()


def attach_tests_to_agent(api_key: str, agent_id: str, test_ids: list[str]) -> dict:
    """PATCH agent to attach test IDs via platform_settings.testing"""
    attached = [{"test_id": tid, "workflow_node_id": None} for tid in test_ids]
    patch_payload = {
        "platform_settings": {
            "testing": {
                "attached_tests": attached
            }
        }
    }
    response = requests.patch(
        f"{BASE_URL}/convai/agents/{agent_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=patch_payload,
        verify=True
    )

    if not response.ok:
        error_detail = ""
        try:
            error_detail = str(response.json())
        except Exception:
            error_detail = response.text[:500] if response.text else "No response body"
        raise Exception(f"{response.status_code} Error: {error_detail}")

    return response.json()


def load_kb_manifest(manifest_path: str) -> list[dict]:
    """Load a KB manifest and return knowledge_base refs for the agent."""
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    docs = manifest.get("documents", [])
    return [
        {"type": "file", "id": doc["id"], "name": doc["name"], "usage_mode": doc.get("usage_mode", "auto")}
        for doc in docs
        if doc.get("id")
    ]


def wire_kb_into_payload(payload: dict, kb_refs: list[dict]) -> dict:
    """Inject knowledge_base refs into the agent payload."""
    prompt = payload.setdefault("conversation_config", {}).setdefault("agent", {}).setdefault("prompt", {})
    existing = prompt.get("knowledge_base", [])
    existing_ids = {ref["id"] for ref in existing}
    for ref in kb_refs:
        if ref["id"] not in existing_ids:
            existing.append(ref)
    prompt["knowledge_base"] = existing
    return payload


def main():
    parser = argparse.ArgumentParser(
        description="Deploy an ElevenLabs agent with tools (and optionally KB) from a JSON payload file"
    )
    parser.add_argument("payload", type=str, help="Agent JSON payload file")
    parser.add_argument("--kb-manifest", type=str, default=None,
                        help="KB manifest JSON from deploy_kb.py — wires document refs into the agent")
    parser.add_argument("--tests", type=str, default=None,
                        help="Tests JSON array — creates tests and attaches them to the deployed agent")
    args = parser.parse_args()

    payload_file = args.payload

    if not os.path.exists(payload_file):
        print(f"Error: File not found: {payload_file}")
        sys.exit(1)

    # Get API key
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export ELEVENLABS_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Validate API key
    print("Validating API key...")
    if not validate_key(api_key):
        print("Error: Invalid API key")
        sys.exit(1)
    print("API key valid!")

    # Load payload
    print(f"\nLoading payload from: {payload_file}")
    with open(payload_file, "r") as f:
        payload = json.load(f)

    agent_name = payload.get('name', 'Unknown')
    print(f"  Agent name: {agent_name}")
    print(f"  Workflow nodes: {len(payload.get('workflow', {}).get('nodes', {}))}")
    print(f"  Workflow edges: {len(payload.get('workflow', {}).get('edges', {}))}")

    # Wire KB manifest if provided
    kb_count = 0
    if args.kb_manifest:
        if not os.path.exists(args.kb_manifest):
            print(f"Error: KB manifest not found: {args.kb_manifest}")
            sys.exit(1)
        kb_refs = load_kb_manifest(args.kb_manifest)
        payload = wire_kb_into_payload(payload, kb_refs)
        kb_count = len(kb_refs)
        print(f"  KB documents: {kb_count} (from manifest)")

    # Load tests if provided
    test_defs = []
    if args.tests:
        if not os.path.exists(args.tests):
            print(f"Error: Tests file not found: {args.tests}")
            sys.exit(1)
        with open(args.tests, "r") as f:
            test_defs = json.load(f)
        if not isinstance(test_defs, list):
            print("Error: Tests file must be a JSON array of test definitions")
            sys.exit(1)
        print(f"  Tests to create: {len(test_defs)}")

    # Extract MCP servers
    mcp_servers = extract_mcp_servers(payload)

    # Extract tools by type
    tools = extract_tools(payload)
    webhook_tools = [t for t in tools if t.get("type") == "webhook"]
    client_tools = [t for t in tools if t.get("type") == "client"]
    system_tools = [t for t in tools if t.get("type") == "system"]
    deployable_tools = webhook_tools + client_tools

    print(f"  Webhook tools: {len(webhook_tools)}")
    print(f"  Client tools: {len(client_tools)}")
    print(f"  System tools: {len(system_tools)} (will stay inline)")
    print(f"  MCP servers: {len(mcp_servers)}")

    # Confirm
    print("\nThis will:")
    step = 1
    if kb_count:
        print(f"  {step}. Wire {kb_count} KB documents into agent")
        step += 1
    if deployable_tools:
        print(f"  {step}. Deploy {len(deployable_tools)} tools ({len(webhook_tools)} webhook, {len(client_tools)} client)")
        step += 1
        print(f"  {step}. Share each tool with workspace (admin access)")
        step += 1
    if mcp_servers:
        print(f"  {step}. Deploy {len(mcp_servers)} MCP server(s)")
        step += 1
        print(f"  {step}. Share each MCP server with workspace (admin access)")
        step += 1
    print(f"  {step}. Deploy agent '{agent_name}'")
    step += 1
    print(f"  {step}. Share agent with workspace (admin access)")
    if test_defs:
        step += 1
        print(f"  {step}. Create {len(test_defs)} tests and attach to agent")

    response = input("\nContinue? [y/N]: ").strip().lower()
    if response != 'y':
        print("Aborted.")
        sys.exit(0)

    # Deploy tools
    tool_mapping = {}

    if deployable_tools:
        print(f"\nDeploying {len(deployable_tools)} tools...")
        for i, tool in enumerate(deployable_tools, 1):
            tool_name = tool.get("name", f"tool_{i}")
            tool_type = tool.get("type", "unknown")
            try:
                result = create_tool(api_key, tool)
                tool_id = result.get("tool_id") or result.get("id")
                if not tool_id:
                    print(f"    WARNING: No tool_id in response. Keys: {list(result.keys())}")
                tool_mapping[tool_name] = tool_id

                shared = share_resource(api_key, tool_id, "convai_tools")
                share_status = "shared" if shared else "share failed"

                print(f"  [{i}/{len(deployable_tools)}] {tool_name} ({tool_type}) -> {tool_id} ({share_status})")

            except Exception as e:
                print(f"  [{i}/{len(deployable_tools)}] {tool_name} ({tool_type}) -> FAILED: {e}")
                cont = input("  Continue with remaining tools? [y/N]: ").strip().lower()
                if cont != 'y':
                    print("Aborted.")
                    sys.exit(1)

    print(f"\nTools deployed: {len(tool_mapping)}/{len(deployable_tools)}")

    # Deploy MCP servers
    mcp_server_mapping = {}

    if mcp_servers:
        print(f"\nDeploying {len(mcp_servers)} MCP server(s)...")
        for i, server_config in enumerate(mcp_servers, 1):
            server_name = server_config.get("name", f"mcp_server_{i}")
            try:
                result = create_mcp_server(api_key, server_config)
                server_id = result.get("id")
                if not server_id:
                    print(f"    WARNING: No id in response. Keys: {list(result.keys())}")
                mcp_server_mapping[server_name] = server_id

                shared = share_resource(api_key, server_id, "convai_mcp_servers")
                share_status = "shared" if shared else "share failed"

                print(f"  [{i}/{len(mcp_servers)}] {server_name} -> {server_id} ({share_status})")

            except Exception as e:
                print(f"  [{i}/{len(mcp_servers)}] {server_name} -> FAILED: {e}")
                cont = input("  Continue with remaining MCP servers? [y/N]: ").strip().lower()
                if cont != 'y':
                    print("Aborted.")
                    sys.exit(1)

    print(f"MCP servers deployed: {len(mcp_server_mapping)}/{len(mcp_servers)}")

    # Replace inline tools with references
    if tool_mapping:
        print("\nUpdating agent payload with tool references...")
        payload = replace_tools_with_refs(payload, tool_mapping)

    # Wire MCP server IDs into agent
    if mcp_server_mapping:
        print("Wiring MCP server IDs into agent config...")
        payload = wire_mcp_servers_into_payload(payload, list(mcp_server_mapping.values()))

    # Create agent
    print("\nDeploying agent...")
    try:
        result = create_agent(api_key, payload)
        agent_id = result.get('agent_id')

        shared = share_resource(api_key, agent_id, "convai_agents")
        share_status = "shared" if shared else "share failed"

        # Create and attach tests
        test_ids = []
        if test_defs:
            print(f"\nCreating {len(test_defs)} tests...")
            for i, test_def in enumerate(test_defs, 1):
                test_name = test_def.get("name", f"test_{i}")
                test_type = test_def.get("type", "unknown")
                try:
                    result_test = create_test(api_key, agent_id, test_def)
                    test_id = result_test.get("test_id") or result_test.get("id")
                    test_ids.append(test_id)
                    print(f"  [{i}/{len(test_defs)}] {test_name} ({test_type}) -> {test_id}")
                except Exception as e:
                    print(f"  [{i}/{len(test_defs)}] {test_name} ({test_type}) -> FAILED: {e}")

            if test_ids:
                print(f"\nAttaching {len(test_ids)} tests to agent...")
                try:
                    attach_tests_to_agent(api_key, agent_id, test_ids)
                    print(f"  Attached {len(test_ids)} tests")
                except Exception as e:
                    print(f"  Failed to attach tests: {e}")
                    print("  Tests were created but not attached. Attach manually or re-run.")

        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"\nAgent ID: {agent_id} ({share_status})")
        print(f"Tools deployed: {len(tool_mapping)}")
        if mcp_server_mapping:
            print(f"MCP servers deployed: {len(mcp_server_mapping)}")
        if kb_count:
            print(f"KB documents: {kb_count}")
        if test_ids:
            print(f"Tests created: {len(test_ids)}/{len(test_defs)}")

        if tool_mapping:
            print("\nTool mapping:")
            for name, tid in tool_mapping.items():
                print(f"  {name} -> {tid}")

        if mcp_server_mapping:
            print("\nMCP server mapping:")
            for name, sid in mcp_server_mapping.items():
                print(f"  {name} -> {sid}")

        if test_ids:
            print("\nTest mapping:")
            for i, tid in enumerate(test_ids):
                print(f"  {test_defs[i].get('name', f'test_{i+1}')} -> {tid}")

    except Exception as e:
        print(f"\nError creating agent: {e}")

        if tool_mapping:
            print("\nTools were already created:")
            for name, tid in tool_mapping.items():
                print(f"  {name} -> {tid}")
            print("\nYou may need to delete these tools manually if retrying.")

        if mcp_server_mapping:
            print("\nMCP servers were already created:")
            for name, sid in mcp_server_mapping.items():
                print(f"  {name} -> {sid}")
            print("You may need to delete these MCP servers manually if retrying.")

        sys.exit(1)


if __name__ == "__main__":
    main()
