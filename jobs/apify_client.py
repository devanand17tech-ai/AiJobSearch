import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class ApifyJobClient:
    """
    Communicates with the Apify API using the official apify-client Python package.
    Executes configured job scraper actors (e.g. apify/google-jobs-scraper) to fetch live job listings.
    """

    def __init__(self, api_token: Optional[str] = None, actor_id: Optional[str] = None):
        self.api_token = (api_token or os.getenv("APIFY_API_TOKEN", "")).strip()
        self.actor_id = (actor_id or os.getenv("APIFY_ACTOR_ID", "misceres/indeed-scraper")).strip()
        self.last_error = ""
        
        self.client = None
        if self.api_token:
            try:
                from apify_client import ApifyClient
                self.client = ApifyClient(token=self.api_token)
            except ImportError:
                print("[ApifyJobClient Warning] apify-client package not installed.")
            except Exception as e:
                print(f"[ApifyJobClient Error] Failed to initialize ApifyClient: {e}")

    def is_configured(self) -> bool:
        """Returns True if Apify token is provided and client initialized."""
        return bool(self.api_token and self.client is not None)

    def search_jobs(self, query: str, location: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Executes an Apify Actor to fetch live jobs matching the search query and location.
        """
        if not self.is_configured():
            print("[ApifyJobClient] Live job search is not configured (missing APIFY_API_TOKEN).")
            return []

        try:
            print(f"[ApifyJobClient] Launching Actor '{self.actor_id}' for query: '{query}', location: '{location}'")
            
            if self.actor_id == "bebity/linkedin-jobs-scraper":
                run_input = {
                    "titles": [query],
                    "locations": [location] if location else [],
                    "rows": max_results,
                }
            elif self.actor_id == "misceres/indeed-scraper":
                run_input = {
                    "position": query,
                    "location": location,
                    "country": os.getenv("APIFY_COUNTRY", "US").strip(),
                    "maxItemsPerSearch": max_results,
                    "saveOnlyUniqueItems": True,
                }
            else:
                # Generic input used by actors that accept query strings.
                run_input = {
                    "queries": f"{query} in {location}".strip() if location else query,
                    "maxItems": max_results,
                    "maxPages": 1,
                }

            # Run the actor synchronously and wait for completion
            run = self.client.actor(self.actor_id).call(run_input=run_input)

            # Fetch dataset items
            dataset_items = []
            dataset_id = getattr(run, "default_dataset_id", None)
            if dataset_id is None and isinstance(run, dict):
                dataset_id = run.get("defaultDatasetId") or run.get("default_dataset_id")

            if dataset_id:
                dataset_client = self.client.dataset(dataset_id)
                dataset_items = list(dataset_client.iterate_items())
                print(f"[ApifyJobClient] Successfully fetched {len(dataset_items)} items from Apify Dataset.")

            return dataset_items

        except Exception as e:
            self.last_error = str(e)
            print(f"[ApifyJobClient Error] Apify actor run failed: {self.last_error}")
            return []
