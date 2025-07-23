#!/usr/bin/env python3
"""Comprehensive MCP diagnostic script to test functionality and identify issues."""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.interfaces.mcp_interface import MCPInterface
from src.interfaces.shared_state import shared_core


class MCPDiagnostic:
    """Diagnostic tool for MCP integration."""
    
    def __init__(self):
        self.results = []
        self.interface = None
        
    def log_result(self, test_name: str, status: str, details: dict):
        """Log test result."""
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.results.append(result)
        
        # Print immediate feedback
        icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if status != "success" and "error" in details:
            print(f"   Error: {details['error']}")
    
    async def test_initialization(self):
        """Test MCP interface initialization."""
        try:
            self.interface = MCPInterface()
            self.log_result("MCP Initialization", "success", {
                "server_name": self.interface.server.name,
                "tools_count": len(self.interface.tools_list)
            })
        except Exception as e:
            self.log_result("MCP Initialization", "error", {"error": str(e)})
            raise
    
    async def test_shared_state(self):
        """Test shared state initialization."""
        try:
            # Check if shared_core is properly initialized
            core_state = {
                "has_scenes": hasattr(shared_core, 'scenes'),
                "scenes_type": type(shared_core.scenes).__name__ if hasattr(shared_core, 'scenes') else None,
                "scenes_count": len(shared_core.scenes) if hasattr(shared_core, 'scenes') else 0,
                "current_scene": shared_core.current_scene.name if hasattr(shared_core, 'current_scene') and shared_core.current_scene else None
            }
            self.log_result("Shared State Check", "success", core_state)
        except Exception as e:
            self.log_result("Shared State Check", "error", {"error": str(e)})
    
    async def test_create_scene(self):
        """Test scene creation."""
        try:
            result = await self.interface.execute_tool("create_scene", {
                "name": "test_scene_diagnostic",
                "duration": 3.0,
                "background_color": "#1a1a1a"
            })
            
            result_data = json.loads(result.to_json())
            self.log_result("Create Scene", result_data["status"], result_data)
            return result_data["status"] == "success"
        except Exception as e:
            self.log_result("Create Scene", "error", {"error": str(e)})
            return False
    
    async def test_list_scenes(self):
        """Test listing scenes."""
        try:
            result = await self.interface.execute_tool("list_scenes", {})
            result_data = json.loads(result.to_json())
            self.log_result("List Scenes", result_data["status"], result_data)
        except Exception as e:
            self.log_result("List Scenes", "error", {"error": str(e)})
    
    async def test_add_text(self, scene_created: bool):
        """Test adding text object."""
        if not scene_created:
            self.log_result("Add Text", "skipped", {"reason": "No scene created"})
            return
            
        try:
            result = await self.interface.execute_tool("add_text", {
                "id": "test_text",
                "content": "Diagnostic Test",
                "position": [0, 2, 0]
            })
            result_data = json.loads(result.to_json())
            self.log_result("Add Text", result_data["status"], result_data)
        except Exception as e:
            self.log_result("Add Text", "error", {"error": str(e)})
    
    async def test_list_presets(self):
        """Test listing timeline presets (known working function)."""
        try:
            result = await self.interface.execute_tool("list_timeline_presets", {})
            result_data = json.loads(result.to_json())
            self.log_result("List Timeline Presets", result_data["status"], {
                "preset_count": len(result_data.get("data", {}).get("presets", [])) if result_data["status"] == "success" else 0
            })
        except Exception as e:
            self.log_result("List Timeline Presets", "error", {"error": str(e)})
    
    async def test_file_permissions(self):
        """Test file system permissions."""
        try:
            test_results = {}
            
            # Check user-data directory
            user_data_path = Path("user-data")
            test_results["user_data_exists"] = user_data_path.exists()
            test_results["user_data_writable"] = os.access(user_data_path, os.W_OK) if user_data_path.exists() else False
            
            # Check if we can create directories
            test_dir = user_data_path / "mcp_diagnostic_test"
            try:
                test_dir.mkdir(exist_ok=True)
                test_results["can_create_dirs"] = True
                test_dir.rmdir()
            except Exception as e:
                test_results["can_create_dirs"] = False
                test_results["mkdir_error"] = str(e)
            
            self.log_result("File Permissions", "success" if test_results.get("user_data_writable") else "warning", test_results)
        except Exception as e:
            self.log_result("File Permissions", "error", {"error": str(e)})
    
    async def test_parameter_handling(self):
        """Test various parameter formats."""
        test_cases = [
            {
                "name": "Empty dict",
                "tool": "list_scenes",
                "params": {}
            },
            {
                "name": "None params",
                "tool": "list_scenes", 
                "params": None
            },
            {
                "name": "Minimal params",
                "tool": "create_scene",
                "params": {"name": "minimal_test"}
            },
            {
                "name": "Full params",
                "tool": "create_scene",
                "params": {
                    "name": "full_test",
                    "duration": 5.0,
                    "background_color": "#000000",
                    "resolution": [1920, 1080],
                    "fps": 60
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                result = await self.interface.execute_tool(test_case["tool"], test_case["params"])
                result_data = json.loads(result.to_json())
                self.log_result(f"Parameter Test: {test_case['name']}", result_data["status"], {
                    "tool": test_case["tool"],
                    "params": test_case["params"],
                    "result": result_data.get("message", result_data.get("error"))
                })
            except Exception as e:
                self.log_result(f"Parameter Test: {test_case['name']}", "error", {
                    "tool": test_case["tool"],
                    "params": test_case["params"],
                    "error": str(e)
                })
    
    async def run_diagnostics(self):
        """Run all diagnostic tests."""
        print("=== MCP Diagnostic Test Suite ===\n")
        
        # Initialize
        await self.test_initialization()
        if not self.interface:
            print("\n❌ Failed to initialize MCP interface. Aborting further tests.")
            return
        
        # Test shared state
        await self.test_shared_state()
        
        # Test file permissions
        await self.test_file_permissions()
        
        # Test parameter handling
        await self.test_parameter_handling()
        
        # Test core functionality
        scene_created = await self.test_create_scene()
        await self.test_list_scenes()
        await self.test_add_text(scene_created)
        await self.test_list_presets()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate diagnostic report."""
        print("\n=== Diagnostic Report ===\n")
        
        # Summary
        success_count = sum(1 for r in self.results if r["status"] == "success")
        error_count = sum(1 for r in self.results if r["status"] == "error")
        warning_count = sum(1 for r in self.results if r["status"] == "warning")
        
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Success: {success_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⚠️  Warnings: {warning_count}")
        
        # Error details
        if error_count > 0:
            print("\n=== Error Details ===")
            for result in self.results:
                if result["status"] == "error":
                    print(f"\n{result['test']}:")
                    print(f"  Error: {result['details'].get('error', 'Unknown error')}")
        
        # Save full report
        report_path = Path("user-data") / f"mcp_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": len(self.results),
                    "success": success_count,
                    "errors": error_count,
                    "warnings": warning_count
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\nFull report saved to: {report_path}")


async def main():
    """Run diagnostic tests."""
    diagnostic = MCPDiagnostic()
    await diagnostic.run_diagnostics()


if __name__ == "__main__":
    asyncio.run(main())