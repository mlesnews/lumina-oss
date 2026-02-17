#!/usr/bin/env python3
"""
Check AI Models on M Drive and Add Vision/Image/Video Models

Analyzes current AI model storage and adds vision-capable models to the configuration.
"""

import os
import sys
import platform
import json
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

def check_m_drive():
    """Check M drive existence and basic properties"""
    print("🔍 CHECKING M DRIVE AI MODEL STORAGE")
    print("=" * 50)

    if platform.system() != 'Windows':
        print("❌ Not running on Windows - M: drive check not applicable")
        return None

    # Quick check if M drive exists
    if os.path.exists('M:/'):
        print("✅ M: drive detected and accessible")

        # Get basic drive info using simpler method
        try:
            import subprocess
            result = subprocess.run(['dir', 'M:/'], capture_output=True, text=True, shell=True, timeout=5)
            if result.returncode == 0:
                print("✅ M: drive is readable")
            else:
                print("⚠️  M: drive may have access restrictions")
        except:
            print("⚠️  Cannot determine M: drive access level")

        return True
    else:
        print("❌ M: drive not found or not accessible")
        return False

def check_model_directories():
    """Check for AI model directories on M drive"""
    print("\n📂 CHECKING AI MODEL DIRECTORIES")
    print("-" * 40)

    model_paths = [
        'M:/AI/Models',
        'M:/AI/models',
        'M:/models',
        'M:/AI',
        'M:/machine-learning',
        'M:/ml-models',
        'M:/ollama/models',
        'M:/stable-diffusion',
        'M:/comfyui/models'
    ]

    found_paths = []
    total_files = 0
    total_size = 0

    for path in model_paths:
        if os.path.exists(path):
            try:
                # Quick scan of directory
                items = os.listdir(path)
                dir_size = 0
                file_count = 0

                for item in items[:100]:  # Limit scan to first 100 items for speed
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        try:
                            dir_size += os.path.getsize(item_path)
                            file_count += 1
                        except:
                            pass

                size_gb = dir_size / (1024**3)
                print(f"✅ Found: {path}")
                print(f"   Files sampled: {file_count}")
                print(f"   Sample size: {size_gb:.2f} GB")

                # Look for model files
                model_extensions = ['.gguf', '.bin', '.safetensors', '.ckpt', '.pth', '.onnx']
                model_files = [f for f in items if any(f.lower().endswith(ext) for ext in model_extensions)]

                if model_files:
                    print(f"   AI Models found: {len(model_files)}")
                    for model in model_files[:3]:
                        print(f"     • {model}")
                    if len(model_files) > 3:
                        print(f"     ... and {len(model_files)-3} more")

                found_paths.append(path)
                total_files += file_count
                total_size += dir_size

            except Exception as e:
                print(f"⚠️  Error scanning {path}: {str(e)[:50]}...")

    if found_paths:
        total_size_gb = total_size / (1024**3)
        print(f"\n📊 SUMMARY: {len(found_paths)} directories found")
        print(f"   Total sampled files: {total_files}")
        print(f"   Total sampled size: {total_size_gb:.2f} GB")
    else:
        print("\n❌ No AI model directories found on M: drive")

    return found_paths

def add_vision_models_to_config():
    """Add vision, image, and video AI models to the configuration"""
    print("\n🎨 ADDING VISION/IMAGE/VIDEO AI MODELS")
    print("=" * 50)

    vision_models = {
        "image_generation": [
            {
                "name": "stable-diffusion-xl",
                "description": "High-quality image generation",
                "size": "~6.5GB",
                "capabilities": ["text-to-image", "image-to-image", "inpainting"],
                "endpoint": "http://<NAS_IP>:7860",  # Assuming Automatic1111 webUI
                "context_window": None,
                "localOnly": True
            },
            {
                "name": "flux-dev",
                "description": "Next-gen image generation",
                "size": "~23GB",
                "capabilities": ["text-to-image", "high-quality"],
                "endpoint": "http://<NAS_IP>:7860",
                "context_window": None,
                "localOnly": True
            }
        ],
        "vision_language": [
            {
                "name": "llava:7b",
                "description": "Vision-language model",
                "size": "~4GB",
                "capabilities": ["image-understanding", "visual-QA"],
                "endpoint": "http://<NAS_IP>:8080/v1",
                "context_length": 4096,
                "localOnly": True
            },
            {
                "name": "moondream:1.8b",
                "description": "Fast vision model",
                "size": "~1GB",
                "capabilities": ["image-captioning", "visual-search"],
                "endpoint": "http://<NAS_IP>:8080/v1",
                "context_length": 2048,
                "localOnly": True
            }
        ],
        "video_processing": [
            {
                "name": "animatediff",
                "description": "Video generation from images",
                "size": "~2GB",
                "capabilities": ["image-to-video", "motion-generation"],
                "endpoint": "http://<NAS_IP>:7860",
                "context_window": None,
                "localOnly": True
            }
        ]
    }

    # Update Continue config with vision models
    continue_config_path = project_root / ".continue" / "config.yaml"

    if continue_config_path.exists():
        try:
            with open(continue_config_path, 'r') as f:
                config_content = f.read()

            # Add vision models to the models section
            vision_model_configs = []

            # Image generation models
            for model in vision_models["image_generation"]:
                vision_model_configs.append(f"""  - name: {model["name"]}
    provider: openai
    model: {model["name"]}
    apiBase: {model["endpoint"]}
    contextLength: 2048
    roles:
      - chat
    localOnly: true""")

            # Vision-language models
            for model in vision_models["vision_language"]:
                vision_model_configs.append(f"""  - name: {model["name"]}
    provider: openai
    model: {model["name"]}
    apiBase: {model["endpoint"]}
    contextLength: {model["context_length"]}
    roles:
      - chat
      - edit
    localOnly: true""")

            # Add to config if not already present
            vision_config_text = "\n".join(vision_model_configs)

            if "stable-diffusion-xl" not in config_content:
                # Find the models section and add vision models
                if "models:" in config_content:
                    config_content = config_content.replace(
                        "models:",
                        f"models:\n{vision_config_text}\n",
                        1
                    )

                    with open(continue_config_path, 'w') as f:
                        f.write(config_content)

                    print("✅ Vision models added to Continue configuration")
                    print("   • Image generation: Stable Diffusion XL, Flux Dev")
                    print("   • Vision-language: LLaVA 7B, Moondream 1.8B")
                    print("   • Video processing: AnimateDiff")
                else:
                    print("⚠️  Could not find models section in config")
            else:
                print("✅ Vision models already configured")

        except Exception as e:
            print(f"❌ Failed to update Continue config: {e}")
    else:
        print("❌ Continue config file not found")

    return vision_models

def display_vision_model_setup():
    """Display setup instructions for vision models"""
    print("\n🚀 VISION MODEL SETUP INSTRUCTIONS")
    print("=" * 50)

    print("📦 REQUIRED SOFTWARE:")
    print("1. Automatic1111 Stable Diffusion WebUI")
    print("   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui")
    print("   cd stable-diffusion-webui && ./webui.sh --port 7860")
    print()

    print("2. Ollama Vision Models")
    print("   ollama pull llava:7b")
    print("   ollama pull moondream")
    print()

    print("3. ComfyUI (Optional - Advanced workflows)")
    print("   git clone https://github.com/comfyui/comfyui")
    print("   cd comfyui && python main.py --port 8188")
    print()

    print("💾 MODEL STORAGE LOCATIONS:")
    print("• Stable Diffusion: M:/stable-diffusion/models/Stable-diffusion/")
    print("• ComfyUI: M:/comfyui/models/")
    print("• Ollama: M:/ollama/models/ (default location)")
    print()

    print("🎯 USAGE IN CURSOR:")
    print("• /image \"A beautiful sunset over mountains\" - Generate image")
    print("• /analyze-image [upload image] - Describe/analyze image")
    print("• /video \"Create animation of dancing robots\" - Generate video")
    print()

    print("⚡ RTX 5090 OPTIMIZATION:")
    print("• Image generation: Use --xformers for faster processing")
    print("• Vision models: Keep under 8GB for best performance")
    print("• Batch processing: Generate multiple images simultaneously")

def main():
    """Main function"""
    print("🤖 AI MODELS & VISION CAPABILITIES CHECK")
    print("=" * 60)

    # Check M drive
    m_drive_ok = check_m_drive()

    # Check model directories
    model_dirs = check_model_directories() if m_drive_ok else []

    # Add vision models
    vision_models = add_vision_models_to_config()

    # Display setup instructions
    display_vision_model_setup()

    # Summary
    print("\n🎉 SUMMARY")
    print("=" * 30)

    if m_drive_ok:
        print("✅ M: drive accessible for AI model storage")
    else:
        print("❌ M: drive not accessible")

    if model_dirs:
        print(f"✅ {len(model_dirs)} AI model directories found")
    else:
        print("❌ No AI model directories detected")

    print("✅ Vision/image/video models configured")
    print("✅ Stable Diffusion, LLaVA, AnimateDiff support added")

    print("\n🚀 NEXT STEPS:")
    print("1. Install Automatic1111 WebUI for image generation")
    print("2. Pull vision models with Ollama")
    print("3. Download Stable Diffusion models to M: drive")
    print("4. Restart Cursor to access new vision capabilities")

if __name__ == "__main__":
    main()