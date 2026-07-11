"""
Test only the Apify connector.
Prints detailed diagnostic information.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.jobs.connectors.apify import ApifyConnector
from src.utils import load_env

load_env()

def test_apify():
    print("=" * 60)
    print("APIFY CONNECTOR TEST")
    print("=" * 60)
    
    try:
        # Initialize connector
        connector = ApifyConnector()
        
        # Check API key
        api_key_loaded = "Yes" if connector.api_key else "No"
        print(f"API key loaded: {api_key_loaded}")
        
        if not connector.api_key:
            print("ERROR: APIFY_API_KEY not set")
            return
        
        # Get actor ID
        actor_id = connector.actors.get("linkedin")
        print(f"Actor ID: {actor_id}")
        
        # Check if actor exists
        try:
            from apify_client import ApifyClient
            client = ApifyClient(connector.api_key)
            
            # Try to get actor info
            try:
                actor_info = client.actor(actor_id).get()
                actor_exists = "Yes"
                print(f"Actor exists: {actor_exists}")
            except Exception as e:
                actor_exists = "No"
                print(f"Actor exists: {actor_exists}")
                print(f"Actor check error: {type(e).__name__}: {e}")
                return
            
            # Try to run actor
            try:
                run_input = {
                    "searchQuery": "python developer",
                    "maxJobs": 5,
                }
                
                print(f"Actor run started: Attempting...")
                run = client.actor(actor_id).call(run_input=run_input)
                print(f"Actor run started: Yes")
                
                # Get dataset ID
                dataset_id = run.get("defaultDatasetId")
                print(f"Dataset ID: {dataset_id}")
                
                if dataset_id:
                    # Fetch dataset items
                    dataset_items = client.dataset(dataset_id).list_items(limit=5)
                    items = dataset_items.items
                    
                    print(f"Number of jobs returned: {len(items)}")
                    
                    if items:
                        print(f"First returned job (JSON):")
                        print(json.dumps(items[0], indent=2, default=str))
                    else:
                        print("No jobs returned")
                else:
                    print("No dataset ID returned")
                    print(f"Full run response: {json.dumps(run, indent=2, default=str)}")
                
            except Exception as e:
                print(f"Actor run started: No")
                print(f"Run error: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                
        except ImportError:
            print("ERROR: apify_client not installed")
            print("Run: pip install apify_client")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_apify()
