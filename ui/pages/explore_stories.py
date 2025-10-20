"""
Explore Stories Page

Browse 115 project case studies with advanced filtering.
Includes semantic search, faceted filters, and pagination.
"""

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import json
import re
from datetime import datetime

def render_explore_stories():
    """
    Render the Explore Stories page with filters and project listings.
    """
    # Add page header matching wireframe - use st.title to ensure it's visible
    st.title("Project Case Studies")
    st.markdown('<p>See how digital transformation happens in practice. Browse case studies, then click Ask MattGPT for the inside story.</p>', unsafe_allow_html=True)

    # --- Explore Stories CSS ---
    st.markdown("""
    <style>
        /* NUCLEAR OPTION: Target ALL Emotion cache classes with wildcard */
        /* This will override any st-emotion-cache-* classes */
        [class*="st-emotion-cache-"] {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Target stColumn with Emotion classes (the outermost wrapper causing the issue) */
        div.stColumn[class*="st-emotion-cache-"],
        div[data-testid="column"][class*="st-emotion-cache-"] {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Specifically target the stHorizontalBlock with any emotion class */
        div[data-testid="stHorizontalBlock"][class*="st-emotion-cache-"],
        div.stHorizontalBlock[class*="st-emotion-cache-"] {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Target the specific Emotion classes we've identified */
        /* Maximum specificity - chain all classes together */
        .st-emotion-cache-ygthqq,
        div.st-emotion-cache-ygthqq,
        div.stColumn.st-emotion-cache-ygthqq,
        div.stColumn.st-emotion-cache-ygthqq.e196pkbe1,
        div[data-testid="column"].st-emotion-cache-ygthqq.e196pkbe1 {
            background-color: transparent !important;
            background: transparent !important;
            background-image: none !important;
        }

        /* Target the specific Emotion class that creates dark background */
        /* Use multiple selectors with increasing specificity */
        .st-emotion-cache-1permvm,
        div.st-emotion-cache-1permvm,
        div.stHorizontalBlock.st-emotion-cache-1permvm,
        div[data-testid="stHorizontalBlock"].st-emotion-cache-1permvm {
            background-color: transparent !important;
            background: transparent !important;
            color: inherit !important;
        }

        /* Remove ALL container and form control backgrounds on this page */
        /* Use attribute selectors with high specificity to override Emotion CSS */
        div[data-testid="stVerticalBlock"][class],
        div[data-testid="stHorizontalBlock"][class],
        div[data-testid="column"][class],
        div[data-testid="element-container"][class],
        section[data-testid="stHorizontalBlock"][class],
        section[data-testid="stVerticalBlock"][class],
        div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"],
        div[data-testid="column"],
        div[data-testid="element-container"] {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Force transparency on ALL child divs inside columns */
        div[data-testid="column"] > div,
        div[data-testid="column"][class] > div[class] {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Target form control wrappers and all nested divs */
        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] > div > div,
        div[data-testid="stMultiSelect"],
        div[data-testid="stMultiSelect"] > div,
        div[data-testid="stMultiSelect"] > div > div,
        div[data-testid="stSelectbox"],
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stSelectbox"] > div > div {
            background-color: transparent !important;
            background: transparent !important;
        }

        /* Target BaseWeb and native elements */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        input:not([type="checkbox"]):not([type="radio"]),
        textarea {
            background-color: white !important;
            background: white !important;
        }

        .stMultiSelect, .stSelectbox, .stTextInput {
            margin-bottom: 0px !important;
        }

        /* Pagination buttons */
        .pagination-btn {
            padding: 8px 16px;
            margin: 0 4px;
            border-radius: 6px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            font-size: 14px;
        }

        .pagination-btn:hover {
            background: #f5f5f5;
        }

        .pagination-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
    """, unsafe_allow_html=True)

    # ===================================================================
    #  DATA LOADING
    # ===================================================================
    # For now, return a placeholder message
    # TODO: Implement actual data loading from case studies
    st.info("Explore Stories page is currently being refactored. Data loading will be implemented shortly.")
    return

    # Load the Case Studies data
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_file = os.path.join(project_root, "data", "all_case_studies.json")

    if not os.path.exists(data_file):
        st.error(f"Data file not found: {data_file}")
        st.info("The Explore Stories feature requires case studies data to be set up.")
        return

    with open(data_file, encoding="utf-8") as f:
        rows = json.load(f)

    # Each row in rows is a dict with keys: title, filename, url, client, domain, role, tags, personas, pub_date, metrics, summary
    # Convert to a format easier to display
    for r in rows:
        # Ensure lists
        if isinstance(r.get("tags"), str):
            r["tags"] = [t.strip() for t in r["tags"].split(",") if t.strip()]
        if isinstance(r.get("personas"), str):
            r["personas"] = [p.strip() for p in r["personas"].split(",") if p.strip()]
        if isinstance(r.get("domains"), str):
            r["domains"] = [d.strip() for d in r["domains"].split(",") if d.strip()]
        # Similarly for domain
        if "domain" in r and isinstance(r["domain"], str) and "," in r["domain"]:
            r["domains"] = [d.strip() for d in r["domain"].split(",")]
        elif "domain" in r and isinstance(r["domain"], str):
            r["domains"] = [r["domain"]]
        else:
            r["domains"] = r.get("domains", [])

        # Convert pub_date if needed
        if "pub_date" in r and isinstance(r["pub_date"], str):
            # Could parse, but let's just keep it simple for display
            pass

    # ===================================================================
    #  FACETS: Build filter options from the data
    # ===================================================================
    personas_set = set()
    clients_set = set()
    domains_set = set()
    roles_set = set()
    tags_set = set()

    for row in rows:
        for p in row.get("personas", []):
            personas_set.add(p)
        clients_set.add(row.get("client", ""))
        for d in row.get("domains", []):
            domains_set.add(d)
        roles_set.add(row.get("role", ""))
        for t in row.get("tags", []):
            tags_set.add(t)

    personas_all = sorted([p for p in personas_set if p])
    clients = sorted([c for c in clients_set if c])
    domains = sorted([d for d in domains_set if d])
    roles = sorted([r for r in roles_set if r])
    tags = sorted([t for t in tags_set if t])

    # ===================================================================
    #  SESSION STATE for filters
    # ===================================================================
    if "filters" not in st.session_state:
        st.session_state["filters"] = {
            "personas": [],
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
            "q": "",
            "has_metric": False,
        }

    F = st.session_state["filters"]

    # ===================================================================
    #  FILTER UI
    # ===================================================================
    # Row 1: Search and Audience
    c1, c2, c3 = st.columns([1, 0.8, 1.5])

    with c1:
        F["q"] = st.text_input(
            "Search keywords",
            value=F["q"],
            placeholder="Search by title, client, or keywords...",
            key="facet_q",
        )

    with c2:
        F["personas"] = st.multiselect(
            "Audience",
            personas_all,
            default=F["personas"],
            key="facet_personas",
        )

    with c3:
        # Domain category grouping
        domain_parts = []
        for d in domains:
            if " / " in d:
                cat, sub = d.split(" / ", 1)
                domain_parts.append((cat, sub, d))
            else:
                domain_parts.append(("", "", d))

        # Extract top-level categories where there's a " / " structure
        groups = sorted({cat for cat, sub, full in domain_parts if full})

        selected_group = st.selectbox(
            "Domain category",
            ["All"] + groups,
            key="facet_domain_group"
        )

    # Row 2: Domain details + additional filters
    c1, c2 = st.columns([1.5, 2.5])

    with c1:
        # Domain multiselect based on category
        def _fmt_sub(full_value: str) -> str:
            return (
                full_value.split(" / ")[-1] if " / " in full_value else full_value
            )

        if selected_group == "All":
            F["domains"] = st.multiselect(
                "Domain",
                options=domains,
                default=F["domains"],
                key="facet_domains_all",
                format_func=_fmt_sub,
            )
        else:
            subdomain_options = [
                full for cat, sub, full in domain_parts if cat == selected_group
            ]
            prev = [d for d in F.get("domains", []) if d in subdomain_options]
            F["domains"] = st.multiselect(
                "Domain",
                options=sorted(subdomain_options),
                default=prev,
                key="facet_subdomains",
                format_func=_fmt_sub,
            )

    with c2:
        # Optional filters in a compact row - NOW WITH CLIENT
        subcols = st.columns([1, 1, 1])  # Changed from [1, 1, 1.2] to [1, 1, 1, 1.2]

        with subcols[0]:
            F["clients"] = st.multiselect(
                "Client", clients, default=F["clients"], key="facet_clients"
            )

        with subcols[1]:
            F["roles"] = st.multiselect(
                "Role", roles, default=F["roles"], key="facet_roles"
            )

        with subcols[2]:
            F["tags"] = st.multiselect(
                "Tags", tags, default=F["tags"], key="facet_tags"
            )

    # Reset button
    cols = st.columns([1, 4])
    with cols[0]:
        def reset_filters():
            st.session_state["filters"] = {
                "personas": [],
                "clients": [],
                "domains": [],
                "roles": [],
                "tags": [],
                "q": "",
                "has_metric": False,
            }
            # Delete ALL widget state keys so they don't override the reset values
            widget_keys = [
                "facet_q",
                "facet_personas",
                "facet_clients",
                "facet_domain_group",
                "facet_domains_all",
                "facet_subdomains",
                "facet_roles",
                "facet_tags",
            ]
            for wk in widget_keys:
                if wk in st.session_state:
                    del st.session_state[wk]
            st.rerun()

        if st.button("Reset Filters", use_container_width=True, key="reset_filters_btn"):
            reset_filters()

    # ===================================================================
    #  APPLY FILTERS
    # ===================================================================
    def matches_filters(row, filters):
        # Text search
        if filters["q"]:
            q_lower = filters["q"].lower()
            searchable = (
                row.get("title", "")
                + " "
                + row.get("client", "")
                + " "
                + " ".join(row.get("tags", []))
                + " "
                + row.get("summary", "")
            ).lower()
            if q_lower not in searchable:
                return False

        # Persona
        if filters["personas"]:
            row_personas = set(row.get("personas", []))
            if not row_personas.intersection(set(filters["personas"])):
                return False

        # Client
        if filters["clients"]:
            if row.get("client", "") not in filters["clients"]:
                return False

        # Domain
        if filters["domains"]:
            row_domains = set(row.get("domains", []))
            if not row_domains.intersection(set(filters["domains"])):
                return False

        # Role
        if filters["roles"]:
            if row.get("role", "") not in filters["roles"]:
                return False

        # Tags
        if filters["tags"]:
            row_tags = set(row.get("tags", []))
            if not row_tags.intersection(set(filters["tags"])):
                return False

        # has_metric (if you want to support this)
        if filters.get("has_metric"):
            metrics_count = row.get("metrics", {}).get("count", 0)
            if metrics_count == 0:
                return False

        return True

    filtered_rows = [r for r in rows if matches_filters(r, F)]

    # ===================================================================
    #  SUMMARY STATS
    # ===================================================================
    total_projects = len(filtered_rows)

    # Count unique clients
    unique_clients = set(r.get("client", "") for r in filtered_rows if r.get("client"))

    # Count projects with metrics
    projects_with_metrics = sum(
        1 for r in filtered_rows if r.get("metrics", {}).get("count", 0) > 0
    )

    # Display summary stats
    st.write("")
    cols = st.columns(3)
    cols[0].metric("Total Projects", total_projects)
    cols[1].metric("Unique Clients", len(unique_clients))
    cols[2].metric("Projects with Metrics", projects_with_metrics)

    # ===================================================================
    #  PAGINATION
    # ===================================================================
    if "page_num" not in st.session_state:
        st.session_state["page_num"] = 1

    page_size = 10
    total_pages = (total_projects + page_size - 1) // page_size if total_projects > 0 else 1
    page_num = st.session_state["page_num"]

    # Ensure page_num is in valid range
    if page_num < 1:
        st.session_state["page_num"] = 1
        page_num = 1
    if page_num > total_pages:
        st.session_state["page_num"] = total_pages
        page_num = total_pages

    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size
    page_rows = filtered_rows[start_idx:end_idx]

    # ===================================================================
    #  RESULTS TABLE
    # ===================================================================
    if not page_rows:
        st.info("No projects match your filters. Try adjusting your criteria.")
    else:
        # Prepare data for AgGrid
        grid_data = []
        for r in page_rows:
            grid_data.append(
                {
                    "Title": r.get("title", ""),
                    "Client": r.get("client", ""),
                    "Domain": ", ".join(r.get("domains", [])),
                    "Role": r.get("role", ""),
                    "Tags": ", ".join(r.get("tags", [])[:3]),  # Limit tags display
                    "Personas": ", ".join(r.get("personas", [])),
                    "Pub Date": r.get("pub_date", ""),
                    "Metrics": r.get("metrics", {}).get("count", 0),
                    "URL": r.get("url", ""),
                    "Filename": r.get("filename", ""),
                }
            )

        # Configure AgGrid
        gb = GridOptionsBuilder.from_dataframe(
            pd.DataFrame(grid_data)
        )
        gb.configure_default_column(
            resizable=True,
            filterable=False,
            sortable=True,
            editable=False,
        )

        # Hide URL and Filename columns (we'll use them for click handling)
        gb.configure_column("URL", hide=True)
        gb.configure_column("Filename", hide=True)

        gb.configure_selection(selection_mode="single", use_checkbox=False)
        gb.configure_grid_options(
            domLayout="normal",
            rowHeight=70,
            enableCellTextSelection=True,
        )

        gridOptions = gb.build()

        # Display the grid
        grid_response = AgGrid(
            pd.DataFrame(grid_data),
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="streamlit",
            height=600,
            allow_unsafe_jscode=True,
        )

        # Handle row selection
        if grid_response and "selected_rows" in grid_response and grid_response["selected_rows"]:
            selected = grid_response["selected_rows"][0]
            filename = selected.get("Filename", "")
            if filename:
                # Store selected case study in session state
                st.session_state["selected_case_study"] = filename
                st.session_state["active_tab"] = "Ask MattGPT"
                st.rerun()

    # ===================================================================
    #  PAGINATION CONTROLS
    # ===================================================================
    if total_pages > 1:
        st.write("")
        cols = st.columns([1, 2, 1])

        with cols[1]:
            # Create pagination buttons
            pcols = st.columns(min(7, total_pages + 2))

            # Previous button
            with pcols[0]:
                if st.button("←", key="prev_page", disabled=(page_num <= 1)):
                    st.session_state["page_num"] = page_num - 1
                    st.rerun()

            # Page number buttons
            # Show up to 5 page numbers
            if total_pages <= 5:
                page_range = range(1, total_pages + 1)
            else:
                # Show current page and 2 pages before/after
                start = max(1, page_num - 2)
                end = min(total_pages, page_num + 2)
                page_range = range(start, end + 1)

            for i, p in enumerate(page_range, start=1):
                with pcols[i]:
                    if st.button(
                        str(p),
                        key=f"page_{p}",
                        type="primary" if p == page_num else "secondary",
                    ):
                        st.session_state["page_num"] = p
                        st.rerun()

            # Next button
            with pcols[-1]:
                if st.button("→", key="next_page", disabled=(page_num >= total_pages)):
                    st.session_state["page_num"] = page_num + 1
                    st.rerun()

        # Show page info
        st.write(
            f"<div style='text-align: center; color: #666; margin-top: 10px;'>"
            f"Page {page_num} of {total_pages} ({total_projects} projects)"
            f"</div>",
            unsafe_allow_html=True,
        )

import pandas as pd
