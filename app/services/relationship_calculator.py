"""Relationship path-finding and human-readable labeling.

Uses BFS over ParentChild + Partnership edges to find the shortest path
between two persons, then labels the relationship in plain English.
"""

from collections import deque

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person, PersonLifecycleState
from app.models.relationships import ParentChild, Partnership


class RelationshipResult:
    def __init__(
        self,
        *,
        found: bool,
        relationship_label: str,
        path: list[str],
        path_details: list[dict],
    ):
        self.found = found
        self.relationship_label = relationship_label
        self.path = path
        self.path_details = path_details


async def find_relationship(
    db: AsyncSession,
    from_id: str,
    to_id: str,
) -> RelationshipResult:
    """Find and label the shortest relationship path between two persons."""
    if from_id == to_id:
        return RelationshipResult(
            found=True,
            relationship_label="same person",
            path=[from_id],
            path_details=[],
        )

    # Load graph
    adj, edge_meta, names = await _load_graph(db)

    if from_id not in adj or to_id not in adj:
        return RelationshipResult(
            found=False,
            relationship_label="no path found",
            path=[],
            path_details=[],
        )

    # BFS
    visited = {from_id}
    queue: deque[tuple[str, list[str]]] = deque([(from_id, [from_id])])

    while queue:
        current, path = queue.popleft()
        for neighbor in adj.get(current, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            new_path = path + [neighbor]
            if neighbor == to_id:
                details = _build_path_details(new_path, edge_meta, names)
                label = _label_relationship(new_path, edge_meta, names)
                return RelationshipResult(
                    found=True,
                    relationship_label=label,
                    path=new_path,
                    path_details=details,
                )
            queue.append((neighbor, new_path))

    return RelationshipResult(
        found=False,
        relationship_label="no path found",
        path=[],
        path_details=[],
    )


async def _load_graph(
    db: AsyncSession,
) -> tuple[dict[str, list[str]], dict[tuple[str, str], dict], dict[str, str]]:
    """Build adjacency list and edge metadata from DB."""
    adj: dict[str, list[str]] = {}
    edge_meta: dict[tuple[str, str], dict] = {}

    # Load persons for names
    result = await db.execute(
        select(Person).where(Person.lifecycle_state == PersonLifecycleState.active.value)
    )
    persons = result.scalars().all()
    names: dict[str, str] = {p.id: p.display_name for p in persons}
    for pid in names:
        adj.setdefault(pid, [])

    # Load parent-child edges
    result = await db.execute(select(ParentChild))
    for pc in result.scalars().all():
        if pc.parent_id not in names or pc.child_id not in names:
            continue
        adj.setdefault(pc.parent_id, []).append(pc.child_id)
        adj.setdefault(pc.child_id, []).append(pc.parent_id)
        meta = {"type": "parent_child", "kind": pc.kind, "parent_id": pc.parent_id, "child_id": pc.child_id}
        edge_meta[(pc.parent_id, pc.child_id)] = meta
        edge_meta[(pc.child_id, pc.parent_id)] = meta

    # Load partnership edges
    result = await db.execute(select(Partnership))
    for p in result.scalars().all():
        if p.person_a_id not in names or p.person_b_id not in names:
            continue
        adj.setdefault(p.person_a_id, []).append(p.person_b_id)
        adj.setdefault(p.person_b_id, []).append(p.person_a_id)
        meta = {"type": "partnership", "kind": p.kind, "person_a_id": p.person_a_id, "person_b_id": p.person_b_id}
        edge_meta[(p.person_a_id, p.person_b_id)] = meta
        edge_meta[(p.person_b_id, p.person_a_id)] = meta

    return adj, edge_meta, names


def _build_path_details(
    path: list[str],
    edge_meta: dict[tuple[str, str], dict],
    names: dict[str, str],
) -> list[dict]:
    """Build edge details for each step in the path."""
    details = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        meta = edge_meta.get((a, b), {})
        details.append({
            "from_id": a,
            "from_name": names.get(a, "?"),
            "to_id": b,
            "to_name": names.get(b, "?"),
            "edge_type": meta.get("type", "unknown"),
            "edge_kind": meta.get("kind", "unknown"),
        })
    return details


def _label_relationship(
    path: list[str],
    edge_meta: dict[tuple[str, str], dict],
    names: dict[str, str],
) -> str:
    """Produce a human-readable relationship label from the BFS path."""
    if len(path) < 2:
        return "same person"

    # Classify each step as up (to parent), down (to child), or across (partnership)
    steps: list[str] = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        meta = edge_meta.get((a, b), {})
        if meta.get("type") == "partnership":
            steps.append("partner")
        elif meta.get("type") == "parent_child":
            if meta.get("parent_id") == b:
                steps.append("up")  # going to parent
            else:
                steps.append("down")  # going to child
        else:
            steps.append("unknown")

    # Get the kind qualifier for the first relevant edge
    first_meta = edge_meta.get((path[0], path[1]), {})
    kind = first_meta.get("kind", "biological")
    kind_prefix = _kind_prefix(kind, first_meta.get("type"))

    # Direct relationships (2 people, 1 edge)
    if len(steps) == 1:
        if steps[0] == "up":
            return f"{kind_prefix}parent"
        if steps[0] == "down":
            return f"{kind_prefix}child"
        if steps[0] == "partner":
            return _partner_label(kind)

    # 2 edges
    if len(steps) == 2:
        s = tuple(steps)
        if s == ("up", "up"):
            return f"{kind_prefix}grandparent"
        if s == ("down", "down"):
            return f"{kind_prefix}grandchild"
        if s == ("up", "down"):
            return "sibling"
        if s == ("down", "up"):
            return "spouse's child" if steps[1] == "up" else "co-parent"
        if s == ("up", "partner"):
            return "parent's partner"
        if s == ("partner", "down"):
            return "partner's child"
        if s == ("partner", "up"):
            return "partner's parent (in-law)"
        if s == ("down", "partner"):
            return "child's partner (in-law)"

    # 3 edges
    if len(steps) == 3:
        s = tuple(steps)
        if s == ("up", "up", "up"):
            return "great-grandparent"
        if s == ("down", "down", "down"):
            return "great-grandchild"
        if s == ("up", "up", "down"):
            return "uncle/aunt"
        if s == ("up", "down", "down"):
            return "niece/nephew"
        if s == ("up", "down", "partner"):
            return "sibling-in-law"
        if s == ("partner", "up", "down"):
            return "sibling-in-law"
        if s == ("up", "partner", "down"):
            return "step-sibling"
        if s == ("up", "up", "partner"):
            return "grandparent's partner"
        if s == ("partner", "up", "up"):
            return "grandparent-in-law"
        if s == ("down", "down", "partner"):
            return "grandchild's partner"

    # Cousin calculation: count ups then downs
    ups = 0
    downs = 0
    phase = "up"
    has_partner = False
    for s in steps:
        if s == "partner":
            has_partner = True
            continue
        if phase == "up" and s == "up":
            ups += 1
        elif s == "down":
            phase = "down"
            downs += 1
        elif phase == "up" and s == "down":
            phase = "down"
            downs += 1

    if ups >= 2 and downs >= 2 and not has_partner:
        degree = min(ups, downs) - 1
        removed = abs(ups - downs)
        label = _cousin_label(degree, removed)
        return label

    # In-law via partner edge at end
    if has_partner and steps[-1] == "partner":
        # Re-label without the partner step
        inner_steps = [s for s in steps if s != "partner"]
        inner_label = _label_from_steps(inner_steps)
        if inner_label:
            return f"{inner_label}-in-law"

    # Fallback: generic path description
    return _generic_label(len(path) - 1)


def _label_from_steps(steps: list[str]) -> str | None:
    """Quick re-labeling for inner steps (without partner edges)."""
    if not steps:
        return None
    ups = sum(1 for s in steps if s == "up")
    downs = sum(1 for s in steps if s == "down")
    if ups == 1 and downs == 0:
        return "parent"
    if ups == 0 and downs == 1:
        return "child"
    if ups == 1 and downs == 1:
        return "sibling"
    if ups == 2 and downs == 0:
        return "grandparent"
    if ups == 0 and downs == 2:
        return "grandchild"
    if ups == 2 and downs == 1:
        return "uncle/aunt"
    if ups == 1 and downs == 2:
        return "niece/nephew"
    if ups >= 2 and downs >= 2:
        degree = min(ups, downs) - 1
        removed = abs(ups - downs)
        return _cousin_label(degree, removed)
    return None


def _cousin_label(degree: int, removed: int) -> str:
    """Generate cousin label: 'first cousin', 'second cousin once removed', etc."""
    ordinals = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}
    removal_words = {0: "", 1: "once removed", 2: "twice removed", 3: "three times removed"}

    degree_str = ordinals.get(degree, f"{degree}th")
    if removed == 0:
        return f"{degree_str} cousin"
    removed_str = removal_words.get(removed, f"{removed} times removed")
    return f"{degree_str} cousin {removed_str}"


def _kind_prefix(kind: str, edge_type: str | None) -> str:
    """Return a qualifier prefix for non-biological relationships."""
    if edge_type != "parent_child":
        return ""
    if kind in ("biological", "unknown"):
        return ""
    return f"{kind} "


def _partner_label(kind: str) -> str:
    labels = {
        "married": "spouse",
        "domestic_partner": "domestic partner",
        "co_parent": "co-parent",
        "engaged": "fiance/fiancee",
        "other": "partner",
    }
    return labels.get(kind, "partner")


def _generic_label(distance: int) -> str:
    """Fallback label for complex paths."""
    return f"related ({distance} steps)"
