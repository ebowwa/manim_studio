#!/usr/bin/env python3
"""Unified Launcher for Manim Studio Interfaces

This launcher can start any of the available interfaces:
- CLI: Command-line interface for rendering YAML scenes
- API: REST API server 
- GUI: Web-based Gradio interface
- MCP: Model Context Protocol server for AI assistants

Usage:
    python src/launcher.py cli scene.yaml -q l -p       # CLI interface
    python src/launcher.py api --port 8000              # API server
    python src/launcher.py gui --port 7860              # GUI interface  
    python src/launcher.py mcp                          # MCP server
    python src/launcher.py --help                       # Show help
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional, NoReturn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the launcher."""
    parser = argparse.ArgumentParser(
        description="Manim Studio - Unified Interface Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CLI Interface (render YAML scenes)
  python src/launcher.py cli scenes/my_scene.yaml -q l -p
  
  # API Server
  python src/launcher.py api --port 8000 --host 0.0.0.0
  
  # GUI Interface  
  python src/launcher.py gui --port 7860 --share
  
  # MCP Server (for AI assistants)
  python src/launcher.py mcp
  
  # Show available interfaces
  python src/launcher.py --list-interfaces
        """
    )
    
    parser.add_argument(
        "--list-interfaces", 
        action="store_true",
        help="List all available interfaces"
    )
    
    # Interface selection
    subparsers = parser.add_subparsers(dest="interface", help="Interface to launch")
    
    # CLI Interface
    cli_parser = subparsers.add_parser("cli", help="Command-line interface for rendering")
    cli_parser.add_argument("scene_file", nargs="?", help="YAML scene file to render")
    cli_parser.add_argument("-q", "--quality", choices=["l", "m", "h", "p", "k"], 
                           default="h", help="Render quality")
    cli_parser.add_argument("-p", "--preview", action="store_true", 
                           help="Preview video after rendering")
    cli_parser.add_argument("--fps", type=int, help="Frames per second")
    cli_parser.add_argument("-o", "--output", help="Output filename")
    cli_parser.add_argument("--validate-only", action="store_true",
                           help="Validate YAML without rendering")
    cli_parser.add_argument("--verbose", action="store_true",
                           help="Show detailed validation results")
    
    # API Interface
    api_parser = subparsers.add_parser("api", help="REST API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    api_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    api_parser.add_argument("--log-level", default="info", 
                           choices=["debug", "info", "warning", "error"],
                           help="Log level")
    
    # GUI Interface
    gui_parser = subparsers.add_parser("gui", help="Web-based GUI interface")
    gui_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    gui_parser.add_argument("--port", type=int, default=7860, help="Port to bind to")
    gui_parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    gui_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # MCP Interface
    mcp_parser = subparsers.add_parser("mcp", help="Model Context Protocol server")
    mcp_parser.add_argument("--log-level", default="info",
                           choices=["debug", "info", "warning", "error"],
                           help="Log level")
    
    return parser


def launch_cli(args: argparse.Namespace) -> int:
    """Launch the CLI interface."""
    print("🖥️  Starting Manim Studio CLI Interface...")
    
    if not args.scene_file:
        print("❌ Error: Scene file required for CLI interface")
        print("Usage: python src/launcher.py cli scenes/my_scene.yaml -q l -p")
        return 1
    
    # Import and run CLI
    try:
        from interfaces.cli.cli import main as cli_main
        
        # Build CLI arguments
        cli_args = [args.scene_file]
        
        if args.quality:
            cli_args.extend(["-q", args.quality])
        if args.preview:
            cli_args.append("-p")
        if args.fps:
            cli_args.extend(["--fps", str(args.fps)])
        if args.output:
            cli_args.extend(["-o", args.output])
        if args.validate_only:
            cli_args.append("--validate-only")
        if args.verbose:
            cli_args.append("--verbose")
        
        # Override sys.argv for CLI
        original_argv = sys.argv
        sys.argv = ["manim-studio"] + cli_args
        
        try:
            cli_main()
            return 0
        finally:
            sys.argv = original_argv
            
    except ImportError as e:
        print(f"❌ Failed to import CLI: {e}")
        return 1
    except Exception as e:
        print(f"❌ CLI failed: {e}")
        return 1


def launch_api(args: argparse.Namespace) -> int:
    """Launch the API interface."""
    print(f"🔗 Starting Manim Studio API Server on {args.host}:{args.port}...")
    
    try:
        from interfaces.api_interface import EnhancedAPIInterface
        
        api = EnhancedAPIInterface()
        api.run(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level
        )
        return 0
        
    except ImportError as e:
        print(f"❌ Failed to import API interface: {e}")
        print("Install required dependencies: pip install fastapi uvicorn")
        return 1
    except Exception as e:
        print(f"❌ API server failed: {e}")
        return 1


def launch_gui(args: argparse.Namespace) -> int:
    """Launch the GUI interface."""
    print(f"🌐 Starting Manim Studio GUI Interface on {args.host}:{args.port}...")
    
    try:
        from interfaces.gradio.gui_interface import GUIInterface
        
        gui = GUIInterface()
        gui.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            debug=args.debug
        )
        return 0
        
    except ImportError as e:
        print(f"❌ Failed to import GUI interface: {e}")
        print("Install required dependencies: pip install gradio")
        return 1
    except Exception as e:
        print(f"❌ GUI interface failed: {e}")
        return 1


def launch_mcp(args: argparse.Namespace) -> int:
    """Launch the MCP interface."""
    print("🤖 Starting Manim Studio MCP Server...")
    
    try:
        import asyncio
        from interfaces.mcp_interface import main as mcp_main
        
        # Set log level
        import logging
        logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
        
        asyncio.run(mcp_main())
        return 0
        
    except ImportError as e:
        print(f"❌ Failed to import MCP interface: {e}")
        print("Install required dependencies: pip install mcp")
        return 1
    except Exception as e:
        print(f"❌ MCP server failed: {e}")
        return 1


def list_interfaces() -> None:
    """List all available interfaces."""
    print("🎭 Manim Studio - Available Interfaces")
    print("=" * 50)
    
    interfaces = [
        {
            "name": "CLI",
            "command": "python src/launcher.py cli scenes/my_scene.yaml -q l -p",
            "description": "Command-line interface for rendering YAML scenes",
            "features": ["YAML scene rendering", "Quality control", "Validation", "Preview"]
        },
        {
            "name": "API", 
            "command": "python src/launcher.py api --port 8000",
            "description": "REST API server for programmatic access",
            "features": ["REST endpoints", "OpenAPI docs", "Batch operations", "External integration"]
        },
        {
            "name": "GUI",
            "command": "python src/launcher.py gui --port 7860",
            "description": "Web-based visual interface using Gradio",
            "features": ["Visual forms", "Real-time feedback", "No coding required", "Web accessible"]
        },
        {
            "name": "MCP",
            "command": "python src/launcher.py mcp", 
            "description": "Model Context Protocol server for AI assistants",
            "features": ["AI assistant integration", "Tool-based interface", "Claude/ChatGPT support", "API discovery"]
        }
    ]
    
    for interface in interfaces:
        print(f"\n📌 {interface['name']} Interface")
        print(f"   {interface['description']}")
        print(f"   Command: {interface['command']}")
        print(f"   Features: {', '.join(interface['features'])}")
    
    print(f"\n🔗 All interfaces use the same shared features for consistency!")
    print(f"📖 See src/interfaces/README.md for detailed documentation")


def main() -> int:
    """Main launcher entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle list interfaces
    if args.list_interfaces:
        list_interfaces()
        return 0
    
    # Handle no interface specified
    if not args.interface:
        print("🎭 Manim Studio - Unified Interface Launcher")
        print("\nNo interface specified. Use --help for usage or --list-interfaces to see options.")
        print("\nQuick start:")
        print("  python src/launcher.py cli scenes/my_scene.yaml -q l -p   # CLI")
        print("  python src/launcher.py api                                # API")
        print("  python src/launcher.py gui                                # GUI") 
        print("  python src/launcher.py mcp                                # MCP")
        return 1
    
    # Launch the appropriate interface
    if args.interface == "cli":
        return launch_cli(args)
    elif args.interface == "api":
        return launch_api(args)
    elif args.interface == "gui":
        return launch_gui(args)
    elif args.interface == "mcp":
        return launch_mcp(args)
    else:
        print(f"❌ Unknown interface: {args.interface}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Launcher interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Launcher failed: {e}")
        sys.exit(1)