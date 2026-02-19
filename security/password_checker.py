"""
Password Checker - Analyze password strength and provide recommendations.
"""

import re
import math


# Common weak passwords
COMMON_PASSWORDS = {
    "password", "123456", "password1", "12345678", "qwerty",
    "abc123", "111111", "123456789", "iloveyou", "admin",
    "letmein", "monkey", "1234567", "sunshine", "master",
    "dragon", "welcome", "shadow", "superman", "michael",
    "football", "baseball", "password123", "qwerty123", "admin123",
}


class PasswordChecker:
    def check(self, password: str) -> str:
        """Analyze a password and return a strength report."""
        if not password:
            return "❌ No password provided."

        score = 0
        issues = []
        strengths = []

        # Length check
        length = len(password)
        if length < 8:
            issues.append(f"Too short ({length} chars). Minimum 8 required.")
        elif length >= 8:
            score += 1
            if length >= 12:
                score += 1
                strengths.append(f"Good length ({length} chars)")
            if length >= 16:
                score += 1

        # Character class checks
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?]", password))

        if has_lower:
            score += 1
            strengths.append("Contains lowercase letters")
        else:
            issues.append("Missing lowercase letters (a-z)")

        if has_upper:
            score += 1
            strengths.append("Contains uppercase letters")
        else:
            issues.append("Missing uppercase letters (A-Z)")

        if has_digit:
            score += 1
            strengths.append("Contains digits")
        else:
            issues.append("Missing digits (0-9)")

        if has_special:
            score += 2
            strengths.append("Contains special characters")
        else:
            issues.append("Missing special characters (!@#$...)")

        # Common password check
        if password.lower() in COMMON_PASSWORDS:
            score = 0
            issues.append("⚠ This is a commonly known password!")

        # Repeated characters
        if re.search(r"(.)\1{3,}", password):
            score -= 1
            issues.append("Contains 4+ repeated characters")

        # Sequential patterns
        if re.search(r"(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def)", password.lower()):
            score -= 1
            issues.append("Contains sequential pattern (e.g. 123, abc)")

        # Entropy estimate
        charset = 0
        if has_lower: charset += 26
        if has_upper: charset += 26
        if has_digit: charset += 10
        if has_special: charset += 32
        entropy = length * math.log2(max(charset, 1))

        # Rating
        score = max(0, score)
        if score <= 2:
            rating = "❌ VERY WEAK"
            color_tip = "Use a password manager to generate a strong password."
        elif score <= 4:
            rating = "🟡 WEAK"
            color_tip = "Improve by adding length and special characters."
        elif score <= 6:
            rating = "🟠 MODERATE"
            color_tip = "Consider making it longer or adding special chars."
        elif score <= 8:
            rating = "🟢 STRONG"
            color_tip = "Good password! Consider using a passphrase for memorability."
        else:
            rating = "✅ VERY STRONG"
            color_tip = "Excellent password!"

        lines = [
            "=" * 50,
            "🔐 PASSWORD STRENGTH REPORT",
            "=" * 50,
            f"Rating   : {rating}",
            f"Score    : {score}/10",
            f"Length   : {length} characters",
            f"Entropy  : ~{entropy:.0f} bits",
            "",
        ]

        if strengths:
            lines.append("✅ Strengths:")
            for s in strengths:
                lines.append(f"   • {s}")
            lines.append("")

        if issues:
            lines.append("⚠ Issues:")
            for i in issues:
                lines.append(f"   • {i}")
            lines.append("")

        lines.append(f"💡 Tip: {color_tip}")
        lines.append("\n🔒 Security Note: This check runs locally. Never enter")
        lines.append("   real passwords into untrusted tools.")
        lines.append("=" * 50)
        return "\n".join(lines)
