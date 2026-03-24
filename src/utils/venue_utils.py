from __future__ import annotations

import re
from dataclasses import dataclass


def normalize_venue_text(text: str) -> str:
    lowered = (text or "").strip().lower()
    # Keep only alphanumeric chars to ignore punctuation and spacing differences.
    return re.sub(r"[^a-z0-9]+", "", lowered)


def normalize_venue_phrase(text: str) -> str:
    lowered = (text or "").strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


@dataclass(frozen=True)
class VenueEntry:
    canonical_name: str
    aliases: list[str]
    tier: str
    venue_type: str


class VenueMatcher:
    def __init__(self, venue_config: dict) -> None:
        self.alias_map: dict[str, VenueEntry] = {}
        self.phrase_aliases: list[tuple[str, VenueEntry]] = []
        self.short_aliases: list[tuple[str, VenueEntry]] = []
        self.entries: list[VenueEntry] = []
        self._load(venue_config)

    def _load(self, venue_config: dict) -> None:
        all_entries = (venue_config.get("conferences", []) or []) + (
            venue_config.get("journals", []) or []
        )
        for item in all_entries:
            entry = VenueEntry(
                canonical_name=item["canonical_name"],
                aliases=item.get("aliases", []) or [],
                tier=item["tier"],
                venue_type=item["type"],
            )
            self.entries.append(entry)

            # Canonical name is also a valid alias.
            for name in [entry.canonical_name, *entry.aliases]:
                key = normalize_venue_text(name)
                if key:
                    self.alias_map[key] = entry
                phrase = normalize_venue_phrase(name)
                if phrase:
                    self.phrase_aliases.append((phrase, entry))
                    # Short aliases like CVPR/TRO should use token-level matching.
                    if len(phrase) <= 8 and " " not in phrase:
                        self.short_aliases.append((phrase, entry))

    def match(self, raw_venue_name: str) -> VenueEntry | None:
        key = normalize_venue_text(raw_venue_name)
        if not key:
            return None
        exact = self.alias_map.get(key)
        if exact is not None:
            return exact

        phrase = normalize_venue_phrase(raw_venue_name)
        if not phrase:
            return None

        # First try short abbreviation matching with word boundaries.
        for short_alias, entry in self.short_aliases:
            if re.search(rf"\b{re.escape(short_alias)}\b", phrase):
                return entry

        # Then try normalized phrase containment for long names.
        for alias_phrase, entry in self.phrase_aliases:
            if len(alias_phrase) <= 8 and " " not in alias_phrase:
                continue
            if alias_phrase in phrase:
                return entry
        return None

    def all_search_names(self) -> list[str]:
        names: list[str] = []
        for entry in self.entries:
            names.append(entry.canonical_name)
            names.extend(entry.aliases)
        # Preserve order while removing duplicates.
        seen: set[str] = set()
        deduped: list[str] = []
        for name in names:
            key = normalize_venue_text(name)
            if key and key not in seen:
                seen.add(key)
                deduped.append(name)
        return deduped

    def canonical_search_names(self) -> list[str]:
        return [entry.canonical_name for entry in self.entries]

    def canonical_queries_with_tier(self) -> list[tuple[str, str]]:
        return [(entry.canonical_name, entry.tier) for entry in self.entries]
