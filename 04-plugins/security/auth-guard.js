/**
 * OpenClaw Authentication Guard
 * 添加到所有受保护页面的认证检查脚本
 */

(function() {
    'use strict';
    
    // Configuration
    const AUTH_CONFIG = {
        tokenName: 'openclaw_auth_token',
        loginPage: 'login.html',
        checkInterval: 60000, // Check every minute
        protectedPaths: [
            'index.html',
            'dashboard-2.0.html',
            'knowledge-graph.html',
            'cards/'
        ]
    };
    
    // Check if current page is protected
    function isProtectedPage() {
        const currentPath = window.location.pathname;
        const currentHref = window.location.href;
        
        // Always allow login page
        if (currentHref.includes(AUTH_CONFIG.loginPage)) {
            return false;
        }
        
        // Check if path matches protected paths
        return AUTH_CONFIG.protectedPaths.some(path => 
            currentPath.includes(path) || currentHref.includes(path)
        );
    }
    
    // Validate authentication token
    function validateAuth() {
        try {
            const authData = localStorage.getItem(AUTH_CONFIG.tokenName);
            
            if (!authData) {
                return false;
            }
            
            const { token, expiry } = JSON.parse(authData);
            
            // Check if token is expired
            if (Date.now() >= expiry) {
                localStorage.removeItem(AUTH_CONFIG.tokenName);
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('Auth validation error:', error);
            return false;
        }
    }
    
    // Redirect to login page
    function redirectToLogin() {
        const currentUrl = encodeURIComponent(window.location.href);
        window.location.href = `${AUTH_CONFIG.loginPage}?redirect=${currentUrl}`;
    }
    
    // Add logout button to page
    function addLogoutButton() {
        // Don't add to login page
        if (window.location.href.includes(AUTH_CONFIG.loginPage)) {
            return;
        }
        
        const logoutBtn = document.createElement('button');
        logoutBtn.innerHTML = '🚪 退出';
        logoutBtn.className = 'logout-btn';
        logoutBtn.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(239, 68, 68, 0.9);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            transition: all 0.3s;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        `;
        
        logoutBtn.onmouseover = function() {
            this.style.transform = 'scale(1.05)';
            this.style.boxShadow = '0 6px 20px rgba(239, 68, 68, 0.6)';
        };
        
        logoutBtn.onmouseout = function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 4px 15px rgba(239, 68, 68, 0.4)';
        };
        
        logoutBtn.onclick = function() {
            if (confirm('确定要退出登录吗？')) {
                localStorage.removeItem(AUTH_CONFIG.tokenName);
                window.location.href = AUTH_CONFIG.loginPage;
            }
        };
        
        document.body.appendChild(logoutBtn);
    }
    
    // Add auth overlay
    function addAuthOverlay() {
        if (window.location.href.includes(AUTH_CONFIG.loginPage)) {
            return;
        }
        
        const overlay = document.createElement('div');
        overlay.id = 'auth-overlay';
        overlay.style.cssText = `
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 9999;
            align-items: center;
            justify-content: center;
        `;
        
        const message = document.createElement('div');
        message.innerHTML = `
            <div style="text-align: center; color: white;">
                <div style="font-size: 4em; margin-bottom: 20px;">🔐</div>
                <h2 style="font-size: 2em; margin-bottom: 10px;">会话已过期</h2>
                <p style="opacity: 0.8; margin-bottom: 30px;">请重新登录以继续访问</p>
                <button onclick="window.location.href='${AUTH_CONFIG.loginPage}'" 
                    style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                           color: white;
                           border: none;
                           padding: 15px 40px;
                           border-radius: 12px;
                           font-size: 1.1em;
                           cursor: pointer;
                           font-weight: 600;">
                    重新登录
                </button>
            </div>
        `;
        
        overlay.appendChild(message);
        document.body.appendChild(overlay);
    }
    
    // Show session expired
    function showSessionExpired() {
        const overlay = document.getElementById('auth-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }
    
    // Periodic auth check
    function startAuthCheck() {
        setInterval(() => {
            if (!validateAuth() && !window.location.href.includes(AUTH_CONFIG.loginPage)) {
                showSessionExpired();
            }
        }, AUTH_CONFIG.checkInterval);
    }
    
    // Initialize
    function init() {
        // Add logout button
        addLogoutButton();
        
        // Add auth overlay
        addAuthOverlay();
        
        // Check authentication
        if (isProtectedPage() && !validateAuth()) {
            redirectToLogin();
            return;
        }
        
        // Start periodic checks
        startAuthCheck();
        
        console.log('✅ OpenClaw Auth Guard initialized');
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Export for external use
    window.OpenClawAuth = {
        validate: validateAuth,
        logout: function() {
            localStorage.removeItem(AUTH_CONFIG.tokenName);
            window.location.href = AUTH_CONFIG.loginPage;
        },
        getToken: function() {
            const authData = localStorage.getItem(AUTH_CONFIG.tokenName);
            if (authData) {
                return JSON.parse(authData);
            }
            return null;
        }
    };
})();
