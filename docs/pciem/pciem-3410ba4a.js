(function() {
    'use strict';

    const REPO_OWNER = 'cakehonolulu';
    const REPO_NAME = 'pciem';
    const GITHUB_TAGS_URL = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/tags`;

    function getDocVersion() {
        const metaVersion = document.querySelector('meta[name="pciem-doc-version"]');
        if (metaVersion) {
            return metaVersion.getAttribute('content');
        }

        const content = document.body.innerHTML;
        const match = content.match(/<!--\s*DOC_VERSION:\s*v?([\d.]+)\s*-->/);
        if (match) {
            return match[1];
        }

        return null;
    }

    function compareVersions(v1, v2) {
        const parts1 = v1.split('.').map(Number);
        const parts2 = v2.split('.').map(Number);
        
        const maxLength = Math.max(parts1.length, parts2.length);
        
        for (let i = 0; i < maxLength; i++) {
            const num1 = parts1[i] || 0;
            const num2 = parts2[i] || 0;
            
            if (num1 > num2) return 1;
            if (num1 < num2) return -1;
        }
        
        return 0;
    }

    function injectVersionIntoHeading() {
        const docVersion = getDocVersion();
        if (!docVersion) return;

        const headings = document.querySelectorAll('h1');
        for (const heading of headings) {
            if (heading.textContent.trim() === 'API') {
                heading.textContent = `API (v${docVersion})`;
                break;
            }
        }
    }

    function createVersionBanner(docVersion, tagVersion, tagUrl, status) {
        const banner = document.createElement('div');
        banner.id = 'pciem-version-banner';
        
        let statusClass, message;
        
        if (status === 'outdated') {
            statusClass = 'warning';
            message = `
                <strong>Documentation Outdated:</strong>
                <p>This page documents <code>v${docVersion}</code>, but the latest version is <code>v${tagVersion}</code>
                <br> 
                <a href="${tagUrl}" target="_blank">View latest tag →</a></p>
            `;
        } else {
            return;
        }
                
        banner.className = `pciem-version-status ${statusClass}`;
        banner.innerHTML = `
            <div class="banner-content">
                <div class="banner-message">${message}</div>
            </div>
            <button class="banner-close" onclick="this.parentElement.style.display='none'" title="Dismiss">×</button>
        `;

        const content = document.querySelector('main') || document.querySelector('.content') || document.body;
        content.insertBefore(banner, content.firstChild);
    }

    async function checkVersion() {
        const docVersion = getDocVersion();
        
        if (!docVersion) {
            console.log('PCIem: No documentation version found');
            return;
        }

        try {
            const response = await fetch(GITHUB_TAGS_URL);
            
            if (!response.ok) {
                console.error('PCIem: Failed to fetch tags', response.status);
                return;
            }

            const tags = await response.json();
            
            if (tags.length === 0) {
                console.log('PCIem: No tags found yet. Version checking disabled.');
                return;
            }

            const latestTag = tags[0];
            const tagVersion = latestTag.name.replace(/^v/, '');
            const tagUrl = `https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/tag/${latestTag.name}`;

            const comparison = compareVersions(docVersion, tagVersion);
            
            let status;
            if (comparison === 0) {
                status = 'current';
            } else if (comparison < 0) {
                status = 'outdated';
            } else {
                status = 'ahead';
            }

            const showAllStatuses = localStorage.getItem('pciem-show-all-version-status') === 'true';
            
            if (status === 'outdated' || showAllStatuses) {
                createVersionBanner(docVersion, tagVersion, tagUrl, status);
            }
        } catch (error) {
            console.error('PCIem: Error checking version', error);
        }
    }

    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #pciem-version-banner::before {
                content: none !important;
                display: none !important;
            }

            #pciem-version-banner {
                position: relative;
                margin: 1.5em 0;
                padding: 0.75em 1em;
                border-left: 3px solid;
                background-color: var(--quote-bg);
                color: var(--fg);
                border-radius: 4px;
                font-size: 0.9em;
                line-height: 1.6;
            }

            #pciem-version-banner.warning {
                border-left-color: #ff9800;
                background-color: rgba(255, 152, 0, 0.1);
            }

            #pciem-version-banner.info {
                border-left-color: #2196f3;
                background-color: rgba(33, 150, 243, 0.1);
            }

            #pciem-version-banner.success {
                border-left-color: #4caf50;
                background-color: rgba(76, 175, 80, 0.1);
            }

            .banner-content {
                display: flex;
                align-items: flex-start;
                gap: 0.75em;
                padding-right: 2.5em;
            }

            .banner-message {
                flex: 1;
                min-width: 0;
            }

            .banner-message strong {
                display: inline;
                font-weight: 600;
                color: var(--fg);
            }

            .banner-message p {
                margin: 0.25em 0 0 0;
                display: inline;
            }

            .banner-message p:first-of-type {
                margin-top: 0;
            }

            .banner-message code {
                background-color: var(--inline-code-bg);
                color: var(--inline-code-color);
                padding: 0.1em 0.3em;
                border-radius: 3px;
                font-family: var(--mono-font, "Source Code Pro", Consolas, monospace);
                font-size: 0.95em;
            }

            .banner-message a {
                color: var(--links);
                text-decoration: none;
            }

            .banner-message a:hover {
                text-decoration: underline;
            }

            .banner-close {
                position: absolute;
                top: 0.5em;
                right: 0.5em;
                background: none;
                border: none;
                font-size: 1.3em;
                line-height: 1;
                cursor: pointer;
                color: var(--fg);
                opacity: 0.4;
                padding: 0.2em;
                width: 1.5em;
                height: 1.5em;
                transition: opacity 0.2s;
            }

            .banner-close:hover {
                opacity: 0.8;
            }

            .light #pciem-version-banner.warning {
                background-color: #fff4e5;
                border-left-color: #ff9800;
            }

            .light #pciem-version-banner.info {
                background-color: #e3f2fd;
                border-left-color: #2196f3;
            }

            .light #pciem-version-banner.success {
                background-color: #e8f5e9;
                border-left-color: #4caf50;
            }

            .rust #pciem-version-banner.warning,
            .coal #pciem-version-banner.warning,
            .navy #pciem-version-banner.warning,
            .ayu #pciem-version-banner.warning {
                background-color: rgba(255, 152, 0, 0.15);
                border-left-color: #ffa726;
            }

            .rust #pciem-version-banner.info,
            .coal #pciem-version-banner.info,
            .navy #pciem-version-banner.info,
            .ayu #pciem-version-banner.info {
                background-color: rgba(33, 150, 243, 0.15);
                border-left-color: #42a5f5;
            }

            .rust #pciem-version-banner.success,
            .coal #pciem-version-banner.success,
            .navy #pciem-version-banner.success,
            .ayu #pciem-version-banner.success {
                background-color: rgba(76, 175, 80, 0.15);
                border-left-color: #66bb6a;
            }
        `;
        document.head.appendChild(style);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            injectStyles();
            injectVersionIntoHeading();
            checkVersion();
        });
    } else {
        injectStyles();
        injectVersionIntoHeading();
        checkVersion();
    }

})();