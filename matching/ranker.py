from typing import List, Dict, Any

class RankerTool:
    """
    Ranks matched job recommendations based on calculated compatibility score and user filters.
    """

    def rank_jobs(
        self,
        jobs_with_matches: List[Dict[str, Any]],
        sort_by: str = "Best match",
        min_score: int = 0,
        filter_remote_only: bool = False,
        location_filter: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Filters and ranks job listings.
        
        Each item in jobs_with_matches is assumed to be:
        {
            **job_dict,
            "match": {
                "score": int,
                "matched_skills": list,
                "missing_skills": list,
                "reason": str, ...
            }
        }
        """
        filtered = []

        for item in jobs_with_matches:
            match_info = item.get("match", {})
            score = match_info.get("score", 0)

            # Minimum score filter
            if score < min_score:
                continue

            # Remote filter
            if filter_remote_only:
                job_loc = item.get("location", "").lower()
                job_type = item.get("job_type", "").lower()
                if "remote" not in job_loc and "remote" not in job_type:
                    continue

            # Location text filter
            if location_filter and location_filter.strip():
                loc_term = location_filter.strip().lower()
                if loc_term not in item.get("location", "").lower():
                    continue

            filtered.append(item)

        # Sorting logic
        if sort_by == "Best match":
            filtered.sort(key=lambda x: x.get("match", {}).get("score", 0), reverse=True)
        elif sort_by == "Newest":
            filtered.sort(key=lambda x: x.get("date_posted", ""), reverse=True)

        return filtered
