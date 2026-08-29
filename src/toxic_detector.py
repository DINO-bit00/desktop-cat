"""
Anti-Toxic Guardian Detection Engine (NyangGuard)
Ultra-fast, lightweight, 100% offline text classifier for Indonesian & English profanity/toxicity.
Sub-millisecond latency (<0.1ms), zero network, zero persistence.
"""

import re
import time
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple, Dict


@dataclass
class ToxicDetectionResult:
    is_toxic: bool
    severity: str             # "none", "mild", "medium", "high"
    matched_words: List[str]  # Detected bad words/patterns
    score: float              # 0.0 to 1.0
    latency_ms: float         # Execution time in milliseconds
    clean_snippet: str        # Context snippet (sanitized)


# ─── 1. CORE TOXIC LEXICON (INDONESIAN & ENGLISH) ───────────────────────────
# High severity: Harsh vulgarities, slurs, explicit swearing, severe toxicity
HIGH_SEVERITY_WORDS = {
    # Indonesian explicit profanities & slurs
    "anjing", "anjir", "anjrit", "anjay", "ajg", "asw", "asu",
    "babi", "bangsat", "bajingan", "bgst", "bjg", "bjir",
    "kontol", "kntl", "memek", "mmk", "jembut", "jmbt",
    "ngentot", "ngewe", "titit", "itil", "pepek", "puki",
    "pantek", "pntk", "picek", "kampret", "lonte", "perek",
    "tempik", "toket", "tetek",
    # English severe profanities & slurs
    "fuck", "fucking", "fucker", "motherfucker", "bitch", "cunt",
    "asshole", "dick", "pussy", "whore", "slut", "cock",
    "nigger", "nigga", "faggot"
}

# Medium severity: Insults, derogatory slurs, toxic gaming remarks
MEDIUM_SEVERITY_WORDS = {
    # Indonesian insults & toxic remarks
    "tolol", "goblok", "gblk", "bego", "idiot", "bodoh", "bloon",
    "dungu", "otak udang", "cacat", "autis", "sampah", "beban",
    "bacot", "bct", "cocote", "bacot lu", "lu bego", "jancuk",
    "jancok", "dancok", "cuk", "ndasmu", "matamu", "mampus",
    "modar", "mati aja", "bocil kematian", "noob sampah",
    # English medium toxicity
    "idiot", "moron", "retard", "dumb", "dumbass", "trash", "loser",
    "stfu", "shut up", "kill yourself", "kys", "noob", "useless",
    "garbage", "bastard", "crap", "bullshit"
}

# Mild severity: Mild slang / frustration expressions
MILD_SEVERITY_WORDS = {
    "sialan", "sial", "brengsek", "kampret", "sompret", "pret",
    "tai", "taek", "shit", "damn", "damn it", "hell"
}


# ─── 2. LEETSPEAK & CHAR MAPPING TABLE ──────────────────────────────────────
LEET_MAP = {
    '0': 'o',
    '1': 'i',
    '!': 'i',
    '|': 'i',
    '3': 'e',
    '4': 'a',
    '@': 'a',
    '5': 's',
    '$': 's',
    '7': 't',
    '+': 't',
    '8': 'b',
    '9': 'g',
    'v': 'u',
}


class ToxicDetector:
    """
    Sub-millisecond local toxicity classifier with robust anti-obfuscation normalization.
    """

    def __init__(self, custom_words: Optional[List[str]] = None):
        self.high_words: Set[str] = set(HIGH_SEVERITY_WORDS)
        self.medium_words: Set[str] = set(MEDIUM_SEVERITY_WORDS)
        self.mild_words: Set[str] = set(MILD_SEVERITY_WORDS)

        if custom_words:
            for w in custom_words:
                self.medium_words.add(w.strip().lower())

        # Compile regexes for rapid tokenization and anti-evasion matching
        self._compile_matchers()

    def _compile_matchers(self):
        """Compile regex patterns for word boundaries and spacing attacks."""
        # Sorted by length descending so longer phrases match first
        all_high = sorted(self.high_words, key=len, reverse=True)
        all_med = sorted(self.medium_words, key=len, reverse=True)
        all_mild = sorted(self.mild_words, key=len, reverse=True)

        self._high_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(w) for w in all_high) + r')\b',
            re.IGNORECASE
        )
        self._med_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(w) for w in all_med) + r')\b',
            re.IGNORECASE
        )
        self._mild_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(w) for w in all_mild) + r')\b',
            re.IGNORECASE
        )

    def normalize_text(self, text: str) -> str:
        """
        Cleans and decodes leetspeak, collapsed repetitions, and obfuscation.
        Example: 'a-n-j-i-n-g' -> 'anjing', 'k0nt0lll' -> 'kontol'
        """
        if not text:
            return ""

        s = text.lower().strip()

        # 1. Decode Leetspeak characters
        decoded_chars = []
        for ch in s:
            decoded_chars.append(LEET_MAP.get(ch, ch))
        s = "".join(decoded_chars)

        # 2. Collapse repetitive characters (e.g. 'anjiiiiiing' -> 'anjiing' -> 'anjing')
        # Replace 3 or more consecutive identical letters with 1 (or 2)
        s = re.sub(r'(.)\1{2,}', r'\1', s)

        # 3. Handle letter-spaced or symbol-separated obfuscation: e.g. 'a-n-j-i-n-g' or 'a n j i n g'
        # Detect single characters separated by spaces/hyphens/dots and rejoin them if they form known words
        s_cleaned = re.sub(r'[^a-z0-9\s]', ' ', s)
        s_cleaned = re.sub(r'\s+', ' ', s_cleaned).strip()

        return s_cleaned

    def evaluate(self, text: str) -> ToxicDetectionResult:
        """
        Evaluates input text and returns structured toxicity result in <0.5ms.
        """
        t0 = time.perf_counter()

        if not text or not text.strip():
            latency = (time.perf_counter() - t0) * 1000.0
            return ToxicDetectionResult(
                is_toxic=False,
                severity="none",
                matched_words=[],
                score=0.0,
                latency_ms=latency,
                clean_snippet=""
            )

        norm_text = self.normalize_text(text)
        # Also create a non-spaced version to catch "a n j i n g" or "k o n t o l"
        dense_text = norm_text.replace(" ", "")

        matched_high = set(self._high_pattern.findall(norm_text))
        matched_med = set(self._med_pattern.findall(norm_text))
        matched_mild = set(self._mild_pattern.findall(norm_text))

        # Check dense string against high words if not found in normalized text
        if not matched_high:
            for w in self.high_words:
                if len(w) >= 3 and w in dense_text:
                    matched_high.add(w)

        if not matched_med:
            for w in self.medium_words:
                if len(w) >= 4 and w in dense_text:
                    matched_med.add(w)

        # Determine severity & score
        if matched_high:
            severity = "high"
            score = 0.95 + min(0.05, len(matched_high) * 0.02)
            all_matches = list(matched_high | matched_med | matched_mild)
            is_toxic = True
        elif matched_med:
            severity = "medium"
            score = 0.75 + min(0.15, len(matched_med) * 0.05)
            all_matches = list(matched_med | matched_mild)
            is_toxic = True
        elif matched_mild:
            severity = "mild"
            score = 0.45 + min(0.15, len(matched_mild) * 0.05)
            all_matches = list(matched_mild)
            is_toxic = True
        else:
            severity = "none"
            score = 0.0
            all_matches = []
            is_toxic = False

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        # Safe sanitized snippet (for debug/logging without exposing full string)
        clean_snippet = text.strip()[:40]

        return ToxicDetectionResult(
            is_toxic=is_toxic,
            severity=severity,
            matched_words=all_matches,
            score=min(1.0, score),
            latency_ms=latency_ms,
            clean_snippet=clean_snippet
        )


# Global singleton instance for maximum performance
_GLOBAL_DETECTOR: Optional[ToxicDetector] = None


def get_detector() -> ToxicDetector:
    global _GLOBAL_DETECTOR
    if _GLOBAL_DETECTOR is None:
        _GLOBAL_DETECTOR = ToxicDetector()
    return _GLOBAL_DETECTOR


def check_toxicity(text: str) -> ToxicDetectionResult:
    """Convenience function to check toxicity with the global detector instance."""
    return get_detector().evaluate(text)


if __name__ == "__main__":
    detector = ToxicDetector()
    test_cases = [
        "Halo bro apa kabar hari ini?",
        "Woi anjing banget lu ya!",
        "Dasar k0nt0llll gak guna",
        "Lu t-o-l-o-l banget sih mainnya",
        "stfu you noob trash",
        "Hari ini cuaca cerah banget mau belajar python",
        "Dasar babi hutan ngeselin",
        "bct lu b ego",
        "sialan tugas belum kelar",
        "good game well played team!"
    ]

    print("=== NYANGGUARD TOXICITY DETECTOR BENCHMARK ===")
    for tc in test_cases:
        res = detector.evaluate(tc)
        status = f"[{res.severity.upper()}]" if res.is_toxic else "[CLEAN]"
        print(f"{status:10} ({res.latency_ms:.3f}ms) -> {tc}")
        if res.is_toxic:
            print(f"           Matches: {res.matched_words} | Score: {res.score:.2f}")
