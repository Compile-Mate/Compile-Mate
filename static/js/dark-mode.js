/**
 * Enhanced Dark Mode System with Auto-switch and Persistence
 * CompileMate Platform
 */

class DarkModeManager {
    constructor() {
        this.STORAGE_KEY = 'compileMateTheme';
        this.THEME_AUTO = 'auto';
        this.THEME_LIGHT = 'light';
        this.THEME_DARK = 'dark';
        
        this.currentTheme = this.loadTheme();
        this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        this.init();
    }
    
    /**
     * Initialize dark mode system
     */
    init() {
        // Apply initial theme
        this.applyTheme();
        
        // Listen for system theme changes (when in auto mode)
        this.mediaQuery.addEventListener('change', () => {
            if (this.currentTheme === this.THEME_AUTO) {
                this.applyTheme();
            }
        });
        
        // Listen for time-based auto-switching
        if (this.currentTheme === this.THEME_AUTO) {
            this.startAutoSwitching();
        }
        
        // Update UI controls
        this.updateControls();
        
        // Add smooth transitions
        this.addTransitions();
    }
    
    /**
     * Load theme from localStorage
     */
    loadTheme() {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        return saved || this.THEME_AUTO;
    }
    
    /**
     * Save theme to localStorage
     */
    saveTheme(theme) {
        localStorage.setItem(this.STORAGE_KEY, theme);
        this.currentTheme = theme;
    }
    
    /**
     * Get effective theme (resolves 'auto' to actual theme)
     */
    getEffectiveTheme() {
        if (this.currentTheme === this.THEME_AUTO) {
            // Check time-based preference (7 PM - 7 AM = dark)
            const hour = new Date().getHours();
            if (hour >= 19 || hour < 7) {
                return this.THEME_DARK;
            }
            
            // Fall back to system preference
            return this.mediaQuery.matches ? this.THEME_DARK : this.THEME_LIGHT;
        }
        return this.currentTheme;
    }
    
    /**
     * Apply theme to document
     */
    applyTheme() {
        const effectiveTheme = this.getEffectiveTheme();
        
        if (effectiveTheme === this.THEME_DARK) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        
        // Dispatch custom event for theme change
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: effectiveTheme }
        }));
        
        // Update Monaco editor theme if present
        this.updateMonacoTheme(effectiveTheme);
    }
    
    /**
     * Update Monaco editor theme
     */
    updateMonacoTheme(theme) {
        if (typeof monaco !== 'undefined' && window.editor) {
            monaco.editor.setTheme(theme === this.THEME_DARK ? 'vs-dark' : 'vs-light');
        }
    }
    
    /**
     * Set theme manually
     */
    setTheme(theme) {
        this.saveTheme(theme);
        this.applyTheme();
        this.updateControls();
        
        // Restart/stop auto-switching based on new theme
        if (theme === this.THEME_AUTO) {
            this.startAutoSwitching();
        } else {
            this.stopAutoSwitching();
        }
    }
    
    /**
     * Toggle between light and dark
     */
    toggle() {
        const current = this.getEffectiveTheme();
        const newTheme = current === this.THEME_DARK ? this.THEME_LIGHT : this.THEME_DARK;
        this.setTheme(newTheme);
    }
    
    /**
     * Start time-based auto-switching
     */
    startAutoSwitching() {
        // Clear existing interval
        this.stopAutoSwitching();
        
        // Check every minute for time changes
        this.autoSwitchInterval = setInterval(() => {
            if (this.currentTheme === this.THEME_AUTO) {
                this.applyTheme();
            }
        }, 60000); // 1 minute
    }
    
    /**
     * Stop auto-switching
     */
    stopAutoSwitching() {
        if (this.autoSwitchInterval) {
            clearInterval(this.autoSwitchInterval);
            this.autoSwitchInterval = null;
        }
    }
    
    /**
     * Update UI controls
     */
    updateControls() {
        // Update toggle button icon
        const toggleBtn = document.getElementById('dark-mode-toggle');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('svg') || toggleBtn.querySelector('i');
            const effectiveTheme = this.getEffectiveTheme();
            
            if (icon) {
                // Update icon based on theme
                if (effectiveTheme === this.THEME_DARK) {
                    toggleBtn.innerHTML = `
                        <svg class="w-5 h-5 transition-transform hover:rotate-180 duration-500" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
                        </svg>
                    `;
                } else {
                    toggleBtn.innerHTML = `
                        <svg class="w-5 h-5 transition-transform hover:rotate-12 duration-500" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
                        </svg>
                    `;
                }
            }
        }
        
        // Update theme selector (if exists)
        const selector = document.getElementById('theme-selector');
        if (selector) {
            selector.value = this.currentTheme;
        }
    }
    
    /**
     * Add smooth transitions
     */
    addTransitions() {
        // Add transition class to prevent flash
        document.documentElement.style.setProperty('color-scheme', this.getEffectiveTheme());
        
        // Add global transition
        const style = document.createElement('style');
        style.textContent = `
            * {
                transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
            }
            
            *:not(.no-transition) {
                transition-property: background-color, color, border-color;
                transition-duration: 0.3s;
                transition-timing-function: ease;
            }
        `;
        document.head.appendChild(style);
        
        // Remove after initial load
        setTimeout(() => {
            style.remove();
        }, 500);
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.darkModeManager = new DarkModeManager();
    
    // Add toggle button event listener
    const toggleBtn = document.getElementById('dark-mode-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.darkModeManager.toggle();
        });
    }
    
    // Add theme selector event listener
    const selector = document.getElementById('theme-selector');
    if (selector) {
        selector.addEventListener('change', (e) => {
            window.darkModeManager.setTheme(e.target.value);
        });
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkModeManager;
}

