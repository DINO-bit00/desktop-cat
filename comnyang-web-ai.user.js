// ==UserScript==
// @name         Desktop Cat AI Companion (Gemini, ChatGPT, Claude)
// @namespace    https://github.com/dino-bit00s/desktop-cat
// @version      1.0
// @description  Connects Gemini Web, ChatGPT, and Claude.ai to your Desktop Cat! Cat thinks when generating and celebrates when done.
// @author       Desktop Cat Team
// @match        https://gemini.google.com/*
// @match        https://chatgpt.com/*
// @match        https://chat.openai.com/*
// @match        https://claude.ai/*
// @match        https://www.perplexity.ai/*
// @match        https://chat.deepseek.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// ==/UserScript==

(function() {
    'use strict';

    const PET_API = 'http://127.0.0.1:59999';
    let isGenerating = false;

    function notifyPet(endpoint, toolName) {
        try {
            fetch(`${PET_API}/${endpoint}?tool=${encodeURIComponent(toolName)}`, { mode: 'no-cors' }).catch(() => {});
        } catch (e) {}
    }

    function getToolName() {
        const host = window.location.hostname;
        if (host.includes('gemini')) return 'Gemini Web';
        if (host.includes('openai') || host.includes('chatgpt')) return 'ChatGPT';
        if (host.includes('claude')) return 'Claude';
        if (host.includes('perplexity')) return 'Perplexity';
        if (host.includes('deepseek')) return 'DeepSeek';
        return 'Web AI';
    }

    // Check DOM state changes periodically
    setInterval(() => {
        const tool = getToolName();
        // Look for stop buttons / active generation indicators
        let generatingNow = false;

        // Gemini stop button or streaming indicator
        if (document.querySelector('button[aria-label*="Stop"], button[aria-label*="Hentikan"], mat-progress-bar, .loading-indicator')) {
            generatingNow = true;
        }
        // ChatGPT stop button
        if (document.querySelector('button[data-testid="stop-button"], button[aria-label="Stop generating"]')) {
            generatingNow = true;
        }
        // Claude stop button
        if (document.querySelector('button[aria-label*="Stop Response"], button[aria-label*="Stop"]')) {
            generatingNow = true;
        }

        if (generatingNow && !isGenerating) {
            isGenerating = true;
            notifyPet('thinking', tool);
        } else if (!generatingNow && isGenerating) {
            isGenerating = false;
            notifyPet('celebrate', tool);
        }
    }, 300);

    // Also listen to enter key in textareas
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            const tool = getToolName();
            notifyPet('thinking', tool);
            isGenerating = true;
        }
    }, true);
})();
