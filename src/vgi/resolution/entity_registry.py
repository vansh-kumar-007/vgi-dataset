"""
Simple deterministic ID-minting registry for entities that Steam doesn't
assign IDs to itself (developers, publishers). Ensures the same normalized
name always maps to the same internal ID across the entire ingestion run.
"""

import hashlib


class EntityRegistry:
    """
    Maps normalized entity names to stable, deterministic IDs.
    Same name -> same ID, every time, even across separate script runs
    (since IDs are derived from the name itself, not an incrementing counter).
    """

    def __init__(self, prefix: str):
        self.prefix = prefix  # e.g. "dev" or "pub", keeps IDs readable/traceable
        self._name_to_id: dict[str, str] = {}

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().casefold()

    def get_or_create_id(self, raw_name: str) -> str:
        normalized = self._normalize(raw_name)
        if normalized not in self._name_to_id:
            # Deterministic hash-based ID: same normalized name always
            # produces the same ID, even in a future separate run.
            digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
            self._name_to_id[normalized] = f"{self.prefix}_{digest}"
        return self._name_to_id[normalized]

    def all_entries(self) -> list[dict]:
        """Returns [{id, name}] for every registered entity, for table export."""
        # Note: stores the FIRST raw_name seen per normalized key as the
        # canonical display name.
        seen_ids = set()
        entries = []
        for normalized, entity_id in self._name_to_id.items():
            if entity_id not in seen_ids:
                entries.append({"id": entity_id, "name": normalized})
                seen_ids.add(entity_id)
        return entries