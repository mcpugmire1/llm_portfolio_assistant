"""
Dark-mode-aware "How Agy Finds Your Stories" modal content.

These components.html blocks detect the parent page's theme and apply
appropriate styling for both light and dark modes.
"""


def get_how_agy_flow_html() -> str:
    """
    3-step flow visualization for How Agy Works modal.
    Theme-aware: detects dark mode from parent page.

    Updated Dec 2024 to reflect current architecture:
    - Pure semantic search (OpenAI text-embedding-3-small)
    - 3-stage quality pipeline (rules → semantic router → confidence)
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
                --modal-blue-text: #1E40AF;
                --modal-blue-border: #BFDBFE;
                --modal-green-text: #065F46;
                --modal-green-border: #A7F3D0;
                --modal-orange-text: #92400E;
                --modal-orange-border: #FDE68A;
                --modal-pill-bg: #EDE9FE;
                --modal-pill-text: #7C3AED;
                --modal-pill-border: #DDD6FE;
                --modal-arrow: #A78BFA;
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
                --modal-blue-text: #93c5fd;
                --modal-blue-border: #1e40af;
                --modal-green-text: #6ee7b7;
                --modal-green-border: #065f46;
                --modal-orange-text: #fcd34d;
                --modal-orange-border: #92400e;
                --modal-pill-bg: #3b2e5a;
                --modal-pill-text: #c4b5fd;
                --modal-pill-border: #5b4b7a;
                --modal-arrow: #a78bfa;
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

            /* Pipeline visualization */
            .pipeline-flow {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            .pipeline-stage {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 10px 16px;
                border-radius: 24px;
                font-size: 13px;
                font-weight: 600;
            }

            .pipeline-stage.rules {
                background: #FEF3C7;
                color: #92400E;
                border: 2px solid #FDE68A;
            }

            .pipeline-stage.router {
                background: #D1FAE5;
                color: #065F46;
                border: 2px solid #A7F3D0;
            }

            .pipeline-stage.confidence {
                background: #EDE9FE;
                color: #5B21B6;
                border: 2px solid #DDD6FE;
            }

            .dark-theme .pipeline-stage.rules {
                background: #78350f;
                color: #fef3c7;
                border-color: #92400e;
            }

            .dark-theme .pipeline-stage.router {
                background: #064e3b;
                color: #d1fae5;
                border-color: #065f46;
            }

            .dark-theme .pipeline-stage.confidence {
                background: #4c1d95;
                color: #ede9fe;
                border-color: #5b21b6;
            }

            .pipeline-arrow {
                color: var(--modal-text-muted);
                font-size: 16px;
                font-weight: bold;
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
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            .search-card.semantic {
                border: 2px solid var(--modal-purple-border);
            }

            .search-card.behavioral {
                border: 2px solid var(--modal-green-border);
            }

            .search-card.diversity {
                border: 2px solid var(--modal-orange-border);
            }

            .card-title {
                font-weight: 700;
                font-size: 15px;
                margin-bottom: 8px;
            }

            .card-title.semantic { color: #7C3AED; }
            .card-title.behavioral { color: #059669; }
            .card-title.diversity { color: #D97706; }

            .dark-theme .card-title.behavioral { color: #6ee7b7; }
            .dark-theme .card-title.diversity { color: #fbbf24; }

            .card-desc {
                font-size: 13px;
                line-height: 1.5;
            }

            .card-desc.semantic { color: var(--modal-purple-text); }
            .card-desc.behavioral { color: var(--modal-green-text); }
            .card-desc.diversity { color: var(--modal-orange-text); }

            .result-wrapper {
                background: var(--modal-card-bg);
                border: 3px solid #8B5CF6;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 8px 20px rgba(139, 92, 246, 0.25);
            }

            .result-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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

            .pill {
                background: var(--modal-pill-bg);
                color: var(--modal-pill-text);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 700;
                border: 2px solid var(--modal-pill-border);
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

            .confidence-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #D1FAE5;
                color: #065F46;
                padding: 6px 12px;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 12px;
            }

            .dark-theme .confidence-badge {
                background: #064e3b;
                color: #6ee7b7;
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
                    <!-- Pipeline visualization -->
                    <div class="pipeline-flow">
                        <div class="pipeline-stage rules">⚡ Quality Filter</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage router">🎯 Intent Router</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage confidence">📊 Confidence Gate</div>
                    </div>

                    <div class="search-cards">
                        <div class="search-card semantic">
                            <div class="card-title semantic">🧠 Semantic Search</div>
                            <div class="card-desc semantic">Finds stories by meaning using AI embeddings, not just keyword matching</div>
                        </div>
                        <div class="search-card behavioral">
                            <div class="card-title behavioral">🎤 Interview Mode</div>
                            <div class="card-desc behavioral">Recognizes behavioral questions and surfaces leadership & soft-skill stories</div>
                        </div>
                    </div>
                    <div class="search-card diversity" style="margin-top: 0;">
                        <div class="card-title diversity">🎯 Best Match</div>
                        <div class="card-desc diversity">Prioritizes the best match for your question type—whether it's a specific client story or a career theme</div>
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
                        </div>
                        <div class="confidence-badge">
                            <span>✓</span> High confidence match
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

            // Re-check periodically (for dynamic theme switches)
            setInterval(applyTheme, 1000);
        })();
    </script>
    """


def get_technical_details_html() -> str:
    """
    Technical details section for How Agy Works modal.
    Theme-aware: detects dark mode from parent page.

    Updated Dec 2024 to reflect current architecture:
    - OpenAI text-embedding-3-small embeddings
    - 3-stage quality filtering pipeline (rules → semantic router → confidence)
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
                --modal-blue-text: #1E40AF;
                --modal-blue-border: #BFDBFE;
                --modal-green-text: #065F46;
                --modal-green-border: #A7F3D0;
                --modal-orange-text: #92400E;
                --modal-orange-border: #FDE68A;
                --modal-stat-color: #8B5CF6;
                --modal-divider: #E5E7EB;
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
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            .tech-card.search {
                border: 2px solid var(--modal-purple-border);
            }

            .tech-card.quality {
                border: 2px solid var(--modal-green-border);
            }

            .tech-card.diversity {
                border: 2px solid var(--modal-orange-border);
            }

            .tech-card.data {
                border: 2px solid var(--modal-blue-border);
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
            }

            .tech-card.search h4 { color: #7C3AED; }
            .tech-card.quality h4 { color: #059669; }
            .tech-card.diversity h4 { color: #D97706; }
            .tech-card.data h4 { color: #2563EB; }

            .dark-theme .tech-card.quality h4 { color: #6ee7b7; }
            .dark-theme .tech-card.diversity h4 { color: #fbbf24; }

            .tech-card ul {
                margin: 0;
                padding-left: 18px;
                color: var(--modal-text-secondary);
                line-height: 1.7;
                font-size: 13px;
            }

            .tech-card.search strong { color: var(--modal-purple-text); }
            .tech-card.quality strong { color: var(--modal-green-text); }
            .tech-card.diversity strong { color: var(--modal-orange-text); }
            .tech-card.data strong { color: var(--modal-blue-text); }

            .pipeline-flow {
                background: var(--modal-card-bg);
                border: 2px solid var(--modal-border);
                border-radius: 12px;
                padding: 16px 24px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                flex-wrap: wrap;
            }

            .pipeline-stage {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 14px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
            }

            .pipeline-stage.rules {
                background: #FEF3C7;
                color: #92400E;
                border: 1px solid #FDE68A;
            }

            .pipeline-stage.router {
                background: #D1FAE5;
                color: #065F46;
                border: 1px solid #A7F3D0;
            }

            .pipeline-stage.confidence {
                background: #EDE9FE;
                color: #5B21B6;
                border: 1px solid #DDD6FE;
            }

            .dark-theme .pipeline-stage.rules {
                background: #78350f;
                color: #fef3c7;
                border-color: #92400e;
            }

            .dark-theme .pipeline-stage.router {
                background: #064e3b;
                color: #d1fae5;
                border-color: #065f46;
            }

            .dark-theme .pipeline-stage.confidence {
                background: #4c1d95;
                color: #ede9fe;
                border-color: #5b21b6;
            }

            .pipeline-arrow {
                color: var(--modal-text-muted);
                font-size: 18px;
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
                <!-- 3-Stage Pipeline Visualization -->
                <div class="pipeline-flow">
                    <div class="pipeline-stage rules">⚡ Rules Filter</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage router">🎯 Semantic Router</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage confidence">📊 Confidence Gate</div>
                </div>

                <!-- Row 1: Search + Quality -->
                <div class="tech-cards">
                    <div class="tech-card search">
                        <div class="tech-card-header">
                            <span>🔍</span>
                            <h4>Semantic Search</h4>
                        </div>
                        <ul>
                            <li><strong>OpenAI text-embedding-3-small</strong></li>
                            <li><strong>Pinecone</strong> vector database</li>
                            <li>Semantic + keyword hybrid scoring</li>
                        </ul>
                    </div>

                    <div class="tech-card quality">
                        <div class="tech-card-header">
                            <span>🛡️</span>
                            <h4>3-Stage Quality Pipeline</h4>
                        </div>
                        <ul>
                            <li><strong>Stage 1:</strong> Fast rules-based nonsense detection</li>
                            <li><strong>Stage 2:</strong> Semantic router intent classification</li>
                            <li><strong>Stage 3:</strong> Confidence scoring & gating</li>
                        </ul>
                    </div>
                </div>

                <!-- Row 2: Diversity + Data -->
                <div class="tech-cards">
                    <div class="tech-card diversity">
                        <div class="tech-card-header">
                            <span>🎯</span>
                            <h4>Smart Ranking</h4>
                        </div>
                        <ul>
                            <li><strong>Best semantic match</strong> always surfaces first</li>
                            <li>Adapts ranking to question type</li>
                            <li>Client variety for broad queries</li>
                        </ul>
                    </div>

                    <div class="tech-card data">
                        <div class="tech-card-header">
                            <span>📚</span>
                            <h4>Story Architecture</h4>
                        </div>
                        <ul>
                            <li><strong>STAR format</strong> + 5P framework</li>
                            <li>Category/Sub-category/Theme taxonomy</li>
                            <li><strong>Behavioral interview</strong> specialization</li>
                        </ul>
                    </div>
                </div>

                <!-- Stats Bar -->
                <div class="stats-bar">
                    <div class="stat">
                        <div class="stat-value">130+</div>
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
                        <div class="stat-value">3</div>
                        <div class="stat-label">Quality Stages</div>
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
            setInterval(applyTheme, 1000);
        })();
    </script>
    """
