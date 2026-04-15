#!/usr/bin/env python3
"""
ElevenLabs Agent JSON Validator

Validates ElevenLabs conversational AI agent JSON files for common errors
before deployment. Run this after generating JSON to catch issues early.

Usage:
    python validate_el_json.py <json_file>
    
Exit codes:
    0 - No errors (warnings may exist)
    1 - Errors found (will fail deployment)
"""

import json
import sys
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class ValidationResult:
    def __init__(self):
        self.errors: List[Tuple[str, str, str]] = []  # (code, message, fix)
        self.warnings: List[Tuple[str, str]] = []  # (code, message)
    
    def add_error(self, code: str, message: str, fix: str):
        self.errors.append((code, message, fix))
    
    def add_warning(self, code: str, message: str):
        self.warnings.append((code, message))
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0


def validate_edges(data: Dict[str, Any], result: ValidationResult):
    """Validate edge constraints."""
    
    workflow = data.get("workflow", {})
    edges = workflow.get("edges", {})
    
    if not edges:
        return
    
    # Track node pairs for duplicate detection
    node_pairs: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    
    for edge_id, edge in edges.items():
        source = edge.get("source", "")
        target = edge.get("target", "")
        
        # E001: Self-loop detection
        if source == target:
            result.add_error(
                "E001",
                f"Self-loop: {source} → {target}\n     Edge: {edge_id}",
                "Remove edge, handle looping behavior in node's prompt"
            )
            continue
        
        # Track for duplicate detection (normalize to sorted tuple)
        pair = tuple(sorted([source, target]))
        node_pairs[pair].append(edge_id)
        
        # E003: Check for unconditional backward_condition
        backward = edge.get("backward_condition")
        if backward and backward.get("type") == "unconditional":
            result.add_error(
                "E003",
                f"Unconditional backward_condition: {source} ↔ {target}\n     Edge: {edge_id}",
                "Change backward_condition to LLM type (unconditional would create infinite loop)"
            )
        
        # W001: Missing label on forward_condition
        forward = edge.get("forward_condition")
        if forward and forward.get("type") == "llm" and not forward.get("label"):
            result.add_warning(
                "W001",
                f"Missing label on forward_condition: {edge_id}"
            )
        
        # W002: Missing label on backward_condition  
        if backward and backward.get("type") == "llm" and not backward.get("label"):
            result.add_warning(
                "W002",
                f"Missing label on backward_condition: {edge_id}"
            )
    
    # E002: Duplicate edge detection (same node pair)
    for pair, edge_ids in node_pairs.items():
        if len(edge_ids) > 1:
            result.add_error(
                "E002",
                f"Duplicate edges between {pair[0]} ↔ {pair[1]}\n     Edges: {', '.join(edge_ids)}",
                "Merge into single edge with combined LLM condition (use forward_condition + backward_condition if bidirectional)"
            )


def validate_terminal_nodes(data: Dict[str, Any], result: ValidationResult):
    """Check that terminal nodes don't have outgoing edges."""
    
    workflow = data.get("workflow", {})
    nodes = workflow.get("nodes", {})
    edges = workflow.get("edges", {})
    
    if not nodes or not edges:
        return
    
    # Find terminal node types
    terminal_types = {"phone_number", "end"}
    terminal_nodes = set()
    
    for node_id, node in nodes.items():
        node_type = node.get("type", "")
        if node_type in terminal_types:
            terminal_nodes.add(node_id)
    
    # Check for outgoing edges from terminal nodes
    for edge_id, edge in edges.items():
        source = edge.get("source", "")
        if source in terminal_nodes:
            result.add_error(
                "E004",
                f"Terminal node has outgoing edge: {source}\n     Edge: {edge_id}",
                "Remove edge - terminal nodes (phone_number, end) cannot have outgoing edges"
            )


def validate_transfer_types(data: Dict[str, Any], result: ValidationResult):
    """Validate transfer_type values in tools."""
    
    valid_types = {"blind", "conference", "sip_refer"}
    
    # Check in conversation_config.agent.prompt.tools
    tools = (data.get("conversation_config", {})
             .get("agent", {})
             .get("prompt", {})
             .get("tools", []))
    
    for i, tool in enumerate(tools):
        system_tool = tool.get("system", {})
        params = system_tool.get("params", {})
        transfer_config = params.get("transfer_to_number", {})
        transfers = transfer_config.get("transfers", [])
        
        for j, transfer in enumerate(transfers):
            transfer_type = transfer.get("transfer_type", "")
            if transfer_type and transfer_type not in valid_types:
                result.add_error(
                    "E005",
                    f"Invalid transfer_type: '{transfer_type}'\n     Location: tools[{i}].system.params.transfer_to_number.transfers[{j}]",
                    f"Use 'conference' (for warm) or 'blind' (for cold). Valid values: {valid_types}"
                )


def validate_url_placeholders(data: Dict[str, Any], result: ValidationResult):
    """Check for URL path placeholders that need path_params_schema."""
    
    # Pattern to match {{variable}} in URL paths
    placeholder_pattern = re.compile(r'\{\{[^}]+\}\}')
    
    tools = (data.get("conversation_config", {})
             .get("agent", {})
             .get("prompt", {})
             .get("tools", []))
    
    for i, tool in enumerate(tools):
        webhook = tool.get("webhook", {})
        api_schema = webhook.get("api_schema", {})
        url = api_schema.get("url", "")
        
        if url and placeholder_pattern.search(url):
            # Check if it's in the path (not query string)
            url_path = url.split("?")[0]
            if placeholder_pattern.search(url_path):
                placeholders = placeholder_pattern.findall(url_path)
                result.add_error(
                    "E006",
                    f"URL path has placeholders: {url_path}\n     Placeholders: {', '.join(placeholders)}\n     Location: tools[{i}].webhook.api_schema.url",
                    "Use static URL and move dynamic values to request_body_schema"
                )


def _collect_tool_schemas(data: Dict[str, Any]) -> List[Tuple[str, str, Dict]]:
    """Gather all (tool_name, schema_location, properties_dict) from webhook tools."""
    results = []
    VALUE_SOURCE_FIELDS = {"description", "constant_value", "dynamic_variable", "is_system_provided"}

    def walk_properties(props: Dict, tool_name: str, path: str):
        for prop_name, prop_def in props.items():
            if not isinstance(prop_def, dict):
                continue
            results.append((tool_name, f"{path}.{prop_name}", prop_def))
            if prop_def.get("type") == "object" and "properties" in prop_def:
                walk_properties(prop_def["properties"], tool_name, f"{path}.{prop_name}")
            if prop_def.get("type") == "array" and isinstance(prop_def.get("items"), dict):
                items = prop_def["items"]
                if items.get("type") == "object" and "properties" in items:
                    walk_properties(items["properties"], tool_name, f"{path}.{prop_name}.items")

    tools = (data.get("conversation_config", {})
             .get("agent", {})
             .get("prompt", {})
             .get("tools", []))

    for tool in tools:
        if tool.get("type") != "webhook":
            continue
        tool_name = tool.get("name", "unnamed")
        for schema_key in ("request_body_schema", "query_params_schema"):
            schema = tool.get("api_schema", {}).get(schema_key, {})
            props = schema.get("properties", {})
            if props:
                walk_properties(props, tool_name, f"{tool_name}.{schema_key}")

    return results


def validate_tool_properties(data: Dict[str, Any], result: ValidationResult):
    """Validate that webhook tool properties have required 'type' field."""
    VALUE_SOURCE_FIELDS = {"description", "constant_value", "dynamic_variable", "is_system_provided"}

    for tool_name, prop_path, prop_def in _collect_tool_schemas(data):
        has_type = "type" in prop_def
        value_sources = VALUE_SOURCE_FIELDS & prop_def.keys()

        if not has_type and value_sources:
            result.add_error(
                "E010",
                f"Property missing 'type': {prop_path}\n"
                f"     Has: {', '.join(value_sources)} but no 'type' field",
                "Add \"type\": \"string\" (or appropriate type) alongside the value source field. "
                "The API discriminator requires 'type' on every property."
            )

        if not has_type and not value_sources:
            result.add_error(
                "E010",
                f"Property missing 'type' and value source: {prop_path}",
                "Add \"type\" and one of: description, constant_value, dynamic_variable, is_system_provided"
            )


def validate_json_structure(data: Dict[str, Any], result: ValidationResult):
    """Validate basic JSON structure."""
    
    # Check for required top-level keys
    if "conversation_config" not in data:
        result.add_error(
            "E007",
            "Missing 'conversation_config' at root level",
            "Add conversation_config with agent configuration"
        )
    
    # Check workflow structure if present
    if "workflow" in data:
        workflow = data["workflow"]
        
        if "nodes" not in workflow:
            result.add_error(
                "E008",
                "Missing 'nodes' in workflow",
                "Add nodes object to workflow"
            )
        
        if "edges" not in workflow:
            result.add_error(
                "E009",
                "Missing 'edges' in workflow",
                "Add edges object to workflow"
            )


def validate_file(filepath: str) -> ValidationResult:
    """Run all validations on a JSON file."""
    
    result = ValidationResult()
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error("E000", f"Invalid JSON: {e}", "Fix JSON syntax errors")
        return result
    except FileNotFoundError:
        result.add_error("E000", f"File not found: {filepath}", "Check file path")
        return result
    
    # Run all validations
    validate_json_structure(data, result)
    validate_edges(data, result)
    validate_terminal_nodes(data, result)
    validate_transfer_types(data, result)
    validate_url_placeholders(data, result)
    validate_tool_properties(data, result)
    
    return result


def print_results(filepath: str, result: ValidationResult):
    """Print validation results in a readable format."""
    
    print(f"\nValidating: {filepath}")
    print("=" * 60)
    
    if result.errors:
        print("\nERRORS:")
        for code, message, fix in result.errors:
            print(f"  ❌ [{code}] {message}")
            print(f"     FIX: {fix}")
            print()
    
    if result.warnings:
        print("\nWARNINGS:")
        for code, message in result.warnings:
            print(f"  ⚠️  [{code}] {message}")
        print()
    
    if not result.errors and not result.warnings:
        print("\n✅ No issues found!")
    
    print("=" * 60)
    print(f"Result: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
    
    if result.has_errors():
        print("Status: FAILED - Fix errors before deployment")
    else:
        print("Status: PASSED - Ready for deployment")


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_el_json.py <json_file>")
        print("       python validate_el_json.py *.json  (validate multiple files)")
        sys.exit(1)
    
    all_passed = True
    
    for filepath in sys.argv[1:]:
        result = validate_file(filepath)
        print_results(filepath, result)
        
        if result.has_errors():
            all_passed = False
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
