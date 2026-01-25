"""
Panel Interactions Module
Contains JavaScript for drag, resize, minimize, maximize, and close functionality.
Uses gridstack.js for dashboard grid layout.
"""
from nicegui import ui


def get_panel_interactions_js() -> str:
    """
    Returns JavaScript code for panel interactions using gridstack.js.
    Each card is a resizable, draggable grid item.
    """
    return '''
    <link href="https://cdn.jsdelivr.net/npm/gridstack@10.3.1/dist/gridstack.min.css" rel="stylesheet"/>
    <link href="https://cdn.jsdelivr.net/npm/gridstack@10.3.1/dist/gridstack-extra.min.css" rel="stylesheet"/>
    <script src="https://cdn.jsdelivr.net/npm/gridstack@10.3.1/dist/gridstack-all.js"></script>
    <script>
    (function() {
        // Prevent multiple initializations
        if (window.gridstackInitialized) {
            console.log('Gridstack already initialized, skipping...');
            return;
        }
        window.gridstackInitialized = true;

        let grid = null;
        const cardsSelector = '.panels-grid > .q-card';

        const cardConfigs = {
            'plot': { w: 12, h: 6, title: '📊 Live Sync Metrics' },
            'upload': { w: 6, h: 5, title: '📤 Upload & Process Files' },
            'storage': { w: 6, h: 5, title: '💾 Storage Browser' }
        };

        function initGridStack() {
            if (grid) return;

            const container = document.querySelector('.panels-grid');
            if (!container) {
                console.log('Container .panels-grid not found');
                return;
            }

            container.classList.add('grid-stack');

            grid = GridStack.init({
                column: 12,
                cellHeight: 70,
                margin: 8,
                float: true,
                animate: true,
                resizable: { handles: 'e, se, s, sw, w' },
                draggable: { handle: '.gs-header' }
            }, container);

            console.log('Gridstack initialized');

            grid.on('resizestop', function() {
                window.dispatchEvent(new Event('resize'));
            });
        }

        function addCardToGrid(cardElement) {
            if (cardElement.dataset.gridstackAdded) return;

            // Get section type from data-section attribute
            const section = cardElement.getAttribute('data-section') || 'default';
            const config = cardConfigs[section] || { w: 6, h: 4, title: section };

            console.log('Adding card to grid:', section);

            // Create grid-stack-item wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'grid-stack-item';
            wrapper.setAttribute('gs-w', config.w);
            wrapper.setAttribute('gs-h', config.h);
            wrapper.setAttribute('gs-x', '0');
            wrapper.setAttribute('gs-y', 'auto');
            wrapper.setAttribute('gs-id', section);

            // Create content wrapper with header
            const content = document.createElement('div');
            content.className = 'grid-stack-item-content';
            content.dataset.section = section;

            // Header for drag handle
            const header = document.createElement('div');
            header.className = 'gs-header';
            header.innerHTML = `
                <span class="gs-title">${config.title}</span>
                <div class="gs-controls">
                    <button class="gs-btn" data-action="minimize" title="Minimize">−</button>
                    <button class="gs-btn" data-action="maximize" title="Maximize">□</button>
                    <button class="gs-btn gs-btn-close" data-action="close" title="Close">✕</button>
                </div>
            `;

            // Body to hold card content
            const body = document.createElement('div');
            body.className = 'gs-body';

            // Move original card content into body
            while (cardElement.firstChild) {
                body.appendChild(cardElement.firstChild);
            }

            content.appendChild(header);
            content.appendChild(body);
            wrapper.appendChild(content);

            // Add to grid
            grid.addWidget(wrapper);

            // Mark original and hide
            cardElement.dataset.gridstackAdded = 'true';
            cardElement.style.display = 'none';

            // Setup button handlers
            setupButtons(wrapper, section);

            // Trigger resize for charts
            setTimeout(() => window.dispatchEvent(new Event('resize')), 200);

            console.log('Card added:', section);
        }

        function setupButtons(wrapper, section) {
            let originalSize = null;
            let isMinimized = false;
            let isMaximized = false;

            wrapper.querySelectorAll('.gs-btn').forEach(btn => {
                btn.onclick = function(e) {
                    e.stopPropagation();
                    const action = btn.dataset.action;
                    const body = wrapper.querySelector('.gs-body');

                    if (action === 'minimize') {
                        if (isMinimized) {
                            body.style.display = '';
                            wrapper.classList.remove('gs-minimized');
                            if (originalSize) grid.update(wrapper, { h: originalSize.h });
                            isMinimized = false;
                            btn.innerHTML = '−';
                        } else {
                            originalSize = {
                                w: parseInt(wrapper.getAttribute('gs-w')),
                                h: parseInt(wrapper.getAttribute('gs-h'))
                            };
                            body.style.display = 'none';
                            wrapper.classList.add('gs-minimized');
                            grid.update(wrapper, { h: 1 });
                            isMinimized = true;
                            btn.innerHTML = '+';
                        }
                    } else if (action === 'maximize') {
                        if (isMaximized) {
                            wrapper.classList.remove('gs-maximized');
                            if (originalSize) {
                                grid.update(wrapper, {
                                    w: originalSize.w,
                                    h: originalSize.h,
                                    x: originalSize.x,
                                    y: originalSize.y
                                });
                            }
                            isMaximized = false;
                            btn.innerHTML = '□';
                            grid.setStatic(false);
                        } else {
                            originalSize = {
                                w: parseInt(wrapper.getAttribute('gs-w')),
                                h: parseInt(wrapper.getAttribute('gs-h')),
                                x: parseInt(wrapper.getAttribute('gs-x')),
                                y: parseInt(wrapper.getAttribute('gs-y'))
                            };
                            wrapper.classList.add('gs-maximized');
                            grid.update(wrapper, { w: 12, h: 8, x: 0, y: 0 });
                            isMaximized = true;
                            btn.innerHTML = '❐';
                            grid.setStatic(true);
                        }
                    } else if (action === 'close') {
                        grid.removeWidget(wrapper);
                        // Allow re-adding
                        const orig = document.querySelector(`.q-card[data-section="${section}"]`);
                        if (orig) orig.dataset.gridstackAdded = '';
                    }

                    window.dispatchEvent(new Event('resize'));
                };
            });
        }

        // MutationObserver to detect new cards
        const observer = new MutationObserver((mutations) => {
            let found = false;
            document.querySelectorAll(cardsSelector).forEach(card => {
                if (!card.dataset.gridstackAdded) {
                    found = true;
                }
            });
            if (found) {
                if (!grid) initGridStack();
                if (grid) {
                    document.querySelectorAll(cardsSelector).forEach(card => {
                        if (!card.dataset.gridstackAdded) {
                            addCardToGrid(card);
                        }
                    });
                }
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });

        // Fallback timeout
        setTimeout(() => {
            if (!grid) initGridStack();
            if (grid) {
                document.querySelectorAll(cardsSelector).forEach(addCardToGrid);
            }
        }, 2000);

        // Expose for debugging
        window.gsGrid = () => grid;
        window.gsAddCard = addCardToGrid;

        console.log('Gridstack panel system ready');
    })();
    </script>
    '''


def inject_panel_interactions():
    """Inject panel interactions JavaScript into the page."""
    ui.add_body_html(get_panel_interactions_js())
