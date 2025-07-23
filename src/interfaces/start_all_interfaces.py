#!/usr/bin/env python3
"""Start All Manim Studio Interfaces

This script can launch multiple interfaces simultaneously in separate processes.
Useful for development and testing.

Usage:
    python start_all_interfaces.py                    # Start API + GUI
    python start_all_interfaces.py --all              # Start API + GUI + MCP  
    python start_all_interfaces.py --api --gui        # Start specific interfaces
    python start_all_interfaces.py --ports 8000 7860  # Custom ports
"""

import argparse
import subprocess
import time
import signal
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

class InterfaceManager:
    """Manages multiple interface processes."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.interface_info: Dict[str, Dict] = {}
        
    def start_interface(self, interface: str, **kwargs) -> Optional[subprocess.Popen]:
        """Start a specific interface in a subprocess."""
        
        if interface == "api":
            port = kwargs.get("api_port", 8000)
            cmd = [sys.executable, str(project_root / "main.py"), "api", "--port", str(port), "--host", "0.0.0.0"]
            if kwargs.get("reload", False):
                cmd.append("--reload")
                
        elif interface == "gui":
            port = kwargs.get("gui_port", 7860)
            cmd = [sys.executable, str(project_root / "main.py"), "gui", "--port", str(port), "--host", "0.0.0.0"]
            if kwargs.get("share", False):
                cmd.append("--share")
                
        elif interface == "mcp":
            cmd = [sys.executable, str(project_root / "main.py"), "mcp"]
            
        else:
            print(f"❌ Unknown interface: {interface}")
            return None
            
        try:
            print(f"🚀 Starting {interface.upper()} interface...")
            if interface in ["api", "gui"]:
                port = kwargs.get(f"{interface}_port", 8000 if interface == "api" else 7860)
                print(f"   URL: http://localhost:{port}")
                self.interface_info[interface] = {"port": port, "url": f"http://localhost:{port}"}
            
            process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            self.interface_info[interface] = {
                **self.interface_info.get(interface, {}),
                "process": process,
                "pid": process.pid
            }
            
            return process
            
        except Exception as e:
            print(f"❌ Failed to start {interface}: {e}")
            return None
    
    def wait_for_startup(self, timeout: int = 30):
        """Wait for interfaces to start up."""
        print(f"⏳ Waiting for interfaces to start (timeout: {timeout}s)...")
        
        import requests
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_ready = True
            
            for interface, info in self.interface_info.items():
                if interface in ["api", "gui"] and "url" in info:
                    try:
                        response = requests.get(f"{info['url']}/health" if interface == "api" else info["url"], timeout=1)
                        if interface == "api" and response.status_code != 200:
                            all_ready = False
                        elif interface == "gui" and response.status_code not in [200, 404]:  # Gradio might return 404 for root
                            all_ready = False
                    except:
                        all_ready = False
                        
            if all_ready:
                print("✅ All interfaces are ready!")
                return True
                
            time.sleep(1)
            
        print("⚠️  Timeout waiting for interfaces to start")
        return False
    
    def show_status(self):
        """Show status of all running interfaces."""
        print("\n" + "=" * 60)
        print("🎭 Manim Studio - Interface Status")
        print("=" * 60)
        
        for interface, info in self.interface_info.items():
            process = info.get("process")
            if process:
                status = "🟢 Running" if process.poll() is None else "🔴 Stopped"
                print(f"{interface.upper():<8} {status:<12} PID: {info.get('pid', 'N/A')}")
                
                if "url" in info:
                    print(f"         {'URL:':<12} {info['url']}")
                    
                if interface == "api":
                    print(f"         {'Docs:':<12} {info['url']}/docs")
                    print(f"         {'OpenAPI:':<12} {info['url']}/openapi.json")
                    
        print("\n📋 Quick Access:")
        for interface, info in self.interface_info.items():
            if "url" in info:
                if interface == "api":
                    print(f"   API Docs: {info['url']}/docs")
                elif interface == "gui":  
                    print(f"   GUI Interface: {info['url']}")
                    
        print("\n🛑 Stop all: Ctrl+C")
    
    def cleanup(self):
        """Clean up all processes."""
        print("\n🧹 Cleaning up processes...")
        
        for process in self.processes:
            if process.poll() is None:  # Still running
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except:
                    pass
                    
        print("✅ All processes terminated")


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Start multiple Manim Studio interfaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_all_interfaces.py                     # API + GUI (default)
  python start_all_interfaces.py --all               # API + GUI + MCP
  python start_all_interfaces.py --api --gui         # Specific interfaces
  python start_all_interfaces.py --ports 8001 7861  # Custom ports
  python start_all_interfaces.py --api --reload      # API with auto-reload
        """
    )
    
    # Interface selection
    parser.add_argument("--api", action="store_true", help="Start API interface")
    parser.add_argument("--gui", action="store_true", help="Start GUI interface") 
    parser.add_argument("--mcp", action="store_true", help="Start MCP interface")
    parser.add_argument("--all", action="store_true", help="Start all interfaces")
    
    # Configuration
    parser.add_argument("--ports", nargs=2, type=int, metavar=("API_PORT", "GUI_PORT"),
                       default=[8000, 7860], help="Custom ports for API and GUI")
    parser.add_argument("--reload", action="store_true", help="Enable API auto-reload")
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    parser.add_argument("--timeout", type=int, default=30, help="Startup timeout in seconds")
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Determine which interfaces to start
    interfaces_to_start = []
    
    if args.all:
        interfaces_to_start = ["api", "gui", "mcp"]
    elif args.api or args.gui or args.mcp:
        if args.api:
            interfaces_to_start.append("api")
        if args.gui:
            interfaces_to_start.append("gui")
        if args.mcp:
            interfaces_to_start.append("mcp")
    else:
        # Default: API + GUI
        interfaces_to_start = ["api", "gui"]
        print("🔧 No interfaces specified, starting default: API + GUI")
        print("   Use --help to see all options")
    
    print(f"🎭 Starting Manim Studio interfaces: {', '.join(interfaces_to_start)}")
    
    # Check dependencies
    missing_deps = []
    if "api" in interfaces_to_start:
        try:
            import fastapi, uvicorn
        except ImportError:
            missing_deps.append("API: pip install fastapi uvicorn")
    
    if "gui" in interfaces_to_start:
        try:
            import gradio
        except ImportError:
            missing_deps.append("GUI: pip install gradio")
            
    if "mcp" in interfaces_to_start:
        try:
            import mcp
        except ImportError:
            missing_deps.append("MCP: pip install mcp")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   {dep}")
        return 1
    
    # Create interface manager
    manager = InterfaceManager()
    
    # Setup signal handler
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}")
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start interfaces
        api_port, gui_port = args.ports
        
        for interface in interfaces_to_start:
            manager.start_interface(
                interface,
                api_port=api_port,
                gui_port=gui_port,
                reload=args.reload,
                share=args.share
            )
            time.sleep(1)  # Stagger startup
        
        # Wait for startup
        if "api" in interfaces_to_start or "gui" in interfaces_to_start:
            manager.wait_for_startup(args.timeout)
        
        # Show status
        manager.show_status()
        
        # Keep running
        print("\n⏳ Interfaces running. Press Ctrl+C to stop all.")
        
        while True:
            time.sleep(1)
            
            # Check if any process died
            for interface, info in manager.interface_info.items():
                process = info.get("process")
                if process and process.poll() is not None:
                    print(f"⚠️  {interface.upper()} interface stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        manager.cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())