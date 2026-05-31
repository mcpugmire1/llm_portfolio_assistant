"""
Dark-mode-aware "How Agy Finds Your Stories" modal content.

These components.html blocks detect the parent page's theme and apply
appropriate styling for both light and dark modes.
"""


def get_how_agy_flow_html() -> str:
    """
    3-step flow visualization for How Agy Works modal.
    Theme-aware: detects dark mode from parent page.

    Updated May 2026 to reflect current architecture:
    - Pure semantic search (OpenAI text-embedding-3-small)
    - 5-stage pipeline (nonsense filters → semantic router → Pinecone → confidence gate → LLM)
    - Client diversity algorithm
    - Behavioral query specialization for interview prep
    """
    return """
    <div id="flow-container">
        <style>
            /* Base/Light theme variables */
            :root {
                --modal-bg: linear-gradient(135deg, #FAFAFA 0%, #F9FAFB 100%);
                --modal-border: #E5E7EB;
                --modal-card-bg: white;
                --modal-text-primary: #1F2937;
                --modal-text-secondary: #4B5563;
                --modal-text-muted: #6B7280;
                --modal-purple-text: #6B21A8;
                --modal-purple-border: #E9D5FF;
                --modal-blue-bg: #DBEAFE;
                --modal-blue-text: #1E40AF;
                --modal-blue-border: #BFDBFE;
                --modal-green-text: #065F46;
                --modal-green-border: #A7F3D0;
                --modal-orange-text: #92400E;
                --modal-orange-border: #FDE68A;
                --modal-pink-bg: #FCE7F3;
                --modal-pink-text: #9D174D;
                --modal-pink-border: #FBCFE8;
                --modal-pill-bg: #EDE9FE;
                --modal-pill-text: #7C3AED;
                --modal-pill-border: #DDD6FE;
                --modal-arrow: #A78BFA;
                --modal-accent-purple: #8B5CF6;
            }

            /* Dark theme overrides */
            .dark-theme {
                --modal-bg: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                --modal-border: #374151;
                --modal-card-bg: #1f2937;
                --modal-text-primary: #f3f4f6;
                --modal-text-secondary: #d1d5db;
                --modal-text-muted: #9ca3af;
                --modal-purple-text: #c4b5fd;
                --modal-purple-border: #4c1d95;
                --modal-blue-bg: #1e3a8a;
                --modal-blue-text: #93c5fd;
                --modal-blue-border: #1e40af;
                --modal-green-text: #6ee7b7;
                --modal-green-border: #065f46;
                --modal-orange-text: #fcd34d;
                --modal-orange-border: #92400e;
                --modal-pink-bg: #831843;
                --modal-pink-text: #f9a8d4;
                --modal-pink-border: #9d174d;
                --modal-pill-bg: #3b2e5a;
                --modal-pill-text: #c4b5fd;
                --modal-pill-border: #5b4b7a;
                --modal-arrow: #a78bfa;
                --modal-accent-purple: #a78bfa;
            }

            #flow-wrapper {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 28px;
                padding-bottom: 40px;
                margin-bottom: 20px;
                background: var(--modal-bg);
                border-radius: 16px;
                border: 2px solid var(--modal-border);
                transition: all 0.3s ease;
            }

            .step-header {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 20px;
            }

            .step-number {
                background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
                color: white;
                width: 48px;
                height: 48px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 22px;
                flex-shrink: 0;
                box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
            }

            .step-title {
                margin: 0;
                color: var(--modal-text-primary);
                font-size: 24px;
                font-weight: 700;
            }

            .step-content {
                margin-left: 64px;
            }

            .query-card {
                background: var(--modal-card-bg);
                padding: 24px;
                border-radius: 12px;
                border: 2px solid var(--modal-purple-border);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            .query-text {
                color: var(--modal-text-secondary);
                font-size: 16px;
                font-style: italic;
                line-height: 1.6;
            }

            .arrow {
                text-align: center;
                color: var(--modal-arrow);
                font-size: 40px;
                margin: 20px 0;
                font-weight: 300;
            }

            /* Pipeline visualization — lightweight flow/navigation.
               Equal-weight pills; the cards below carry hierarchy and emphasis.
               Container chrome (bg + border + padding) matches the tech section's
               .pipeline-flow so pills get the same visual framing. */
            .pipeline-flow {
                background: var(--modal-card-bg);
                border: 2px solid var(--modal-border);
                border-radius: 12px;
                padding: 16px 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            /* All pipeline pills share the same muted style — equal weight, no rainbow.
               The cards below carry the stage color via their borders. */
            .pipeline-stage {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 7px 13px;
                border-radius: 22px;
                font-size: 13px;
                font-weight: 600;
                background: var(--modal-card-bg);
                color: var(--modal-text-secondary);
                border: 1px solid var(--modal-border);
            }

            .pipeline-arrow {
                color: var(--modal-text-muted);
                font-size: 12px;
                font-weight: 400;
                opacity: 0.5;
            }

            .search-cards {
                display: flex;
                gap: 16px;
                margin-bottom: 16px;
            }

            .search-card {
                flex: 1;
                background: var(--modal-card-bg);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid var(--modal-border);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            /* Hero card styling — sizing + typography (border defined after
               stage-color rules below, so the purple override wins the cascade) */
            .search-card.hero {
                padding: 26px 24px;
            }

            .search-card.hero .card-title {
                font-size: 17px;
                font-weight: 800;
                margin-bottom: 10px;
            }

            .search-card.hero .card-desc {
                font-size: 14px;
            }

            /* Guardrail cards (filter + intent + confidence) — supporting, visually quieter */
            .search-card.guardrail {
                padding: 14px 16px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                opacity: 0.88;
            }

            .search-card.guardrail .card-title {
                font-size: 13px;
                font-weight: 600;
                margin-bottom: 6px;
            }

            .search-card.guardrail .card-desc {
                font-size: 12px;
            }

            /* Hero override — brand purple border + matching shadow.
               Higher specificity (.search-card.hero) beats the base .search-card
               border, so hero gets purple emphasis; all other cards keep
               the uniform 1px modal-border. */
            .search-card.hero {
                border: 2px solid var(--modal-accent-purple);
                box-shadow: 0 6px 18px rgba(139, 92, 246, 0.15);
            }

            .card-title {
                font-weight: 700;
                font-size: 15px;
                margin-bottom: 8px;
                color: var(--modal-text-primary);
            }

            .card-desc {
                font-size: 13px;
                line-height: 1.5;
                color: var(--modal-text-secondary);
            }

            .result-wrapper {
                background: var(--modal-card-bg);
                border: 3px solid #8B5CF6;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 8px 20px rgba(139, 92, 246, 0.25);
                box-sizing: border-box;
                max-width: 100%;
            }

            .result-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                box-sizing: border-box;
                max-width: 100%;
            }

            .result-title {
                font-weight: 700;
                font-size: 17px;
                margin-bottom: 8px;
            }

            .result-desc {
                font-size: 15px;
                opacity: 0.95;
                line-height: 1.6;
            }

            .pills {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }

            /* Result pills (Step 3) — quieter than pipeline pills so the pipeline
               section reads as the hero. Borderless, lighter weight; colored fill
               + colored text still carry the categorization signal. */
            .pill {
                background: var(--modal-pill-bg);
                color: var(--modal-pill-text);
                padding: 7px 13px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 500;
                border: none;
            }

            .pill.blue {
                background: #E0E7FF;
                color: #4F46E5;
                border-color: #C7D2FE;
            }

            .pill.green {
                background: #D1FAE5;
                color: #065F46;
                border-color: #A7F3D0;
            }

            .dark-theme .pill.blue {
                background: #312e81;
                color: #a5b4fc;
                border-color: #4338ca;
            }

            .dark-theme .pill.green {
                background: #064e3b;
                color: #6ee7b7;
                border-color: #065f46;
            }

            .step-section {
                margin-bottom: 48px;
            }

            .step-section:last-child {
                margin-bottom: 0;
            }

            /* Confidence badge — same demoted treatment as .pill (borderless, 500). */
            .confidence-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #D1FAE5;
                color: #065F46;
                padding: 7px 13px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 500;
                border: none;
            }

            .dark-theme .confidence-badge {
                background: #064e3b;
                color: #6ee7b7;
                border-color: #065f46;
            }
        </style>

        <div id="flow-wrapper">
            <!-- Step 1: You Ask -->
            <div class="step-section">
                <div class="step-header">
                    <div class="step-number">1</div>
                    <h3 class="step-title">You Ask</h3>
                </div>
                <div class="step-content">
                    <div class="query-card">
                        <div class="query-text">"Tell me about a time you dealt with a difficult stakeholder"</div>
                    </div>
                </div>
            </div>

            <!-- Arrow -->
            <div class="arrow">↓</div>

            <!-- Step 2: Agy Searches -->
            <div class="step-section">
                <div class="step-header">
                    <div class="step-number">2</div>
                    <h3 class="step-title">Agy Searches</h3>
                </div>
                <div class="step-content">
                    <!-- Pipeline visualization. Pills are lightweight navigation only —
                         equal weight, muted. The cards below carry the hierarchy
                         (hero stages 3 + 5, guardrails 1 / 2 / 4). -->
                    <div class="pipeline-flow">
                        <div class="pipeline-stage rules">Filters noisy input</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage router">Detects interview intent</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage retrieval">Retrieves stories</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage confidence">Refuses weak matches</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage generation">Synthesizes response</div>
                    </div>

                    <!-- 5 callouts, 1:1 with pipeline stages above.
                         Each callout's border color matches its corresponding
                         pipeline pill so the linkage is visual, not positional. -->
                    <!-- Callout cards carry the hierarchy: hero (3 + 5) vs guardrail (1, 2, 4).
                         Titles match the pipeline pill labels above verbatim. -->
                    <div class="search-cards">
                        <div class="search-card rules guardrail">
                            <div class="card-title">Filters irrelevant/noisy input</div>
                            <div class="card-desc">Homework requests, gibberish, and off-domain queries get bounced before they reach the model — no wasted cost, no off-topic answers</div>
                        </div>
                        <div class="search-card router guardrail">
                            <div class="card-title">Detects interview intent</div>
                            <div class="card-desc">Recognizes behavioral, technical, leadership, and background questions — and adapts the response style to fit hiring context</div>
                        </div>
                    </div>
                    <!-- Card 3 alone: hero treatment, full width -->
                    <div class="search-card retrieval hero" style="margin-bottom: 16px;">
                        <div class="card-title">Retrieves grounded experience stories</div>
                        <div class="card-desc">Pulls from Matt's actual 20+ years of work — never invents examples, never paraphrases someone else's resume</div>
                    </div>
                    <!-- Row 3: Cards 4 + 5 share a row (matches row 1 pattern) -->
                    <div class="search-cards">
                        <div class="search-card confidence guardrail">
                            <div class="card-title">Refuses weak matches / avoids fabrication</div>
                            <div class="card-desc">If the closest story isn't a strong fit, says "I don't know" instead of bluffing a stretch answer</div>
                        </div>
                        <div class="search-card generation guardrail">
                            <div class="card-title">Synthesizes a tailored interview response</div>
                            <div class="card-desc">Structures the answer for hiring decisions — situation, action, outcome — grounded in the retrieved stories, with distinctive phrases preserved verbatim</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Arrow -->
            <div class="arrow">↓</div>

            <!-- Step 3: You Get Results -->
            <div class="step-section">
                <div class="step-header">
                    <div class="step-number">3</div>
                    <h3 class="step-title">You Get Results</h3>
                </div>
                <div class="step-content">
                    <div class="result-wrapper">
                        <div class="result-card">
                            <div class="result-title">Navigating Executive Resistance at Fortune 100 Bank</div>
                            <div class="result-desc">Turned a skeptical CTO into a transformation champion through deep listening, small wins, and building trust over 6 months...</div>
                        </div>
                        <div class="pills">
                            <span class="pill">Stakeholder Management</span>
                            <span class="pill blue">Financial Services</span>
                            <span class="pill green">Leadership</span>
                            <span class="confidence-badge"><span>✓</span> High confidence match</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        (function() {
            // Detect dark mode from parent page
            function detectTheme() {
                try {
                    var parentBody = window.parent.document.body;
                    var isDark = parentBody.classList.contains('dark-theme') ||
                                 parentBody.getAttribute('data-theme') === 'dark';
                    return isDark;
                } catch(e) {
                    // Cross-origin fallback: check media query
                    return window.matchMedia('(prefers-color-scheme: dark)').matches;
                }
            }

            function applyTheme() {
                var container = document.getElementById('flow-wrapper');
                if (detectTheme()) {
                    container.classList.add('dark-theme');
                } else {
                    container.classList.remove('dark-theme');
                }
            }

            // Apply on load
            applyTheme();

            // Watch for theme class changes on parent body — no polling.
            try {
                new MutationObserver(applyTheme).observe(window.parent.document.body, {
                    attributes: true, attributeFilter: ['class', 'data-theme']
                });
            } catch(e) { setTimeout(applyTheme, 800); }
        })();
    </script>
    """


def get_technical_details_html() -> str:
    """
    Technical details section for How Agy Works modal.
    Theme-aware: detects dark mode from parent page.

    Updated May 2026 to reflect current architecture:
    - OpenAI text-embedding-3-small embeddings
    - 5-stage pipeline (nonsense filters → semantic router → Pinecone → confidence gate → LLM)
    - Client diversity algorithm for varied results
    - Behavioral query specialization for interview prep
    """
    return """
    <div id="tech-container">
        <style>
            :root {
                --modal-bg: linear-gradient(135deg, #FAFAFA 0%, #F9FAFB 100%);
                --modal-border: #E5E7EB;
                --modal-card-bg: white;
                --modal-text-primary: #1F2937;
                --modal-text-secondary: #4B5563;
                --modal-text-muted: #6B7280;
                --modal-purple-text: #6B21A8;
                --modal-purple-border: #E9D5FF;
                --modal-blue-bg: #DBEAFE;
                --modal-blue-text: #1E40AF;
                --modal-blue-border: #BFDBFE;
                --modal-green-text: #065F46;
                --modal-green-border: #A7F3D0;
                --modal-orange-text: #92400E;
                --modal-orange-border: #FDE68A;
                --modal-pink-bg: #FCE7F3;
                --modal-pink-text: #9D174D;
                --modal-pink-border: #FBCFE8;
                --modal-stat-color: #8B5CF6;
                --modal-divider: #E5E7EB;
                --modal-accent-purple: #8B5CF6;
            }

            .dark-theme {
                --modal-bg: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                --modal-border: #374151;
                --modal-card-bg: #1f2937;
                --modal-text-primary: #f3f4f6;
                --modal-text-secondary: #d1d5db;
                --modal-text-muted: #9ca3af;
                --modal-purple-text: #c4b5fd;
                --modal-purple-border: #4c1d95;
                --modal-blue-text: #93c5fd;
                --modal-blue-border: #1e40af;
                --modal-green-text: #6ee7b7;
                --modal-green-border: #065f46;
                --modal-orange-text: #fcd34d;
                --modal-orange-border: #78350f;
                --modal-stat-color: #a78bfa;
                --modal-divider: #374151;
                --modal-accent-purple: #a78bfa;
            }

            #tech-wrapper {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                transition: all 0.3s ease;
            }

            .tech-header {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 24px;
            }

            .tech-header h3 {
                margin: 0;
                color: var(--modal-text-primary);
                font-size: 24px;
                font-weight: 700;
            }

            .tech-content {
                padding: 26px;
                padding-bottom: 36px;
                background: var(--modal-bg);
                border-radius: 16px;
                border: 2px solid var(--modal-border);
            }

            .tech-cards {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }

            .tech-card {
                flex: 1;
                background: var(--modal-card-bg);
                padding: 20px;
                border-radius: 12px;
                border: 1px solid var(--modal-border);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            /* Hero card styling — sizing + typography (border defined after
               stage-color rules below, so the purple override wins the cascade) */
            .tech-card.hero {
                padding: 26px 24px;
            }

            .tech-card.hero .tech-card-header h4 {
                font-size: 18px;
                font-weight: 800;
            }

            .tech-card.hero ul {
                font-size: 14px;
            }

            /* Guardrail cards (filter + intent + confidence) — supporting, visually quieter */
            .tech-card.guardrail {
                padding: 14px 16px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                opacity: 0.88;
            }

            .tech-card.guardrail .tech-card-header h4 {
                font-size: 14px;
                font-weight: 600;
            }

            .tech-card.guardrail ul {
                font-size: 12px;
                line-height: 1.6;
            }

            /* Hero override — brand purple border + matching shadow.
               Higher specificity (.tech-card.hero) beats the base .tech-card
               border, so hero gets purple emphasis; all other cards keep
               the uniform 1px modal-border. */
            .tech-card.hero {
                border: 2px solid var(--modal-accent-purple);
                box-shadow: 0 6px 18px rgba(139, 92, 246, 0.15);
            }

            .tech-card-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 12px;
            }

            .tech-card-header span {
                font-size: 22px;
            }

            .tech-card-header h4 {
                margin: 0;
                font-size: 16px;
                font-weight: 700;
                color: var(--modal-text-primary);
            }

            .tech-card ul {
                margin: 0;
                padding-left: 18px;
                color: var(--modal-text-secondary);
                line-height: 1.7;
                font-size: 13px;
            }

            .tech-card strong { color: var(--modal-text-primary); }

            .pipeline-flow {
                background: var(--modal-card-bg);
                border: 2px solid var(--modal-border);
                border-radius: 12px;
                padding: 16px 24px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                flex-wrap: wrap;
            }

            /* All pipeline pills share the same muted style — equal weight, no rainbow.
               The cards below carry the stage color via their borders.
               Matches the flow section's .pipeline-stage exactly. */
            .pipeline-stage {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 7px 13px;
                border-radius: 22px;
                font-size: 13px;
                font-weight: 600;
                background: var(--modal-card-bg);
                color: var(--modal-text-secondary);
                border: 1px solid var(--modal-border);
            }

            .pipeline-arrow {
                color: var(--modal-text-muted);
                font-size: 12px;
                opacity: 0.5;
            }

            .stats-bar {
                background: var(--modal-card-bg);
                padding: 16px 24px;
                border-radius: 12px;
                border: 2px solid var(--modal-border);
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                display: flex;
                justify-content: space-around;
                align-items: center;
            }

            .stat {
                text-align: center;
            }

            .stat-value {
                font-size: 24px;
                font-weight: 700;
                color: var(--modal-stat-color);
                margin-bottom: 2px;
            }

            .stat-label {
                font-size: 12px;
                color: var(--modal-text-muted);
                font-weight: 500;
            }

            .stat-divider {
                width: 1px;
                height: 36px;
                background: var(--modal-divider);
            }
        </style>

        <div id="tech-wrapper">
            <div class="tech-header">
                <h3>Technical Details</h3>
            </div>
            <div class="tech-content">
                <!-- 5-Stage Pipeline Visualization. Pills are lightweight navigation only —
                     equal weight, muted. The cards below carry the hierarchy. -->
                <div class="pipeline-flow">
                    <div class="pipeline-stage rules">Filters noisy input</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage router">Detects interview intent</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage retrieval">Retrieves stories</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage confidence">Refuses weak matches</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage generation">Synthesizes response</div>
                </div>

                <!-- 5 tech-cards, 1:1 with pipeline stages above.
                     Each card's border color matches its corresponding pipeline pill;
                     body text stays neutral (no stage-colored headings or strong tags).

                     Hierarchy: hero (3 + 5) vs guardrail (1, 2, 4). -->

                <!-- Row 1: Guardrails (Filters + Detects intent) -->
                <div class="tech-cards">
                    <div class="tech-card rules guardrail">
                        <div class="tech-card-header">
                            <h4>Filters irrelevant/noisy input</h4>
                        </div>
                        <ul>
                            <li><strong>Regex-based</strong> nonsense rejection (sub-millisecond)</li>
                            <li>Catches homework asks, gibberish, off-domain queries</li>
                            <li><strong>No LLM cost</strong> for rejected queries</li>
                        </ul>
                    </div>

                    <div class="tech-card router guardrail">
                        <div class="tech-card-header">
                            <h4>Detects interview intent</h4>
                        </div>
                        <ul>
                            <li><strong>Semantic router</strong> classifies into 15 intent families</li>
                            <li>Background, behavioral, technical, leadership, synthesis, etc.</li>
                            <li>Detects <strong>out-of-scope</strong> and personal queries before retrieval</li>
                        </ul>
                    </div>
                </div>

                <!-- HERO: Retrieves grounded stories (full width) -->
                <div class="tech-cards">
                    <div class="tech-card retrieval hero">
                        <div class="tech-card-header">
                            <h4>Retrieves grounded experience stories</h4>
                        </div>
                        <ul>
                            <li><strong>Pinecone</strong> top-K vector search</li>
                            <li><strong>OpenAI text-embedding-3-small</strong> (1536 dimensions)</li>
                            <li><strong>Entity-aware pinning</strong> for known clients, employers, divisions</li>
                        </ul>
                    </div>
                </div>

                <!-- Row 3: Cards 4 + 5 share a row (matches row 1 pattern) -->
                <div class="tech-cards">
                    <div class="tech-card confidence guardrail">
                        <div class="tech-card-header">
                            <h4>Refuses weak matches / avoids fabrication</h4>
                        </div>
                        <ul>
                            <li><strong>Confidence gate</strong> inspects top match similarity</li>
                            <li>Below threshold → "no strong matches" response</li>
                            <li>Prevents <strong>low-quality fabrication</strong></li>
                        </ul>
                    </div>
                    <div class="tech-card generation guardrail">
                        <div class="tech-card-header">
                            <h4>Synthesizes a tailored interview response</h4>
                        </div>
                        <ul>
                            <li><strong>GPT-4o</strong> grounded synthesis</li>
                            <li><strong>&lt;primary_story&gt;</strong> + <strong>&lt;supporting_story&gt;</strong> XML tags prevent cross-story bleed</li>
                            <li><strong>STAR format</strong> for behavioral queries — distinctive phrases preserved verbatim</li>
                        </ul>
                    </div>
                </div>

                <!-- Stats Bar -->
                <div class="stats-bar">
                    <div class="stat">
                        <div class="stat-value">100+</div>
                        <div class="stat-label">Stories</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">20+</div>
                        <div class="stat-label">Years</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">6</div>
                        <div class="stat-label">Industries</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">5</div>
                        <div class="stat-label">Pipeline Stages</div>
                    </div>
                </div>

                <!-- Design Spec Link -->
                <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(139, 92, 246, 0.2); text-align: center;">
                    <p style="margin: 0; color: #64748b; font-size: 0.95rem;">
                        Want to go deeper?
                        <a href="https://mcpugmire1.github.io/mattgpt-design-spec/"
                           target="_blank"
                           rel="noopener noreferrer"
                           style="color: #8B5CF6; text-decoration: none; font-weight: 500; margin-left: 0.25rem;">
                            View the full design specification →
                        </a>
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        (function() {
            function detectTheme() {
                try {
                    var parentBody = window.parent.document.body;
                    var isDark = parentBody.classList.contains('dark-theme') ||
                                 parentBody.getAttribute('data-theme') === 'dark';
                    return isDark;
                } catch(e) {
                    return window.matchMedia('(prefers-color-scheme: dark)').matches;
                }
            }

            function applyTheme() {
                var container = document.getElementById('tech-wrapper');
                if (detectTheme()) {
                    container.classList.add('dark-theme');
                } else {
                    container.classList.remove('dark-theme');
                }
            }

            applyTheme();

            // Watch for theme class changes on parent body — no polling.
            try {
                new MutationObserver(applyTheme).observe(window.parent.document.body, {
                    attributes: true, attributeFilter: ['class', 'data-theme']
                });
            } catch(e) { setTimeout(applyTheme, 800); }
        })();
    </script>
    """
