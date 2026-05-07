#!/usr/bin/env python3
"""
Krishi Saarthi Demo Runner
Automated demonstration script for showcasing platform capabilities
"""

import os
import sys
import time
import json
import asyncio
import argparse
from typing import Dict, List, Any
from datetime import datetime
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.krishi.database import init_database
from src.krishi.security import SecurityManager
from src.krishi.logging import app_logger


class DemoRunner:
    """Main demo automation runner"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_tokens = {}
        self.demo_data = self._load_demo_data()
        self.logger = app_logger
        
    def _load_demo_data(self) -> Dict[str, Any]:
        """Load demo data from JSON files"""
        data_dir = Path(__file__).parent.parent / "data"
        
        try:
            vendors = json.load(open(data_dir / "sample_vendors.json"))
            consumers = json.load(open(data_dir / "sample_consumers.json"))
            conversations = json.load(open(data_dir / "sample_conversations.json"))
            
            return {
                "vendors": vendors,
                "consumers": consumers,
                "conversations": conversations
            }
        except Exception as e:
            self.logger.error(f"Failed to load demo data: {e}")
            return {}
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
    
    def login_user(self, user: Dict[str, Any]) -> bool:
        """Login user and store session token"""
        login_data = {
            "phone": user["phone"],
            "password": user["password"]
        }
        
        response = self._make_request("POST", "/api/auth/login", login_data)
        
        if response and response.status_code == 200:
            token = response.json().get("session_token")
            if token:
                self.session_tokens[user["id"]] = token
                self.logger.info(f"Logged in user: {user['name']} (ID: {user['id']})")
                return True
        
        self.logger.error(f"Failed to login user: {user['name']}")
        return False
    
    def logout_user(self, user_id: int) -> bool:
        """Logout user"""
        if user_id not in self.session_tokens:
            return True
        
        logout_data = {"session_token": self.session_tokens[user_id]}
        response = self._make_request("POST", "/api/auth/logout", logout_data)
        
        if response and response.status_code == 200:
            del self.session_tokens[user_id]
            self.logger.info(f"Logged out user ID: {user_id}")
            return True
        
        return False
    
    def simulate_voice_interaction(self, user_id: int, voice_text: str, 
                              expected_response: str = None) -> bool:
        """Simulate voice interaction with the system"""
        if user_id not in self.session_tokens:
            self.logger.error(f"User {user_id} not logged in")
            return False
        
        voice_data = {
            "voice_text": voice_text,
            "language": "hi",
            "session_token": self.session_tokens[user_id],
            "state": {}
        }
        
        response = self._make_request("POST", "/api/voice", voice_data)
        
        if response and response.status_code == 200:
            result = response.json()
            actual_response = result.get("reply_text", "")
            
            self.logger.info(f"Voice Input: {voice_text}")
            self.logger.info(f"System Response: {actual_response}")
            
            if expected_response:
                # Simple check if expected keywords are in response
                expected_keywords = expected_response.split()[:3]  # Check first 3 words
                matches = sum(1 for word in expected_keywords if word.lower() in actual_response.lower())
                success_rate = matches / len(expected_keywords)
                
                if success_rate >= 0.5:  # At least 50% keyword match
                    self.logger.info(f"✓ Response matches expected (Success rate: {success_rate:.1%})")
                    return True
                else:
                    self.logger.warning(f"✗ Response doesn't match expected (Success rate: {success_rate:.1%})")
            
            return True
        
        self.logger.error(f"Voice interaction failed")
        return False
    
    def run_vendor_demo(self) -> bool:
        """Run vendor workflow demonstration"""
        self.logger.info("=== Starting Vendor Demo ===")
        
        vendor = self.demo_data["vendors"][0]  # Ramesh Kumar
        
        # Login vendor
        if not self.login_user(vendor):
            return False
        
        # Simulate product listing
        conversations = [c for c in self.demo_data["conversations"] 
                        if c["scenario"] == "vendor_product_listing"]
        
        if conversations:
            conv = conversations[0]
            for i, voice_input in enumerate(conv["voice_inputs"]):
                expected = conv["expected_responses"][i] if i < len(conv["expected_responses"]) else None
                self.simulate_voice_interaction(vendor["id"], voice_input, expected)
                time.sleep(2)  # Pause between interactions
        
        # Logout vendor
        self.logout_user(vendor["id"])
        return True
    
    def run_consumer_demo(self) -> bool:
        """Run consumer workflow demonstration"""
        self.logger.info("=== Starting Consumer Demo ===")
        
        consumer = self.demo_data["consumers"][0]  # Sita Devi
        
        # Login consumer
        if not self.login_user(consumer):
            return False
        
        # Simulate product search
        conversations = [c for c in self.demo_data["conversations"] 
                        if c["scenario"] == "consumer_product_search"]
        
        if conversations:
            conv = conversations[0]
            for i, voice_input in enumerate(conv["voice_inputs"]):
                expected = conv["expected_responses"][i] if i < len(conv["expected_responses"]) else None
                self.simulate_voice_interaction(consumer["id"], voice_input, expected)
                time.sleep(2)
        
        # Simulate order placement
        conversations = [c for c in self.demo_data["conversations"] 
                        if c["scenario"] == "consumer_order_placement"]
        
        if conversations:
            conv = conversations[0]
            for i, voice_input in enumerate(conv["voice_inputs"]):
                expected = conv["expected_responses"][i] if i < len(conv["expected_responses"]) else None
                self.simulate_voice_interaction(consumer["id"], voice_input, expected)
                time.sleep(2)
        
        # Logout consumer
        self.logout_user(consumer["id"])
        return True
    
    def run_udhar_demo(self) -> bool:
        """Run udhar (credit) system demonstration"""
        self.logger.info("=== Starting Udhar Demo ===")
        
        vendor = self.demo_data["vendors"][0]
        consumer = self.demo_data["consumers"][0]
        
        # Login vendor
        if not self.login_user(vendor):
            return False
        
        # Vendor creates udhar
        conversations = [c for c in self.demo_data["conversations"] 
                        if c["scenario"] == "vendor_udhar_creation"]
        
        if conversations:
            conv = conversations[0]
            for voice_input in conv["voice_inputs"]:
                self.simulate_voice_interaction(vendor["id"], voice_input)
                time.sleep(2)
        
        # Logout vendor
        self.logout_user(vendor["id"])
        
        # Login consumer
        if not self.login_user(consumer):
            return False
        
        # Consumer confirms udhar
        conversations = [c for c in self.demo_data["conversations"] 
                        if c["scenario"] == "consumer_udhar_confirmation"]
        
        if conversations:
            conv = conversations[0]
            for voice_input in conv["voice_inputs"]:
                self.simulate_voice_interaction(consumer["id"], voice_input)
                time.sleep(2)
        
        # Logout consumer
        self.logout_user(consumer["id"])
        return True
    
    def run_multi_user_demo(self) -> bool:
        """Run multi-user concurrent demonstration"""
        self.logger.info("=== Starting Multi-User Demo ===")
        
        # Login all users
        users = []
        
        # Login vendors
        for vendor in self.demo_data["vendors"][:2]:
            if self.login_user(vendor):
                users.append(vendor)
        
        # Login consumers
        for consumer in self.demo_data["consumers"][:2]:
            if self.login_user(consumer):
                users.append(consumer)
        
        # Simulate concurrent interactions
        async def user_interaction(user):
            """Simulate user interaction"""
            if user["role"] == "vendor":
                voice_text = f"मेरे पास {user['products'][0]['quantity']} {user['products'][0]['unit']} {user['products'][0]['product_name']} हैं"
            else:
                voice_text = "मुझे ताजा सब्जी चाहिए"
            
            return self.simulate_voice_interaction(user["id"], voice_text)
        
        # Run concurrent interactions
        async def run_concurrent():
            tasks = [user_interaction(user) for user in users]
            results = await asyncio.gather(*tasks)
            return results
        
        # Run async demo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(run_concurrent())
        loop.close()
        
        # Logout all users
        for user in users:
            self.logout_user(user["id"])
        
        success_count = sum(1 for r in results if r)
        self.logger.info(f"Multi-user demo: {success_count}/{len(users)} successful")
        return success_count == len(users)
    
    def check_system_health(self) -> bool:
        """Check if system is ready for demo"""
        self.logger.info("=== Checking System Health ===")
        
        # Check API health
        response = self._make_request("GET", "/api/health")
        if not response or response.status_code != 200:
            self.logger.error("API health check failed")
            return False
        
        health_data = response.json()
        self.logger.info(f"API Status: {health_data.get('status', 'unknown')}")
        
        # Check database connectivity
        try:
            init_database()
            self.logger.info("Database connectivity: OK")
        except Exception as e:
            self.logger.error(f"Database connectivity failed: {e}")
            return False
        
        # Check LLM service
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        try:
            response = requests.get(f"{ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info("LLM service: OK")
            else:
                self.logger.warning(f"LLM service returned status {response.status_code}")
        except Exception as e:
            self.logger.error(f"LLM service check failed: {e}")
            return False
        
        return True
    
    def run_full_demo(self) -> bool:
        """Run complete demonstration"""
        self.logger.info("=== Starting Full Krishi Saarthi Demo ===")
        start_time = time.time()
        
        try:
            # Health check
            if not self.check_system_health():
                self.logger.error("System health check failed. Cannot proceed with demo.")
                return False
            
            # Vendor demo
            if not self.run_vendor_demo():
                self.logger.error("Vendor demo failed")
                return False
            
            time.sleep(3)
            
            # Consumer demo
            if not self.run_consumer_demo():
                self.logger.error("Consumer demo failed")
                return False
            
            time.sleep(3)
            
            # Udhar demo
            if not self.run_udhar_demo():
                self.logger.error("Udhar demo failed")
                return False
            
            time.sleep(3)
            
            # Multi-user demo
            if not self.run_multi_user_demo():
                self.logger.error("Multi-user demo failed")
                return False
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info(f"=== Demo Completed Successfully ===")
            self.logger.info(f"Total duration: {duration:.1f} seconds")
            return True
            
        except Exception as e:
            self.logger.error(f"Demo failed with error: {e}")
            return False
    
    def interactive_demo(self):
        """Run interactive demo mode"""
        print("=== Krishi Saarthi Interactive Demo ===")
        print("Available scenarios:")
        print("1. Vendor Demo")
        print("2. Consumer Demo")
        print("3. Udhar Demo")
        print("4. Multi-User Demo")
        print("5. Full Demo")
        print("6. Health Check")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (0-6): ").strip()
                
                if choice == "0":
                    print("Exiting demo...")
                    break
                elif choice == "1":
                    self.run_vendor_demo()
                elif choice == "2":
                    self.run_consumer_demo()
                elif choice == "3":
                    self.run_udhar_demo()
                elif choice == "4":
                    self.run_multi_user_demo()
                elif choice == "5":
                    self.run_full_demo()
                elif choice == "6":
                    self.check_system_health()
                else:
                    print("Invalid choice. Please enter 0-6.")
                    
            except KeyboardInterrupt:
                print("\nExiting demo...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Krishi Saarthi Demo Runner")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL for the API")
    parser.add_argument("--scenario", choices=["vendor", "consumer", "udhar", "multi", "full", "health"],
                       help="Run specific demo scenario")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Initialize demo runner
    runner = DemoRunner(args.url)
    
    if args.interactive:
        runner.interactive_demo()
    elif args.scenario:
        if args.scenario == "vendor":
            runner.run_vendor_demo()
        elif args.scenario == "consumer":
            runner.run_consumer_demo()
        elif args.scenario == "udhar":
            runner.run_udhar_demo()
        elif args.scenario == "multi":
            runner.run_multi_user_demo()
        elif args.scenario == "full":
            runner.run_full_demo()
        elif args.scenario == "health":
            runner.check_system_health()
    else:
        # Default to full demo
        runner.run_full_demo()


if __name__ == "__main__":
    main()
