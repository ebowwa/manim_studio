#!/usr/bin/env python3
"""
API Discovery Demo

This script demonstrates how the MCP interface can discover and interact with 
the REST API endpoints automatically.

Usage:
1. Start the API server: python src/interfaces/api_interface.py
2. Run this demo: python examples/api_discovery_demo.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from interfaces.mcp_interface import MCPInterface


async def demo_api_discovery():
    """Demonstrate API discovery capabilities."""
    print("🔍 API Discovery Demo")
    print("=" * 50)
    
    # Create MCP interface instance
    mcp = MCPInterface()
    
    # 1. Discover API endpoints
    print("\n1. Discovering API endpoints...")
    discovery_result = await mcp._discover_api_endpoints(
        api_base_url="http://localhost:8000",
        include_schemas=False
    )
    
    if discovery_result.status == "success":
        data = discovery_result.data
        print(f"✅ Found {data['total_endpoints']} endpoints")
        print(f"📖 API: {data['api_info']['title']} v{data['api_info']['version']}")
        
        # Show some endpoints
        print("\n📍 Available endpoints:")
        for endpoint in data['endpoints'][:10]:  # Show first 10
            print(f"  {endpoint['method']} {endpoint['path']} - {endpoint['summary']}")
        
        if len(data['endpoints']) > 10:
            print(f"  ... and {len(data['endpoints']) - 10} more")
            
    else:
        print(f"❌ Discovery failed: {discovery_result.error}")
        print("Make sure the API server is running: python src/interfaces/api_interface.py")
        return
    
    # 2. Test API health check
    print("\n2. Testing API health check...")
    health_result = await mcp._call_api_endpoint("/health")
    
    if health_result.status == "success":
        response = health_result.data['response']
        print(f"✅ API Health: {response['status']} - {response['message']}")
    else:
        print(f"❌ Health check failed: {health_result.error}")
    
    # 3. Create a scene via API
    print("\n3. Creating scene via API...")
    scene_data = {
        "name": "APIDiscoveryDemo",
        "duration": 5.0,
        "background_color": "#2a2a2a",
        "resolution": [1280, 720],
        "fps": 30
    }
    
    create_result = await mcp._call_api_endpoint(
        endpoint="/scenes",
        method="POST",
        data=scene_data
    )
    
    if create_result.status == "success":
        response_data = create_result.data['response']
        if response_data.get('status') == 'success':
            scene_info = response_data['data']
            print(f"✅ Scene created: {scene_info['name']}")
            print(f"   Duration: {scene_info['duration']}s")
            print(f"   Resolution: {scene_info['resolution']}")
        else:
            print(f"❌ Scene creation failed: {response_data.get('error', 'Unknown error')}")
    else:
        print(f"❌ API call failed: {create_result.error}")
    
    # 4. List scenes
    print("\n4. Listing all scenes...")
    list_result = await mcp._call_api_endpoint("/scenes")
    
    if list_result.status == "success":
        response_data = list_result.data['response']
        if response_data.get('status') == 'success':
            scenes_data = response_data['data']
            print(f"✅ Found {scenes_data['total']} scenes:")
            for scene_name in scenes_data['scenes']:
                print(f"   📄 {scene_name}")
            if scenes_data['current_scene']:
                print(f"   👉 Current: {scenes_data['current_scene']}")
        else:
            print(f"❌ Failed to list scenes: {response_data.get('error', 'Unknown error')}")
    else:
        print(f"❌ API call failed: {list_result.error}")
    
    # 5. Get available animation types
    print("\n5. Getting available animation types...")
    types_result = await mcp._call_api_endpoint("/animation-types")
    
    if types_result.status == "success":
        anim_types = types_result.data['response']
        print(f"✅ Available animation types ({len(anim_types)}):")
        print(f"   {', '.join(anim_types)}")
    else:
        print(f"❌ Failed to get animation types: {types_result.error}")
    
    print("\n" + "=" * 50)
    print("🎉 API Discovery Demo Complete!")
    print("\nThis demonstrates how MCP can:")
    print("• Automatically discover API endpoints")
    print("• Call any endpoint with proper data")
    print("• Combine MCP tools with direct API access")
    print("• Enable hybrid workflows and external integrations")


async def demo_with_schemas():
    """Demonstrate API discovery with detailed schemas."""
    print("\n🔍 Detailed API Discovery (with schemas)")
    print("=" * 50)
    
    mcp = MCPInterface()
    
    # Get detailed API info with schemas
    discovery_result = await mcp._discover_api_endpoints(
        api_base_url="http://localhost:8000",
        include_schemas=True
    )
    
    if discovery_result.status == "success":
        data = discovery_result.data
        
        print(f"📊 API Schemas ({len(data.get('schemas', {}))}):")
        for schema_name in list(data.get('schemas', {}).keys())[:5]:
            print(f"   📋 {schema_name}")
        
        if len(data.get('schemas', {})) > 5:
            print(f"   ... and {len(data.get('schemas', {})) - 5} more schemas")
        
        # Show endpoint with most detail
        scene_endpoints = [ep for ep in data['endpoints'] if 'scene' in ep['path'].lower()]
        if scene_endpoints:
            print(f"\n📍 Scene-related endpoints:")
            for ep in scene_endpoints:
                print(f"   {ep['method']} {ep['path']} - {ep['summary']}")
    else:
        print(f"❌ Detailed discovery failed: {discovery_result.error}")


if __name__ == "__main__":
    print("Starting API Discovery Demo...")
    print("Make sure the API server is running on port 8000")
    print("Start it with: python src/interfaces/api_interface.py")
    
    try:
        asyncio.run(demo_api_discovery())
        
        # Optional: Run detailed demo
        print("\nWould you like to see detailed schema information? (y/n)")
        if input().lower().startswith('y'):
            asyncio.run(demo_with_schemas())
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure the API server is running and accessible")