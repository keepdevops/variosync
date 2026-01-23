#!/usr/bin/env python3
"""
VARIOSYNC Docker Multi-Stage Build Script (Python)
Alternative to bash script with more features and cross-platform support.
"""
import argparse
import subprocess
import sys
import os
from pathlib import Path


class Colors:
    """ANSI color codes."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def run_command(cmd, check=True, capture_output=False):
    """Run shell command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Command failed: {cmd}{Colors.NC}")
        print(f"{Colors.RED}   Error: {e}{Colors.NC}")
        sys.exit(1)


def check_docker():
    """Check if Docker is running."""
    result = run_command("docker info", check=False, capture_output=True)
    if result.returncode != 0:
        print(f"{Colors.RED}❌ Docker daemon is not running.{Colors.NC}")
        print("   Please start Docker Desktop or Docker daemon first.")
        sys.exit(1)


def check_docker_login():
    """Check if logged into Docker Hub."""
    result = run_command("docker info", check=False, capture_output=True)
    if "Username" not in result.stdout:
        print(f"{Colors.YELLOW}⚠️  Not logged into Docker Hub.{Colors.NC}")
        print("   Logging in...")
        run_command("docker login", check=True)


def check_dockerfile(dockerfile):
    """Check if Dockerfile exists."""
    if not Path(dockerfile).exists():
        print(f"{Colors.RED}❌ Dockerfile not found: {dockerfile}{Colors.NC}")
        sys.exit(1)


def build_image(
    version,
    username,
    dockerfile="Dockerfile.production",
    no_push=False,
    no_latest=False,
    no_cache=False,
    platform=None,
    multi_platform=False,
    bytecode=True
):
    """Build and optionally push Docker image."""
    
    image_name = f"{username}/variosync"
    image_tag = f"{image_name}:{version}"
    image_latest = f"{image_name}:latest"
    
    # Build cache options
    cache_opts = "--no-cache" if no_cache else ""
    
    # Platform options
    platform_opts = ""
    if platform:
        platform_opts = f"--platform {platform}"
    elif multi_platform:
        platform_opts = "--platform linux/amd64,linux/arm64"
        # Check buildx
        result = run_command("docker buildx version", check=False, capture_output=True)
        if result.returncode != 0:
            print(f"{Colors.RED}❌ Docker buildx not available.{Colors.NC}")
            print("   Install Docker Buildx for multi-platform builds.")
            sys.exit(1)
        
        # Create builder if needed
        result = run_command("docker buildx ls", check=False, capture_output=True)
        if "multiarch" not in result.stdout:
            print("🔧 Creating buildx builder...")
            run_command("docker buildx create --name multiarch --use --bootstrap", check=False)
        run_command("docker buildx use multiarch", check=False)
    
    # Print header
    print("")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     VARIOSYNC Docker Multi-Stage Build               ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print("")
    print(f"📦 Image: {image_tag}")
    if not no_latest:
        print(f"🏷️  Latest: {image_latest}")
    print(f"📄 Dockerfile: {dockerfile}")
    if bytecode:
        print(f"{Colors.BLUE}🔧 Bytecode compilation: Enabled{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Bytecode compilation: Disabled{Colors.NC}")
    if no_push:
        print(f"{Colors.YELLOW}⚠️  Build only mode (no push){Colors.NC}")
    if platform_opts:
        print(f"{Colors.BLUE}📱 Platform: {platform_opts}{Colors.NC}")
    print("")
    
    # Check prerequisites
    check_docker()
    check_dockerfile(dockerfile)
    if not no_push:
        check_docker_login()
    
    # Build command
    print("🔨 Building production image (multi-stage)...")
    print(f"{Colors.BLUE}   Stage 1: Builder (installing dependencies){Colors.NC}")
    print(f"{Colors.BLUE}   Stage 2: Final (copying packages + app code){Colors.NC}")
    print("")
    
    if multi_platform:
        # Multi-platform build with buildx
        build_cmd = f"docker buildx build {platform_opts} {cache_opts} -f {dockerfile} -t {image_tag}"
        
        if not no_latest:
            build_cmd += f" -t {image_latest}"
        
        if not no_push:
            build_cmd += " --push"
        else:
            build_cmd += " --load"
        
        build_cmd += " ."
        
        run_command(build_cmd)
    else:
        # Single platform build
        build_cmd = f"docker build {platform_opts} {cache_opts} -f {dockerfile} -t {image_tag} ."
        run_command(build_cmd)
        
        print(f"{Colors.GREEN}✅ Build successful!{Colors.NC}")
        
        # Tag as latest
        if not no_latest:
            print("🏷️  Tagging as latest...")
            run_command(f"docker tag {image_tag} {image_latest}")
        
        # Push
        if not no_push:
            print("📤 Pushing version tag...")
            run_command(f"docker push {image_tag}")
            
            if not no_latest:
                print("📤 Pushing latest tag...")
                run_command(f"docker push {image_latest}")
    
    # Show image info
    print("")
    if not no_push:
        print(f"{Colors.GREEN}✅ Successfully pushed to Docker Hub!{Colors.NC}")
    else:
        print(f"{Colors.GREEN}✅ Build completed successfully!{Colors.NC}")
    
    print("")
    print("📊 Image Information:")
    run_command(f"docker images {image_tag} --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}'")
    
    print("")
    if not no_push:
        print("📋 Next steps:")
        print(f"   1. Go to Render dashboard")
        print(f"   2. Update service to use: docker.io/{image_tag}")
        print(f"   3. Or enable auto-deploy with webhook")
        print("")
        print(f"🔗 Image URL: https://hub.docker.com/r/{username}/variosync")
    else:
        print("📋 Next steps:")
        print(f"   1. Test the image locally:")
        print(f"      docker run -p 8080:8080 {image_tag}")
        print(f"   2. When ready, push with:")
        print(f"      docker push {image_tag}")
        if not no_latest:
            print(f"      docker push {image_latest}")
    print("")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build and push VARIOSYNC Docker image (multi-stage)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1.0.0 yourusername
  %(prog)s 1.0.0 yourusername --no-push
  %(prog)s 1.0.0 yourusername --platform linux/arm64
  %(prog)s 1.0.0 yourusername --multi-platform
        """
    )
    
    parser.add_argument("version", help="Version tag (e.g., 1.0.0)")
    parser.add_argument("username", help="Docker Hub username")
    parser.add_argument("--dockerfile", "-f", default="Dockerfile.production",
                       help="Dockerfile to use (default: Dockerfile.production)")
    parser.add_argument("--no-push", action="store_true",
                       help="Build only, don't push to Docker Hub")
    parser.add_argument("--no-latest", action="store_true",
                       help="Don't tag/push as :latest")
    parser.add_argument("--no-cache", action="store_true",
                       help="Build without cache")
    parser.add_argument("--platform", help="Build for specific platform (e.g., linux/amd64)")
    parser.add_argument("--multi-platform", action="store_true",
                       help="Build for multiple platforms (requires buildx)")
    parser.add_argument("--no-bytecode", action="store_true",
                       help="Disable bytecode compilation")
    
    args = parser.parse_args()
    
    build_image(
        version=args.version,
        username=args.username,
        dockerfile=args.dockerfile,
        no_push=args.no_push,
        no_latest=args.no_latest,
        no_cache=args.no_cache,
        platform=args.platform,
        multi_platform=args.multi_platform,
        bytecode=not args.no_bytecode
    )


if __name__ == "__main__":
    main()
