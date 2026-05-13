"""
Unit tests for utils/landing_cards.py — data-driven card derivation for
Banking and Cross-Industry landing pages.

Behavioral contract:
- Cards are derived from real data — no hardcoded list. The card universe
  is exactly the Solution/Offering values that have >=1 story matching the
  industry filter (after Era exclusion).
- Era exclusion: stories with Era == "Leadership & Professional Narrative"
  are excluded from card counts (mirrors timeline_view.py EXCLUDED_ERA).
- Cards are tiered: Core (>=3 stories) vs Specialized (<3 stories).
- Each card carries title (Solution/Offering value), count, client count,
  subtitle (from CAPABILITY_SUBTITLES, empty string if not curated), tier.
- Ordering: descending by story count within each tier.

This contract prevents the May 12, 2026 Card 3 regression class of bug:
no hardcoded card can reference a Solution/Offering value that doesn't
exist in the data, because cards ARE the data.
"""

# Build sample stories that exercise the contract:
# - 4 banking stories with "Global Payments" (Core tier — 3+)
# - 3 banking stories with "Modern Engineering" (Core tier — 3+)
# - 2 banking stories with "Digital Product" (Specialized — <3)
# - 1 banking story with "Security & Compliance" (Specialized — <3)
# - 1 banking story with Era=EXCLUDED — must NOT count
# - 2 non-banking stories (must be excluded by industry filter)
SAMPLE_STORIES = [
    # Banking + Global Payments (4)
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Global Payments & Treasury Solutions",
        "Era": "Financial Services Platform Modernization",
        "Client": "JPMC",
    },
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Global Payments & Treasury Solutions",
        "Era": "Financial Services Platform Modernization",
        "Client": "JPMC",
    },
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Global Payments & Treasury Solutions",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "Fiserv",
    },
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Global Payments & Treasury Solutions",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "HSBC",
    },
    # Banking + Modern Engineering (3)
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Modern Engineering Practices & Solutions",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "RBC",
    },
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Modern Engineering Practices & Solutions",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "RBC",
    },
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Modern Engineering Practices & Solutions",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "AmEx",
    },
    # Banking + Digital Product (2 — Specialized)
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Digital Product Development",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "JPMC",
    },
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Digital Product Development",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "JPMC",
    },
    # Banking + Security (1 — Specialized)
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Security & Compliance Solutions",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "Capital One",
    },
    # Banking + EXCLUDED ERA (must NOT appear in cards)
    {
        "Industry": "Financial Services / Banking",
        "Solution / Offering": "Leadership Philosophy",
        "Era": "Leadership & Professional Narrative",
        "Client": "Various",
    },
    # Non-banking (must be excluded by industry filter)
    {
        "Industry": "Cross Industry",
        "Solution / Offering": "Modern Engineering Practices & Solutions",
        "Era": "Enterprise Innovation & Transformation",
        "Client": "Various",
    },
    {
        "Industry": "Healthcare / Life Sciences",
        "Solution / Offering": "Digital Product Development",
        "Era": "Independent Product Development",
        "Client": "Pfizer",
    },
]


class TestBuildLandingCards:
    """Contract tests for build_landing_cards()."""

    def test_filters_to_named_industry_only(self):
        """Non-banking stories must not contribute to banking cards."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        # "Healthcare" story would have made Digital Product Development have 3 stories
        # if filtering weren't industry-scoped. Confirm count comes from banking only.
        digital = next(
            (c for c in cards if c["title"] == "Digital Product Development"), None
        )
        assert digital is not None
        assert digital["count"] == 2, (
            f"Digital Product Development should have 2 banking stories, got {digital['count']}. "
            f"Likely the non-banking Healthcare story leaked through industry filtering."
        )

    def test_excludes_narrative_era(self):
        """Stories with Era == 'Leadership & Professional Narrative' must not count."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        titles = [c["title"] for c in cards]
        assert (
            "Leadership Philosophy" not in titles
        ), "EXCLUDED_ERA stories should be filtered out — same rule timeline applies."

    def test_core_tier_threshold_is_3_or_more(self):
        """Cards with >=3 banking stories land in Core tier."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        core = [c for c in cards if c["tier"] == "core"]
        core_titles = [c["title"] for c in core]
        assert "Global Payments & Treasury Solutions" in core_titles  # 4 stories
        assert "Modern Engineering Practices & Solutions" in core_titles  # 3 stories
        assert "Digital Product Development" not in core_titles  # 2 stories
        assert "Security & Compliance Solutions" not in core_titles  # 1 story

    def test_specialized_tier_under_3_stories(self):
        """Cards with <3 banking stories land in Specialized tier."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        specialized = [c for c in cards if c["tier"] == "specialized"]
        spec_titles = [c["title"] for c in specialized]
        assert "Digital Product Development" in spec_titles  # 2 stories
        assert "Security & Compliance Solutions" in spec_titles  # 1 story

    def test_each_card_has_required_fields(self):
        """Cards have title, count, clients, subtitle, tier."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        for c in cards:
            assert "title" in c
            assert "count" in c and isinstance(c["count"], int) and c["count"] >= 1
            assert (
                "clients" in c and isinstance(c["clients"], int) and c["clients"] >= 1
            )
            assert "subtitle" in c and isinstance(c["subtitle"], str)
            assert c["tier"] in ("core", "specialized")

    def test_subtitle_pulled_from_capability_subtitles(self):
        """Subtitle for a known capability should match CAPABILITY_SUBTITLES."""
        from config.constants import CAPABILITY_SUBTITLES
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        gp = next(
            c for c in cards if c["title"] == "Global Payments & Treasury Solutions"
        )
        assert (
            gp["subtitle"]
            == CAPABILITY_SUBTITLES["Global Payments & Treasury Solutions"]
        )

    def test_subtitle_empty_string_for_uncurated_capability(self):
        """When a Solution/Offering has no CAPABILITY_SUBTITLES entry, subtitle is ''."""
        # "Leadership Philosophy" is filtered by Era, so use a different probe.
        # Construct a story whose Solution/Offering isn't in CAPABILITY_SUBTITLES.
        stories = [
            {
                "Industry": "Financial Services / Banking",
                "Solution / Offering": "Fake Uncurated Capability",
                "Era": "Enterprise Innovation & Transformation",
                "Client": "X",
            },
        ]
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(stories, industry="Financial Services / Banking")
        assert len(cards) == 1
        assert cards[0]["subtitle"] == "", (
            "Uncurated capabilities should fall through to empty-string subtitle, "
            "same fallback behavior as ERA_SUBTITLES.get(era, '') in timeline_view.py."
        )

    def test_cards_sorted_by_count_descending(self):
        """Within each tier, cards are ordered by story count descending."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        core_counts = [c["count"] for c in cards if c["tier"] == "core"]
        spec_counts = [c["count"] for c in cards if c["tier"] == "specialized"]
        assert core_counts == sorted(core_counts, reverse=True)
        assert spec_counts == sorted(spec_counts, reverse=True)

    def test_client_count_reflects_unique_clients_only(self):
        """Client count counts UNIQUE clients per capability, not story repeats."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        # Global Payments: JPMC(2), Fiserv(1), HSBC(1) = 3 unique clients across 4 stories
        gp = next(
            c for c in cards if c["title"] == "Global Payments & Treasury Solutions"
        )
        assert gp["clients"] == 3, f"Expected 3 unique clients, got {gp['clients']}"
        # Modern Engineering: RBC(2), AmEx(1) = 2 unique clients across 3 stories
        me = next(
            c for c in cards if c["title"] == "Modern Engineering Practices & Solutions"
        )
        assert me["clients"] == 2

    def test_no_broken_zero_count_cards(self):
        """No card with count=0 may exist. Cards ARE the data; broken cards can't exist."""
        from utils.landing_cards import build_landing_cards

        cards = build_landing_cards(
            SAMPLE_STORIES, industry="Financial Services / Banking"
        )
        assert all(c["count"] >= 1 for c in cards), (
            "Cards must derive from real stories. The May 12, 2026 Card 3 bug "
            "shipped because a hardcoded card referenced a Solution/Offering value "
            "with 0 stories — this contract makes that impossible by construction."
        )
