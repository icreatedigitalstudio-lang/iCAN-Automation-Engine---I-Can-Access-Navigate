"""
iCREATE Automation Engine - Auto-Train Loop Example
Nightly self-updating: check DB -> export JSON -> push GitHub -> redeploy k8s

pip install apscheduler
"""

import asyncio
import os
from src.pyautoforge.self_healing.auto_train import AutoTrainer, AutoTrainConfig

# Config from env
config = AutoTrainConfig(
    db_path="healed_selectors.db",
    export_json_path="src/pyautoforge/self_healing/healed_selectors_export.json",
    github_repo=os.getenv("GITHUB_REPO", "icreate-studio/automation-engine"),
    github_token=os.getenv("GITHUB_TOKEN", ""),
    github_branch="main",
    k8s_deployment="icreate-automation-engine",
    k8s_namespace="default",
    auto_push=False,  # Set True to actually push
    auto_redeploy=False,  # Set True to actually redeploy
    min_new_heals_to_trigger=1
)

trainer = AutoTrainer(config)

async def test_nightly_job():
    print("🌙 Testing nightly job...")
    result = await trainer.nightly_job()
    print(f"Result: {result}")

def test_schedule():
    print("⏰ Scheduling nightly job at 2 AM...")
    scheduler = trainer.schedule_nightly()
    if scheduler:
        print("Scheduler started. Will run at 2 AM daily.")
        print("For testing, you can also run manually: asyncio.run(trainer.nightly_job())")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.shutdown()
            print("Scheduler stopped")

if __name__ == "__main__":
    asyncio.run(test_nightly_job())
    # test_schedule()  # Uncomment to test scheduler loop
