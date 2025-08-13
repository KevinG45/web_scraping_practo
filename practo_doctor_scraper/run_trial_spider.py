#!/usr/bin/env python
"""
Simple script to run the Practo doctor spider for testing
"""
import os
import sys
import subprocess
from pathlib import Path

def run_spider():
    """Run the doctor spider with proper environment setup"""
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🚀 Starting Practo Doctor Spider (5 doctors test)")
    print("=" * 50)
    
    # Clean previous output files
    for file in ['doctors_data.json', 'doctors_data.csv']:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Cleaned old {file}")
    
    # Run the spider
    cmd = [
        sys.executable, "-m", "scrapy", "crawl", "doctor_spider",
        "-s", "LOG_LEVEL=INFO",
        "-s", "CLOSESPIDER_ITEMCOUNT=5"
    ]
    
    try:
        print(f"🔍 Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        print("\n📊 SPIDER OUTPUT:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  WARNINGS/ERRORS:")
            print("-" * 30)
            print(result.stderr)
        
        print(f"\n✅ Spider completed with exit code: {result.returncode}")
        
        # Check output files
        if os.path.exists('doctors_data.json'):
            with open('doctors_data.json', 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                print(f"\n📁 Generated doctors_data.json with {len(data)} records")
                if data:
                    print("📋 Sample record:")
                    print(f"   Name: {data[0].get('name', 'N/A')}")
                    print(f"   Specialization: {data[0].get('specialization', 'N/A')}")
                    print(f"   Rating: {data[0].get('rating', 'N/A')}")
        
        if os.path.exists('doctors_data.csv'):
            print(f"📁 Generated doctors_data.csv")
            
    except subprocess.TimeoutExpired:
        print("⏰ Spider timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error running spider: {e}")

if __name__ == "__main__":
    run_spider()
