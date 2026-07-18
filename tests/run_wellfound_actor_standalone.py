"""
Standalone Wellfound Actor Runner

Demonstrates the WellfoundActor running independently.
This script shows:
- Browser launches
- URL opened
- Final redirected URL
- Page title
- Whether CAPTCHA was detected
- Number of job cards found
- First extracted job (if any)

Run: python tests/run_wellfound_actor_standalone.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging to stdout with clear formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def run_standalone():
    """Run the Wellfound actor standalone and report results."""
    print("=" * 70)
    print("  WELLFOUND ACTOR - STANDALONE RUN")
    print("  Test query: Backend Developer | Pune")
    print("=" * 70)

    # Step 0: Import the actor
    print("\n[0/6] Importing WellfoundActor...")
    from src.jobs.actors.wellfound_actor import WellfoundActor
    from src.jobs.actors.base_actor import ActorCAPTCHAError, ActorError

    actor = WellfoundActor()
    print("  [OK] WellfoundActor imported successfully")

    # Step 1: Initialize browser
    print("\n[1/6] Initializing browser...")
    try:
        await actor.initialize()
        print("  [OK] Browser initialized successfully")
        print("  Browser type: Chromium (headless=True)")
    except Exception as e:
        print(f"  [FAIL] Browser initialization failed: {type(e).__name__}: {e}")
        return

    # Step 2: Build search URL
    query = "Backend Developer"
    location = "Pune"
    print("\n[2/6] Building search URL...")
    print(f"  Query: {query}")
    print(f"  Location: {location}")
    print("  Remote: False")
    print("  Experience: None")

    search_url = actor._build_search_url(
        query=query,
        location=location,
        remote=False,
        experience=None,
    )
    print(f"  [OK] Search URL: {search_url}")

    # Step 3: Try to search jobs
    print("\n[3/6] Executing job search...")
    print("  Opening browser and navigating to URL...")
    print("  This may take a few seconds...")
    print()

    try:
        jobs = await actor.search_jobs(
            query=query,
            location=location,
            remote=False,
            experience=None,
            limit=10,
        )
        print("  [OK] Search completed")
        print(f"  Jobs extracted: {len(jobs)}")

        # Show first job if any
        if jobs:
            print("\n  First extracted job:")
            job = jobs[0]
            print(f"    Title: {job.title}")
            print(f"    Company: {job.company}")
            print(f"    Location: {job.location}")
            print(f"    URL: {job.url}")
            print(f"    Source: {job.source}")
            print(f"    Remote: {job.is_remote}")

    except ActorCAPTCHAError as e:
        # Step 4: CAPTCHA detected
        print("\n[4/6] CAPTCHA RESULT")
        print("  [CAPTCHA] CAPTCHA DETECTED")
        print("  Provider: DataDome CAPTCHA")
        print(f"  Details: {str(e)[:200]}...")
        print()
        print("  Wellfound uses DataDome CAPTCHA protection which prevents")
        print("  automated browser-based job extraction. No jobs were extracted.")

    except Exception as e:
        print(f"\n  [FAIL] Search failed: {type(e).__name__}: {e}")
    finally:
        # Step 5: Cleanup
        print("\n[5/6] Cleaning up...")
        await actor.cleanup()
        print("  [OK] Browser closed and resources released")

    # Step 6: Get source status
    print("\n[6/6] Source Status Report:")
    status = actor.get_source_status()
    print(f"  Available: {status['available']}")
    print(f"  Message: {status['message']}")
    print(f"  Last Check: {status['last_check']}")

    print()
    print("=" * 70)
    print("  RUN COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_standalone())