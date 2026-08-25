// ==UserScript==
// @name         Desktop Cat AI Companion (Gemini, ChatGPT, Claude, DeepSeek)
// @namespace    https://github.com/dino-bit00s/desktop-cat
// @version      1.3
// @description  Frame-perfect real-time synchronization between Gemini Web, ChatGPT, Claude.ai, DeepSeek and your Desktop Cat!
// @author       Desktop Cat Team
// @match        https://gemini.google.com/*
// @match        https://chatgpt.com/*
// @match        https://chat.openai.com/*
// @match        https://claude.ai/*
// @match        https://www.perplexity.ai/*
// @match        https://chat.deepseek.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @connect      localhost
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    const PET_API = 'http://127.0.0.1:59999';
    let isCurrentlyThinking = false;
    let pendingStart = false;

    function sendPetSignal(endpoint, toolName) {
        try {
            if (typeof GM_xmlhttpRequest !== 'undefined') {
                GM_xmlhttpRequest({
                    method: 'GET',
                    url: `${PET_API}/${endpoint}?tool=${encodeURIComponent(toolName)}`,
                    onload: function(res) {
                        console.log(`[Desktop Cat] Sent /${endpoint} (${toolName}) -> HTTP ${res.status}`);
                    },
                    onerror: function(err) {
                        console.error(`[Desktop Cat] Failed to send /${endpoint}:`, err);
                    }
                });
            } else {
                fetch(`${PET_API}/${endpoint}?tool=${encodeURIComponent(toolName)}`, {
                    method: 'GET',
                    mode: 'no-cors'
                }).catch(() => {});
            }
        } catch (e) {
            console.error('[Desktop Cat] sendPetSignal exception:', e);
        }
    }

    function detectToolName() {
        const host = window.location.hostname;
        if (host.includes('gemini')) return 'Gemini Web';
        if (host.includes('openai') || host.includes('chatgpt')) return 'ChatGPT';
        if (host.includes('claude')) return 'Claude';
        if (host.includes('deepseek')) return 'DeepSeek';
        if (host.includes('perplexity')) return 'Perplexity';
        return 'Web AI';
    }

    function checkIsAiGenerating() {
        const host = window.location.hostname;

        // 1. Google Gemini (gemini.google.com)
        if (host.includes('gemini')) {
            const stopBtn = document.querySelector('button[aria-label*="Stop"], button[aria-label*="Hentikan"], button[mattooltip*="Stop"], mat-progress-bar, .loading-indicator, .sparkle-container, [aria-label*="Thinking"]');
            const generatingContainer = document.querySelector('.response-streaming, .is-streaming, [data-is-generating="true"]');
            return !!(stopBtn || generatingContainer);
        }

        // 2. ChatGPT (chatgpt.com)
        if (host.includes('chatgpt') || host.includes('openai')) {
            const stopBtn = document.querySelector('button[data-testid="stop-button"], button[aria-label="Stop generating"], button[aria-label="Stop streaming"]');
            return !!stopBtn;
        }

        // 3. Claude (claude.ai)
        if (host.includes('claude')) {
            const stopBtn = document.querySelector('button[aria-label*="Stop Response"], button[aria-label*="Stop generating"], button[aria-label*="Stop"]');
            return !!stopBtn;
        }

        // 4. DeepSeek (chat.deepseek.com)
        if (host.includes('deepseek')) {
            const stopBtn = document.querySelector('.ds-icon-button--stop, button[aria-label*="Stop"], .ds-loading');
            return !!stopBtn;
        }

        // 5. Perplexity (perplexity.ai)
        if (host.includes('perplexity')) {
            const stopBtn = document.querySelector('button[aria-label*="Stop"], .animate-pulse');
            return !!stopBtn;
        }

        return false;
    }

    function evaluateAiState() {
        const isGenerating = checkIsAiGenerating();
        const tool = detectToolName();

        if (isGenerating && !isCurrentlyThinking) {
            isCurrentlyThinking = true;
            pendingStart = false;
            console.log(`[Desktop Cat] AI Started Generating (${tool}) -> Sending /thinking`);
            sendPetSignal('thinking', tool);
        } else if (!isGenerating && isCurrentlyThinking && !pendingStart) {
            isCurrentlyThinking = false;
            console.log(`[Desktop Cat] AI Finished Generating (${tool}) -> Sending /celebrate`);
            sendPetSignal('celebrate', tool);
        }
    }

    // Real-time polling every 150ms
    setInterval(evaluateAiState, 150);

    // Immediate reaction on Enter key or Send button click
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            const tool = detectToolName();
            pendingStart = true;
            isCurrentlyThinking = true;
            sendPetSignal('thinking', tool);
            setTimeout(() => { pendingStart = false; }, 1000);
        }
    }, true);

    document.addEventListener('click', (e) => {
        const target = e.target;
        if (!target) return;
        const btn = target.closest('button[aria-label*="Send"], button[aria-label*="Kirim"], button[data-testid*="send"], button.send-button');
        if (btn) {
            const tool = detectToolName();
            pendingStart = true;
            isCurrentlyThinking = true;
            sendPetSignal('thinking', tool);
            setTimeout(() => { pendingStart = false; }, 1000);
        }
    }, true);

    console.log(`[Desktop Cat v1.3] Active for ${detectToolName()} -> Bridge to ${PET_API}`);
})();
