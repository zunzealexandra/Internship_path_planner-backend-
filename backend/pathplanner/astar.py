from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from heapq import heappop, heappush
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .models import Internship
from .utils import normalize_skills


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_goal_title(job_title: str, target_role: str) -> bool:
    normalized_title = job_title.lower()
    normalized_target = target_role.lower()
    return normalized_target in normalized_title or title_similarity(normalized_title, normalized_target) >= 0.72


@dataclass(order=True)
class SearchState:
    priority: float
    cost: float
    node_id: Optional[int] = field(compare=False)
    acquired_skills: Set[str] = field(compare=False, default_factory=set)
    path: List[int] = field(compare=False, default_factory=list)
    path_detail: List[Dict] = field(compare=False, default_factory=list)


class PathPlanner:
    """
    Lightweight A* pathfinder tuned for internship transitions.
    """

    def __init__(self, internships: Iterable[Internship]):
        self.nodes = []
        for internship in internships:
            needed = set(normalize_skills(internship.skills_needed))
            learned = set(normalize_skills(internship.skills_learned))
            self.nodes.append(
                {
                    "id": internship.id,
                    "model": internship,
                    "job_title": internship.job_title,
                    "location": internship.location,
                    "skills_needed": needed,
                    "skills_learned": learned,
                    "title_lower": internship.job_title.lower(),
                }
            )
        self.node_lookup: Dict[int, Dict] = {node["id"]: node for node in self.nodes}

    def _heuristic(self, acquired: Set[str], node: Dict, target_role: str) -> float:
        missing = len(node["skills_needed"] - acquired)
        title_score = title_similarity(node["job_title"], target_role)
        return missing * 0.4 + (1 - title_score) * 3

    def plan(
        self,
        start_skills: Iterable[str],
        target_role: str,
    ) -> Dict:
        if not self.nodes:
            return {
                "message": "No internships are available to explore.",
                "path": [],
                "reached_goal": False,
                "expanded_nodes": 0,
                "total_cost": 0.0,
                "target_role": target_role,
            }

        start_skills_set = set(normalize_skills(start_skills))
        open_heap: List[SearchState] = []
        start_state = SearchState(
            priority=0.0,
            cost=0.0,
            node_id=None,
            acquired_skills=start_skills_set,
            path=[],
            path_detail=[],
        )
        heappush(open_heap, start_state)

        visited: Set[Tuple[Optional[int], frozenset[str]]] = set()
        best_state: Optional[SearchState] = None
        best_title_score = 0.0
        expanded = 0

        while open_heap:
            current = heappop(open_heap)
            state_key = (current.node_id, frozenset(current.acquired_skills))
            if state_key in visited:
                continue
            visited.add(state_key)
            expanded += 1

            if current.node_id is not None:
                current_node = self.node_lookup[current.node_id]
                score = title_similarity(current_node["job_title"], target_role)
                if score > best_title_score:
                    best_title_score = score
                    best_state = current
                if is_goal_title(current_node["job_title"], target_role):
                    return self._build_result(
                        current,
                        expanded,
                        target_role,
                        reached_goal=True,
                    )

            for node in self.nodes:
                if node["id"] in current.path:
                    continue  # avoid cycles

                missing_skills = node["skills_needed"] - current.acquired_skills
                step_cost = 1 + len(missing_skills) * 0.5
                new_acquired = current.acquired_skills | node["skills_learned"] | node["skills_needed"]
                g_cost = current.cost + step_cost
                h_cost = self._heuristic(new_acquired, node, target_role)
                f_cost = g_cost + h_cost

                detail = {
                    "internship_id": node["id"],
                    "company": node["model"].company,
                    "job_title": node["job_title"],
                    "location": node["location"],
                    "job_type": node["model"].job_type,
                    "experience": node["model"].experience,
                    "step_cost": round(step_cost, 3),
                    "cumulative_cost": round(g_cost, 3),
                    "missing_skills": sorted(missing_skills),
                    "skills_gained": sorted(node["skills_learned"]),
                    "acquired_skills_after": sorted(new_acquired),
                }

                new_state = SearchState(
                    priority=f_cost,
                    cost=g_cost,
                    node_id=node["id"],
                    acquired_skills=new_acquired,
                    path=current.path + [node["id"]],
                    path_detail=current.path_detail + [detail],
                )
                heappush(open_heap, new_state)

        if best_state:
            return self._build_result(
                best_state,
                expanded,
                target_role,
                reached_goal=False,
            )

        return {
            "message": "Unable to build a path with the provided inputs.",
            "path": [],
            "reached_goal": False,
            "expanded_nodes": expanded,
            "total_cost": 0.0,
            "target_role": target_role,
        }

    def _build_result(
        self,
        state: SearchState,
        expanded: int,
        target_role: str,
        reached_goal: bool,
    ) -> Dict:
        return {
            "path": state.path_detail,
            "reached_goal": reached_goal,
            "target_role": target_role,
            "expanded_nodes": expanded,
            "total_cost": round(state.cost, 3),
        }







