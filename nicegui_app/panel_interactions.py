"""
Panel Interactions Module
Contains JavaScript for drag, resize, float, minimize, maximize, and close functionality.
Uses interact.js for drag-and-drop and resizing.
"""
from nicegui import ui


def get_panel_interactions_js() -> str:
    """
    Returns JavaScript code for panel interactions (drag, resize, float, etc.).
    Each card is independent and moveable within the browser.
    """
    return '''
    <script src="https://cdn.jsdelivr.net/npm/interactjs@1.10.17/dist/interact.min.js"></script>
    <script>
    (function() {
        const panelConfig = {
            plot: { 
                title: '📊 Live Sync Metrics', 
                wide: true,
                windowType: 'plotting',
                description: 'Independent resizable window for Live Sync Metrics charts',
                resizable: true,
                minWidth: 400,
                minHeight: 300
            },
            upload: { 
                title: '📤 Upload & Process Files',
                windowType: 'upload',
                description: 'Independent window for file upload and processing',
                resizable: true,
                minWidth: 250,
                minHeight: 200
            },
            storage: { 
                title: '💾 Storage Browser',
                windowType: 'storage',
                description: 'Independent window for file storage browser',
                resizable: true,
                minWidth: 250,
                minHeight: 200
            },
            'navbar-left': { title: '🧭 Navbar - Actions', navbar: true },
            'navbar-center': { title: '🧭 Navbar - Status', navbar: true },
            'navbar-right': { title: '🧭 Navbar - Info', navbar: true }
        };

        let panelInstances = new Map();
        let closedPanels = new Map();
        
        const CardLogger = {
            log: function(operation, cardTitle, details) {
                const timestamp = new Date().toISOString();
                const logEntry = {
                    timestamp: timestamp,
                    operation: operation,
                    card: cardTitle,
                    details: details || {}
                };
                console.log(`[CARD ${operation}]`, cardTitle, details || '');
                return logEntry;
            },
            
            validateResize: function(panel, newWidth, newHeight) {
                const instance = panelInstances.get(panel.dataset.panelId);
                if (!instance) {
                    console.error('[VALIDATION ERROR] Panel instance not found for resize');
                    return false;
                }
                
                const isPlottingWindow = panel.dataset.windowType === 'plotting' || 
                                       panel.querySelector('[data-section="plot"]');
                const minWidth = isPlottingWindow ? 400 : 250;
                const minHeight = isPlottingWindow ? 300 : 200;
                
                if (newWidth < minWidth || newHeight < minHeight) {
                    console.warn('[VALIDATION WARNING] Resize below minimum:', {
                        newWidth, newHeight, minWidth, minHeight
                    });
                    return false;
                }
                
                if (newWidth > window.innerWidth || newHeight > window.innerHeight - 80) {
                    console.warn('[VALIDATION WARNING] Resize exceeds viewport:', {
                        newWidth, newHeight, maxWidth: window.innerWidth, maxHeight: window.innerHeight - 80
                    });
                    return false;
                }
                
                return true;
            },
            
            validateFloat: function(panel, x, y) {
                const maxX = window.innerWidth - panel.offsetWidth;
                const maxY = window.innerHeight - panel.offsetHeight;
                const minX = 0;
                const minY = 80;
                
                if (x < minX || x > maxX || y < minY || y > maxY) {
                    console.warn('[VALIDATION WARNING] Float position out of bounds:', {
                        x, y, minX, maxX, minY, maxY
                    });
                    return false;
                }
                
                return true;
            },
            
            validateState: function(panel, operation) {
                const instance = panelInstances.get(panel.dataset.panelId);
                if (!instance) {
                    console.error('[VALIDATION ERROR] Panel instance not found for', operation);
                    return false;
                }
                
                const state = {
                    isFloating: panel.classList.contains('floating'),
                    isMaximized: panel.classList.contains('maximized'),
                    isMinimized: panel.classList.contains('minimized'),
                    isHidden: instance.isHidden || false,
                    isClosed: instance.isClosed || false
                };
                
                if (operation === 'minimize' && state.isMaximized) {
                    console.warn('[VALIDATION WARNING] Cannot minimize maximized card');
                    return false;
                }
                
                if (operation === 'maximize' && state.isMinimized) {
                    console.info('[VALIDATION INFO] Maximizing will remove minimized state');
                }
                
                if (operation === 'resize' && state.isMinimized) {
                    console.warn('[VALIDATION WARNING] Cannot resize minimized card');
                    return false;
                }
                
                return true;
            }
        };

        function wrapCardsInPanels() {
            console.log('wrapCardsInPanels called');
            const container = document.querySelector('.panels-grid');
            if (!container) {
                console.log('Container not found, retrying...');
                setTimeout(wrapCardsInPanels, 200);
                return;
            }

            console.log('Container found, wrapping cards...');
            const cards = container.querySelectorAll('[data-section]');
            console.log('Found', cards.length, 'cards to wrap');
            
            const allCards = container.querySelectorAll('.q-card, [class*="card"]');
            console.log('Found', allCards.length, 'total card elements');
            
            cards.forEach(card => {
                if (card.closest('.flexi-panel')) {
                    console.log('Card already wrapped:', card.getAttribute('data-section'));
                    return;
                }

                const section = card.getAttribute('data-section');
                const config = panelConfig[section] || { title: section };
                console.log('Wrapping card:', section, 'with config:', config);

                wrapCardInPanel(card, config);
            });
            
            const plotCard = container.querySelector('[data-section="plot"]');
            if (plotCard && !plotCard.closest('.flexi-panel')) {
                console.log('Found Live Sync Metrics card, wrapping now...');
                const config = panelConfig['plot'] || { title: '📊 Live Sync Metrics', windowType: 'plotting' };
                wrapCardInPanel(plotCard, config);
            }

            wrapNavbarComponents();

            setTimeout(() => {
                initPanelInteractions();
                verifyButtonsVisible();
            }, 100);
        }

        function wrapCardInPanel(card, config) {
            const panel = document.createElement('div');
            panel.className = 'flexi-panel' + (config.wide ? ' panel-wide' : '') + (config.navbar ? ' navbar-panel' : '');
            panel.dataset.panelId = 'panel-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            panel.dataset.section = config.title;
            
            if (config.windowType) {
                panel.dataset.windowType = config.windowType;
            }
            
            panel.id = 'panel-window-' + panel.dataset.panelId;
            
            if (config.description) {
                panel.title = config.description;
            }
            
            const header = document.createElement('div');
            header.className = 'flexi-panel-header';
            header.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;';
            
            const title = document.createElement('span');
            title.className = 'flexi-panel-title';
            title.textContent = config.title;
            title.style.cssText = 'color: white; font-weight: 600; font-size: 14px; flex: 1;';
            
            const controls = document.createElement('div');
            controls.className = 'flexi-panel-controls';
            controls.style.cssText = 'display: flex; gap: 6px; align-items: center; flex-shrink: 0;';
            
            const buttonStyle = 'width: 40px !important; height: 40px !important; min-width: 40px !important; min-height: 40px !important; border: 3px solid white !important; border-radius: 8px !important; background: white !important; color: #1e1e2e !important; cursor: pointer !important; font-size: 22px !important; font-weight: bold !important; line-height: 1 !important; display: inline-flex !important; align-items: center !important; justify-content: center !important; padding: 0 !important; margin: 0 3px !important; visibility: visible !important; opacity: 1 !important; box-shadow: 0 3px 8px rgba(0,0,0,0.4) !important; z-index: 1000 !important; position: relative !important;';
            
            const minimizeBtn = document.createElement('button');
            minimizeBtn.className = 'flexi-panel-btn';
            minimizeBtn.setAttribute('data-action', 'minimize');
            minimizeBtn.setAttribute('title', 'Minimize');
            minimizeBtn.setAttribute('type', 'button');
            minimizeBtn.innerHTML = '−';
            minimizeBtn.style.cssText = buttonStyle;
            
            const maximizeBtn = document.createElement('button');
            maximizeBtn.className = 'flexi-panel-btn';
            maximizeBtn.setAttribute('data-action', 'maximize');
            maximizeBtn.setAttribute('title', 'Maximize');
            maximizeBtn.setAttribute('type', 'button');
            maximizeBtn.innerHTML = '□';
            maximizeBtn.style.cssText = buttonStyle;
            
            const floatBtn = document.createElement('button');
            floatBtn.className = 'flexi-panel-btn';
            floatBtn.setAttribute('data-action', 'float');
            floatBtn.setAttribute('title', 'Float/Dock');
            floatBtn.setAttribute('type', 'button');
            floatBtn.innerHTML = '⧉';
            floatBtn.style.cssText = buttonStyle;
            
            const closeBtn = document.createElement('button');
            closeBtn.className = 'flexi-panel-btn';
            closeBtn.setAttribute('data-action', 'close');
            closeBtn.setAttribute('title', 'Close');
            closeBtn.setAttribute('type', 'button');
            closeBtn.innerHTML = '✕';
            closeBtn.style.cssText = buttonStyle;
            
            controls.appendChild(minimizeBtn);
            controls.appendChild(maximizeBtn);
            controls.appendChild(floatBtn);
            controls.appendChild(closeBtn);
            header.appendChild(title);
            header.appendChild(controls);
            
            minimizeBtn.addEventListener('click', function(e) {
                console.log('✓ Minimize button clicked for:', config.title);
            }, true);
            
            maximizeBtn.addEventListener('click', function(e) {
                console.log('✓ Maximize button clicked for:', config.title);
            }, true);
            
            const body = document.createElement('div');
            body.className = 'flexi-panel-body';
            body.dataset.panelBody = panel.dataset.panelId;

            const resizeHandle = document.createElement('div');
            resizeHandle.className = 'flexi-resize-handle';
            resizeHandle.title = 'Resize window';

            card.parentNode.insertBefore(panel, card);
            body.appendChild(card);
            panel.appendChild(header);
            panel.appendChild(body);
            panel.appendChild(resizeHandle);
            
            card.style.isolation = 'isolate';
            card.style.contain = 'layout style paint';

            panelInstances.set(panel.dataset.panelId, {
                panel: panel,
                header: header,
                body: body,
                card: card,
                originalParent: card.parentNode,
                originalNextSibling: card.nextSibling,
                config: config,
                isFloating: false,
                isMaximized: false,
                isMinimized: false,
                originalSize: null,
                originalPosition: null,
                windowType: config.windowType || 'default',
                independent: true,
                resizable: true,
                floatable: true
            });
            
            CardLogger.log('CARD_CREATED', config.title, {
                panelId: panel.dataset.panelId,
                windowType: config.windowType || 'default',
                capabilities: {
                    resizable: true,
                    floatable: true,
                    minimizable: true,
                    maximizable: true,
                    closeable: true,
                    independent: true
                }
            });
            
            console.log('Created independent entity:', config.title, 'Type:', config.windowType || 'default', 'ID:', panel.dataset.panelId);
        }

        function wrapNavbarComponents() {
            const navbarSections = document.querySelectorAll('header [data-section^="navbar"], .q-header [data-section^="navbar"]');
            if (navbarSections.length === 0) {
                console.log('No navbar sections found');
                return;
            }

            const container = document.querySelector('.panels-grid');
            if (!container) {
                console.log('Panels grid container not found');
                return;
            }

            console.log('Found', navbarSections.length, 'navbar sections');

            navbarSections.forEach((section) => {
                if (section.closest('.flexi-panel')) {
                    console.log('Navbar section already wrapped');
                    return;
                }

                const sectionType = section.getAttribute('data-section');
                let title = '🧭 Navigation';
                if (sectionType === 'navbar-left') title = '🧭 Navbar - Actions';
                else if (sectionType === 'navbar-center') title = '🧭 Navbar - Status';
                else if (sectionType === 'navbar-right') title = '🧭 Navbar - Info';

                const config = { 
                    title: title, 
                    navbar: true 
                };
                
                const card = document.createElement('div');
                card.className = 'q-card';
                card.setAttribute('data-section', sectionType);
                card.style.cssText = 'padding: 12px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; min-height: 60px; display: flex; flex-direction: column;';
                
                const clonedContent = section.cloneNode(true);
                clonedContent.removeAttribute('data-section');
                clonedContent.style.cssText = section.style.cssText || '';
                card.appendChild(clonedContent);
                
                wrapCardInPanel(card, config);
                const panel = card.closest('.flexi-panel');
                if (panel) {
                    container.appendChild(panel);
                    console.log('Added navbar panel:', sectionType);
                }
            });
        }

        function initPanelInteractions() {
            console.log('initPanelInteractions called, interact available:', typeof interact !== 'undefined');
            if (typeof interact === 'undefined') {
                console.log('interact.js not loaded, retrying...');
                setTimeout(initPanelInteractions, 200);
                return;
            }

            interact('.flexi-panel-header').unset();
            interact('.flexi-panel').unset();
            interact('.flexi-resize-handle').unset();

            console.log('Setting up draggable panels...');
            interact('.flexi-panel-header').draggable({
                allowFrom: '.flexi-panel-header',
                ignoreFrom: '.flexi-panel-btn',
                listeners: {
                    start(event) {
                        const panel = event.target.closest('.flexi-panel');
                        if (!panel) {
                            console.error('[DRAG ERROR] Panel not found');
                            return;
                        }
                        
                        const instance = panelInstances.get(panel.dataset.panelId);
                        const cardTitle = instance ? instance.config.title : 'Unknown';
                        
                        CardLogger.log('DRAG_START', cardTitle, {
                            wasFloating: panel.classList.contains('floating'),
                            position: {
                                left: panel.style.left,
                                top: panel.style.top
                            }
                        });
                        
                        if (!panel.classList.contains('floating')) {
                            const rect = panel.getBoundingClientRect();
                            const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
                            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
                            
                            panel.style.position = 'fixed';
                            panel.style.width = rect.width + 'px';
                            panel.style.height = rect.height + 'px';
                            panel.style.left = (rect.left + scrollX) + 'px';
                            panel.style.top = (rect.top + scrollY) + 'px';
                            panel.style.margin = '0';
                            panel.style.flex = 'none';
                            panel.style.maxWidth = 'none';
                            panel.style.zIndex = '1000';
                            panel.classList.add('floating');
                            
                            if (instance) {
                                instance.isFloating = true;
                                CardLogger.log('FLOAT_ENABLED', cardTitle, {
                                    position: { left: panel.style.left, top: panel.style.top },
                                    size: { width: panel.style.width, height: panel.style.height }
                                });
                            }
                        }
                    },
                    move(event) {
                        const panel = event.target.closest('.flexi-panel');
                        if (!panel || !panel.classList.contains('floating')) return;
                        
                        const instance = panelInstances.get(panel.dataset.panelId);
                        const cardTitle = instance ? instance.config.title : 'Unknown';
                        
                        const x = (parseFloat(panel.style.left) || 0) + event.dx;
                        const y = (parseFloat(panel.style.top) || 0) + event.dy;
                        
                        const maxX = window.innerWidth - panel.offsetWidth;
                        const maxY = window.innerHeight - panel.offsetHeight;
                        const minX = 0;
                        const minY = 80;
                        
                        const finalX = Math.max(minX, Math.min(x, maxX));
                        const finalY = Math.max(minY, Math.min(y, maxY));
                        
                        panel.style.left = finalX + 'px';
                        panel.style.top = finalY + 'px';
                    },
                    end(event) {
                        const panel = event.target.closest('.flexi-panel');
                        const instance = panelInstances.get(panel.dataset.panelId);
                        const cardTitle = instance ? instance.config.title : 'Unknown';
                        
                        CardLogger.log('DRAG_END', cardTitle, {
                            finalPosition: {
                                left: panel.style.left,
                                top: panel.style.top
                            },
                            isFloating: panel.classList.contains('floating')
                        });
                    }
                }
            });

            interact('.flexi-panel').resizable({
                edges: { left: true, right: true, bottom: true, top: true },
                listeners: {
                    start(event) {
                        const panel = event.target;
                        const instance = panelInstances.get(panel.dataset.panelId);
                        const cardTitle = instance ? instance.config.title : 'Unknown';
                        
                        if (!CardLogger.validateState(panel, 'resize')) {
                            console.error('[RESIZE ERROR] Invalid state for resize operation');
                            return false;
                        }
                        
                        CardLogger.log('RESIZE_START', cardTitle, {
                            currentSize: {
                                width: panel.offsetWidth,
                                height: panel.offsetHeight
                            },
                            isFloating: panel.classList.contains('floating'),
                            isMaximized: panel.classList.contains('maximized'),
                            isMinimized: panel.classList.contains('minimized')
                        });
                        
                        if (!panel.classList.contains('floating') && !panel.classList.contains('maximized')) {
                            const rect = panel.getBoundingClientRect();
                            const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
                            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
                            
                            panel.style.position = 'fixed';
                            panel.style.width = rect.width + 'px';
                            panel.style.height = rect.height + 'px';
                            panel.style.left = (rect.left + scrollX) + 'px';
                            panel.style.top = (rect.top + scrollY) + 'px';
                            panel.style.margin = '0';
                            panel.style.flex = 'none';
                            panel.style.maxWidth = 'none';
                            panel.style.zIndex = '1000';
                            panel.classList.add('floating');
                            
                            if (instance) {
                                instance.isFloating = true;
                                CardLogger.log('RESIZE_AUTO_FLOAT', cardTitle, {
                                    reason: 'Resize started on docked card'
                                });
                            }
                        }
                        
                        if (!panel.style.position || panel.style.position === 'relative') {
                            panel.style.position = 'fixed';
                        }
                    },
                    move(event) {
                        const panel = event.target;
                        const instance = panelInstances.get(panel.dataset.panelId);
                        const cardTitle = instance ? instance.config.title : 'Unknown';
                        
                        const newWidth = event.rect.width;
                        const newHeight = event.rect.height;
                        
                        if (!CardLogger.validateResize(panel, newWidth, newHeight)) {
                        }
                        
                        panel.style.width = newWidth + 'px';
                        panel.style.height = newHeight + 'px';
                        
                        if (event.deltaRect.left !== 0) {
                            const newLeft = (parseFloat(panel.style.left) || 0) + event.deltaRect.left;
                            panel.style.left = newLeft + 'px';
                        }
                        if (event.deltaRect.top !== 0) {
                            const newTop = (parseFloat(panel.style.top) || 0) + event.deltaRect.top;
                            panel.style.top = newTop + 'px';
                        }
                        
                        const isPlottingWindow = panel.dataset.windowType === 'plotting' || 
                                               panel.querySelector('[data-section="plot"]');
                        const minWidth = isPlottingWindow ? 400 : 250;
                        const minHeight = isPlottingWindow ? 300 : 200;
                        
                        if (parseFloat(panel.style.width) < minWidth) {
                            panel.style.width = minWidth + 'px';
                        }
                        if (parseFloat(panel.style.height) < minHeight) {
                            panel.style.height = minHeight + 'px';
                        }
                        
                        setTimeout(() => {
                            window.dispatchEvent(new Event('resize'));
                        }, 10);
                    },
                    end(event) {
                        const panel = event.target;
                        const instance = panelInstances.get(panel.dataset.panelId);
                        const cardTitle = instance ? instance.config.title : 'Unknown';
                        
                        CardLogger.log('RESIZE_END', cardTitle, {
                            finalSize: {
                                width: panel.style.width,
                                height: panel.style.height
                            },
                            position: {
                                left: panel.style.left,
                                top: panel.style.top
                            }
                        });
                    }
                },
                modifiers: [
                    interact.modifiers.restrictSize({
                        min: function(panel) {
                            const isPlottingWindow = panel.dataset.windowType === 'plotting' || 
                                                   panel.querySelector('[data-section="plot"]');
                            return {
                                width: isPlottingWindow ? 400 : 250,
                                height: isPlottingWindow ? 300 : 200
                            };
                        },
                        max: { width: window.innerWidth, height: window.innerHeight - 80 }
                    }),
                    interact.modifiers.restrictEdges({
                        outer: 'parent'
                    })
                ]
            });

            interact('.flexi-resize-handle').draggable({
                onstart: function(event) {
                    const panel = event.target.closest('.flexi-panel');
                    const instance = panelInstances.get(panel.dataset.panelId);
                    const cardTitle = instance ? instance.config.title : 'Unknown';
                    
                    CardLogger.log('RESIZE_HANDLE_START', cardTitle, {
                        wasFloating: panel.classList.contains('floating'),
                        currentSize: {
                            width: panel.offsetWidth,
                            height: panel.offsetHeight
                        }
                    });
                    
                    if (!panel.classList.contains('floating')) {
                        const rect = panel.getBoundingClientRect();
                        const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
                        const scrollY = window.pageYOffset || document.documentElement.scrollTop;
                        
                        panel.style.position = 'fixed';
                        panel.style.width = rect.width + 'px';
                        panel.style.height = rect.height + 'px';
                        panel.style.left = (rect.left + scrollX) + 'px';
                        panel.style.top = (rect.top + scrollY) + 'px';
                        panel.style.margin = '0';
                        panel.style.flex = 'none';
                        panel.style.maxWidth = 'none';
                        panel.style.zIndex = '1000';
                        panel.classList.add('floating');
                        
                        if (instance) {
                            instance.isFloating = true;
                            CardLogger.log('RESIZE_HANDLE_AUTO_FLOAT', cardTitle, {
                                reason: 'Resize handle used on docked card'
                            });
                        }
                    }
                },
                onmove: function(event) {
                    const panel = event.target.closest('.flexi-panel');
                    const instance = panelInstances.get(panel.dataset.panelId);
                    const cardTitle = instance ? instance.config.title : 'Unknown';
                    
                    const rect = panel.getBoundingClientRect();
                    const newWidth = rect.width + event.dx;
                    const newHeight = rect.height + event.dy;
                    
                    const isPlottingWindow = panel.dataset.windowType === 'plotting' || 
                                           panel.querySelector('[data-section="plot"]');
                    const minWidth = isPlottingWindow ? 400 : 250;
                    const minHeight = isPlottingWindow ? 300 : 200;
                    
                    if (!CardLogger.validateResize(panel, newWidth, newHeight)) {
                    }
                    
                    const finalWidth = Math.max(minWidth, newWidth);
                    const finalHeight = Math.max(minHeight, newHeight);
                    
                    panel.style.width = finalWidth + 'px';
                    panel.style.height = finalHeight + 'px';
                    
                    window.dispatchEvent(new Event('resize'));
                },
                onend: function(event) {
                    const panel = event.target.closest('.flexi-panel');
                    const instance = panelInstances.get(panel.dataset.panelId);
                    const cardTitle = instance ? instance.config.title : 'Unknown';
                    
                    CardLogger.log('RESIZE_HANDLE_END', cardTitle, {
                        finalSize: {
                            width: panel.style.width,
                            height: panel.style.height
                        }
                    });
                }
            });

            document.addEventListener('click', function(e) {
                const btn = e.target.closest('.flexi-panel-btn');
                if (!btn) return;

                e.stopPropagation();
                e.preventDefault();
                
                const panel = btn.closest('.flexi-panel');
                if (!panel) {
                    console.warn('Button clicked but panel not found');
                    return;
                }
                
                const action = btn.dataset.action;
                console.log('Button action triggered:', action, 'for panel:', panel.dataset.panelId);

                if (action === 'float') {
                    const panelId = panel.dataset.panelId;
                    const instance = panelInstances.get(panelId);
                    const cardTitle = instance ? instance.config.title : 'Unknown';
                    
                    if (panel.classList.contains('floating')) {
                        CardLogger.log('FLOAT_DOCK', cardTitle, {
                            previousState: {
                                position: { left: panel.style.left, top: panel.style.top },
                                size: { width: panel.style.width, height: panel.style.height }
                            }
                        });
                        
                        panel.classList.remove('floating');
                        panel.style.position = '';
                        panel.style.left = '';
                        panel.style.top = '';
                        panel.style.width = '';
                        panel.style.height = '';
                        panel.style.margin = '';
                        panel.style.flex = '';
                        panel.style.maxWidth = '';
                        
                        if (instance) {
                            instance.isFloating = false;
                        }
                    } else {
                        const rect = panel.getBoundingClientRect();
                        const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
                        const scrollY = window.pageYOffset || document.documentElement.scrollTop;
                        
                        const floatX = rect.left + scrollX;
                        const floatY = rect.top + scrollY;
                        
                        if (!CardLogger.validateFloat(panel, floatX, floatY)) {
                            console.warn('[FLOAT WARNING] Position may be out of bounds');
                        }
                        
                        panel.style.position = 'fixed';
                        panel.style.width = rect.width + 'px';
                        panel.style.height = rect.height + 'px';
                        panel.style.left = floatX + 'px';
                        panel.style.top = floatY + 'px';
                        panel.style.margin = '0';
                        panel.style.flex = 'none';
                        panel.style.maxWidth = 'none';
                        panel.classList.add('floating');
                        
                        if (instance) {
                            instance.isFloating = true;
                        }
                        
                        CardLogger.log('FLOAT_ENABLE', cardTitle, {
                            position: { x: floatX, y: floatY },
                            size: { width: rect.width, height: rect.height }
                        });
                    }
                    window.dispatchEvent(new Event('resize'));
                } else if (action === 'minimize') {
                    const panelId = panel.dataset.panelId;
                    const instance = panelInstances.get(panelId);
                    const cardTitle = instance ? instance.config.title : 'Unknown';
                    
                    if (!CardLogger.validateState(panel, 'minimize')) {
                        console.error('[MINIMIZE ERROR] Cannot minimize in current state');
                        return;
                    }
                    
                    if (panel.classList.contains('minimized')) {
                        panel.classList.remove('minimized');
                        panel.style.height = '';
                        panel.style.width = '';
                        
                        if (instance && instance.originalSize) {
                            if (instance.originalSize.width) {
                                panel.style.width = instance.originalSize.width;
                            }
                            if (instance.originalSize.height) {
                                panel.style.height = instance.originalSize.height;
                            }
                            instance.originalSize = null;
                        }
                        
                        const body = panel.querySelector('.flexi-panel-body');
                        if (body) {
                            body.style.display = '';
                        }
                        
                        instance.isMinimized = false;
                        
                        CardLogger.log('MINIMIZE_RESTORE', cardTitle, {
                            restoredSize: {
                                width: panel.style.width,
                                height: panel.style.height
                            }
                        });
                    } else {
                        const rect = panel.getBoundingClientRect();
                        
                        if (instance) {
                            instance.originalSize = {
                                width: rect.width + 'px',
                                height: rect.height + 'px'
                            };
                        }
                        
                        panel.classList.add('minimized');
                        panel.style.height = '40px';
                        panel.style.width = rect.width + 'px';
                        
                        const body = panel.querySelector('.flexi-panel-body');
                        if (body) {
                            body.style.display = 'none';
                        }
                        
                        if (!panel.classList.contains('floating') && !panel.classList.contains('maximized')) {
                            const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
                            const scrollY = window.pageYOffset || document.documentElement.scrollTop;
                            
                            panel.style.position = 'fixed';
                            panel.style.left = (rect.left + scrollX) + 'px';
                            panel.style.top = (rect.top + scrollY) + 'px';
                            panel.style.zIndex = '1000';
                            panel.classList.add('floating');
                            
                            if (instance) {
                                instance.isFloating = true;
                            }
                        }
                        
                        if (instance) {
                            instance.isMinimized = true;
                        }
                        
                        CardLogger.log('MINIMIZE_ENABLE', cardTitle, {
                            originalSize: instance.originalSize,
                            minimizedHeight: '40px',
                            autoFloated: !panel.classList.contains('floating') && !panel.classList.contains('maximized')
                        });
                    }
                    window.dispatchEvent(new Event('resize'));
                } else if (action === 'maximize') {
                    const panelId = panel.dataset.panelId;
                    const instance = panelInstances.get(panelId);
                    const cardTitle = instance ? instance.config.title : 'Unknown';
                    
                    if (!CardLogger.validateState(panel, 'maximize')) {
                        console.error('[MAXIMIZE ERROR] Cannot maximize in current state');
                        return;
                    }
                    
                    if (panel.classList.contains('maximized')) {
                        panel.classList.remove('maximized');
                        
                        if (instance && instance.originalSize) {
                            if (instance.originalSize.width) {
                                panel.style.width = instance.originalSize.width;
                            }
                            if (instance.originalSize.height) {
                                panel.style.height = instance.originalSize.height;
                            }
                            if (instance.originalPosition) {
                                panel.style.left = instance.originalPosition.left;
                                panel.style.top = instance.originalPosition.top;
                            }
                            instance.originalSize = null;
                            instance.originalPosition = null;
                        } else {
                            panel.style.position = '';
                            panel.style.left = '';
                            panel.style.top = '';
                            panel.style.width = '';
                            panel.style.height = '';
                        }
                        
                        instance.isMaximized = false;
                        
                        CardLogger.log('MAXIMIZE_RESTORE', cardTitle, {
                            restoredSize: instance.originalSize,
                            restoredPosition: instance.originalPosition
                        });
                    } else {
                        const rect = panel.getBoundingClientRect();
                        
                        if (instance) {
                            instance.originalSize = {
                                width: rect.width + 'px',
                                height: rect.height + 'px'
                            };
                            instance.originalPosition = {
                                left: panel.style.left || rect.left + 'px',
                                top: panel.style.top || rect.top + 'px'
                            };
                        }
                        
                        const wasFloating = panel.classList.contains('floating');
                        const wasMinimized = panel.classList.contains('minimized');
                        
                        panel.classList.add('maximized');
                        if (wasFloating) {
                            panel.classList.remove('floating');
                        }
                        if (wasMinimized) {
                            panel.classList.remove('minimized');
                            const body = panel.querySelector('.flexi-panel-body');
                            if (body) {
                                body.style.display = '';
                            }
                        }
                        
                        instance.isMaximized = true;
                        instance.isMinimized = false;
                        if (wasFloating) {
                            instance.isFloating = false;
                        }
                        
                        CardLogger.log('MAXIMIZE_ENABLE', cardTitle, {
                            originalSize: instance.originalSize,
                            originalPosition: instance.originalPosition,
                            wasFloating: wasFloating,
                            wasMinimized: wasMinimized,
                            maximizedSize: {
                                width: '100vw',
                                height: 'calc(100vh - 80px)'
                            }
                        });
                    }
                    window.dispatchEvent(new Event('resize'));
                } else if (action === 'close') {
                    const panelId = panel.dataset.panelId;
                    const instance = panelInstances.get(panelId);
                    
                    if (instance) {
                    closedPanels.set(panelId, {
                        panel: panel,
                        instance: instance,
                        wasFloating: panel.classList.contains('floating'),
                        wasMaximized: panel.classList.contains('maximized'),
                        wasMinimized: panel.classList.contains('minimized'),
                        position: {
                            left: panel.style.left,
                            top: panel.style.top,
                            width: panel.style.width,
                            height: panel.style.height
                        },
                        originalSize: instance.originalSize ? {...instance.originalSize} : null,
                        originalPosition: instance.originalPosition ? {...instance.originalPosition} : null
                    });
                        
                        panel.style.display = 'none';
                        instance.isHidden = true;
                        instance.isClosed = true;
                        
                        console.log('Card closed (can be restored):', instance.config.title, 'ID:', panelId);
                        
                        updateRestoreUI();
                    }
                }
            });

            console.log('FlexiPanel system initialized with', panelInstances.size, 'panels');
            console.log('Panel headers found:', document.querySelectorAll('.flexi-panel-header').length);
            console.log('Panels found:', document.querySelectorAll('.flexi-panel').length);
            
            verifyButtonsVisible();
            logAllCardStates();
            createRestoreUI();
        }
        
        function verifyButtonsVisible() {
            console.log('=== VERIFYING BUTTONS ===');
            const panels = document.querySelectorAll('.flexi-panel');
            panels.forEach((panel, index) => {
                const header = panel.querySelector('.flexi-panel-header');
                const controls = panel.querySelector('.flexi-panel-controls');
                const buttons = panel.querySelectorAll('.flexi-panel-btn');
                
                const instance = panelInstances.get(panel.dataset.panelId);
                const cardTitle = instance ? instance.config.title : 'Unknown';
                
                const minimizeBtn = panel.querySelector('.flexi-panel-btn[data-action="minimize"]');
                const maximizeBtn = panel.querySelector('.flexi-panel-btn[data-action="maximize"]');
                
                console.log(`Card ${index + 1}: ${cardTitle}`, {
                    hasHeader: !!header,
                    hasControls: !!controls,
                    buttonCount: buttons.length,
                    hasMinimize: !!minimizeBtn,
                    hasMaximize: !!maximizeBtn
                });
                
                if (buttons.length > 0) {
                    buttons.forEach(btn => {
                        btn.style.display = 'flex';
                        btn.style.visibility = 'visible';
                        btn.style.opacity = '1';
                        btn.style.pointerEvents = 'auto';
                        btn.style.width = '28px';
                        btn.style.height = '28px';
                    });
                }
                
                if (minimizeBtn) {
                    minimizeBtn.style.display = 'flex';
                    minimizeBtn.style.visibility = 'visible';
                    minimizeBtn.style.opacity = '1';
                    console.log(`  ✓ Minimize button found and made visible for: ${cardTitle}`);
                } else {
                    console.warn(`  ✗ Minimize button MISSING for: ${cardTitle}`);
                }
                
                if (maximizeBtn) {
                    maximizeBtn.style.display = 'flex';
                    maximizeBtn.style.visibility = 'visible';
                    maximizeBtn.style.opacity = '1';
                    console.log(`  ✓ Maximize button found and made visible for: ${cardTitle}`);
                } else {
                    console.warn(`  ✗ Maximize button MISSING for: ${cardTitle}`);
                }
            });
            console.log('=== BUTTON VERIFICATION COMPLETE ===');
        }
        
        function logAllCardStates() {
            console.log('=== CARD STATE SUMMARY ===');
            panelInstances.forEach((instance, panelId) => {
                const panel = instance.panel;
                const state = {
                    card: instance.config.title,
                    panelId: panelId,
                    isFloating: panel.classList.contains('floating'),
                    isMaximized: panel.classList.contains('maximized'),
                    isMinimized: panel.classList.contains('minimized'),
                    isHidden: instance.isHidden || false,
                    isClosed: instance.isClosed || false,
                    position: {
                        left: panel.style.left || 'auto',
                        top: panel.style.top || 'auto'
                    },
                    size: {
                        width: panel.style.width || 'auto',
                        height: panel.style.height || 'auto'
                    },
                    capabilities: {
                        resizable: instance.resizable || false,
                        floatable: instance.floatable || false,
                        independent: instance.independent || false
                    }
                };
                console.log('Card State:', state);
            });
            console.log('=== END CARD STATE SUMMARY ===');
        }
        
        window.logCardStates = logAllCardStates;
        window.CardLogger = CardLogger;
        
        function createRestoreUI() {
            const existing = document.querySelector('.restore-panels-container');
            if (existing) existing.remove();
            
            const restoreContainer = document.createElement('div');
            restoreContainer.className = 'restore-panels-container hidden';
            restoreContainer.innerHTML = '<h3>📋 Closed Windows</h3><div class="restore-panels-list"></div>';
            document.body.appendChild(restoreContainer);
        }
        
        function updateRestoreUI() {
            const restoreContainer = document.querySelector('.restore-panels-container');
            if (!restoreContainer) return;
            
            const listContainer = restoreContainer.querySelector('.restore-panels-list');
            if (!listContainer) return;
            
            listContainer.innerHTML = '';
            
            if (closedPanels.size === 0) {
                restoreContainer.classList.add('hidden');
                return;
            }
            
            restoreContainer.classList.remove('hidden');
            
            closedPanels.forEach((closedData, panelId) => {
                const instance = closedData.instance;
                const btn = document.createElement('button');
                btn.className = 'restore-panel-btn';
                btn.textContent = instance.config.title;
                btn.onclick = function() {
                    restorePanel(panelId);
                };
                listContainer.appendChild(btn);
            });
        }
        
        function restorePanel(panelId) {
            const closedData = closedPanels.get(panelId);
            if (!closedData) return;
            
            const panel = closedData.panel;
            const instance = closedData.instance;
            
            panel.style.display = '';
            instance.isHidden = false;
            instance.isClosed = false;
            
            if (closedData.wasFloating) {
                panel.classList.add('floating');
                if (closedData.position.left) panel.style.left = closedData.position.left;
                if (closedData.position.top) panel.style.top = closedData.position.top;
                if (closedData.position.width) panel.style.width = closedData.position.width;
                if (closedData.position.height) panel.style.height = closedData.position.height;
                panel.style.position = 'fixed';
                panel.style.zIndex = '1000';
            }
            
            if (closedData.wasMaximized) {
                panel.classList.add('maximized');
                instance.isMaximized = true;
            }
            
            if (closedData.wasMinimized) {
                panel.classList.add('minimized');
                panel.style.height = '40px';
                const body = panel.querySelector('.flexi-panel-body');
                if (body) {
                    body.style.display = 'none';
                }
                instance.isMinimized = true;
            }
            
            if (closedData.originalSize && instance) {
                instance.originalSize = closedData.originalSize;
            }
            if (closedData.originalPosition && instance) {
                instance.originalPosition = closedData.originalPosition;
            }
            
            closedPanels.delete(panelId);
            
            updateRestoreUI();
            
            setTimeout(() => {
                initPanelInteractions();
            }, 100);
            
            console.log('Panel restored:', instance.config.title, 'ID:', panelId);
        }

        function initialize() {
            console.log('Initializing flexi-panel system...');
            wrapCardsInPanels();
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(initialize, 100);
            });
        } else {
            setTimeout(initialize, 300);
            setTimeout(initialize, 1000);
        }

        const observer = new MutationObserver(function(mutations) {
            let shouldReinit = false;
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1 && (node.hasAttribute('data-section') || node.querySelector('[data-section]'))) {
                            shouldReinit = true;
                        }
                    });
                }
            });
            if (shouldReinit) {
                setTimeout(wrapCardsInPanels, 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    })();
    </script>
    '''


def inject_panel_interactions():
    """Inject panel interactions JavaScript into the page."""
    ui.add_body_html(get_panel_interactions_js())
