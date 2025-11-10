#!/usr/bin/env python3
"""
Test script to verify HTML rendering fixes for AI suggestions
Tests: heuristic response, no heuristic, and tab switching scenarios
"""
import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the format function
from app.agent_dashboard import format_suggestion_text

def test_html_rendering():
    """Test various HTML rendering scenarios"""
    print("🧪 Testing HTML Rendering - All Scenarios")
    print("="*80)
    
    # Test case 1: Heuristic response (instant suggestion)
    test1 = """Context Summary: Member Melissa Solis asking about catch-up contributions; positive sentiment but compliance issues flagged.

Suggested Response: "Catch-up contributions let you contribute more if you didn't use your full $30,000 cap in previous years—your unused amounts from the last 5 years can be carried forward if your balance was under $500,000. This is general information only; for personal advice, I can connect you with a financial adviser."

Compliance: Privacy breach detected - review what personal information was shared"""
    
    print("\n📝 Test 1: Heuristic Response (Plain Text)")
    print("-" * 80)
    print("Input (first 150 chars):")
    print(test1[:150] + "...")
    result1 = format_suggestion_text(test1)
    print("\nOutput (first 300 chars):")
    print(result1[:300] + "...")
    print("\n✅ Check: Should have proper <div> wrappers, no raw HTML")
    
    # Test case 2: LLM response with markdown + HTML mix (the problematic case)
    test2 = """**[COMPLIANCE WARNING]** <br><br>**<div class="context-summary"><strong>Context Summary:</strong> ** Member Tracy Robinson is escalating due to agent providing personal investment advice and potential privacy breach - serious</div>compliance violations detected.<br><br>**<div class="suggested-response"><strong>Suggested Response:</strong> ** "Ms. Robinson, I sincerely apologize for any concern this has caused. Let me connect you with my supervisor</div>immediately to address this properly. Please hold for just one moment."<br><br>**Compliance Warnings:**<br>- **PERSONAL ADVICE VIOLATION**: Agent appears to have provided personalized investment advice (not permitted without proper licensing)<br>- **PRIVACY BREACH**: Potential privacy violation detected<br>- **ACTION REQUIRED**: Escalate to supervisor immediately and flag for compliance review<br><br>**Next Steps:** Transfer to supervisor now. Document the compliance issues for immediate review."""
    
    print("\n📝 Test 2: LLM Response (Markdown + HTML Mix)")
    print("-" * 80)
    print("Input (first 200 chars):")
    print(test2[:200] + "...")
    result2 = format_suggestion_text(test2)
    print("\nOutput (first 400 chars):")
    print(result2[:400] + "...")
    print("\n✅ Check: Should have NO raw markdown (**), NO raw HTML tags, proper div wrappers")
    
    # Test case 3: No heuristic (just LLM response)
    test3 = """<div class="context-summary"><strong>Context Summary:</strong> Member Miranda Johnson asking about increasing her death and TPD insurance coverage (current premiums $124.42/month).</div><div class="suggested-response"><strong>Suggested Response:</strong> "Yes, you can increase your cover by completing an application form - I can email that to you today. Keep in mind higher cover means higher premiums, but I can provide a quote first so you know the cost before applying."</div><div class="compliance-info"><strong>Compliance:</strong> All clear - no issues detected.</div>"""
    
    print("\n📝 Test 3: LLM Response (Already HTML)")
    print("-" * 80)
    print("Input (first 200 chars):")
    print(test3[:200] + "...")
    result3 = format_suggestion_text(test3)
    print("\nOutput (first 300 chars):")
    print(result3[:300] + "...")
    print("\n✅ Check: Should preserve HTML structure, no changes needed")
    
    # Test case 4: Tab switching scenario (same text processed multiple times)
    print("\n📝 Test 4: Tab Switching (Same Text Processed Multiple Times)")
    print("-" * 80)
    print("Simulating: User switches tabs, same suggestion text is formatted again")
    result4a = format_suggestion_text(test2)
    result4b = format_suggestion_text(test2)  # Process again (simulates tab switch)
    result4c = format_suggestion_text(test2)  # Process again
    
    print("First processing (first 200 chars):")
    print(result4a[:200] + "...")
    print("\nSecond processing (first 200 chars):")
    print(result4b[:200] + "...")
    print("\nThird processing (first 200 chars):")
    print(result4c[:200] + "...")
    print("\n✅ Check: All three should be identical, no degradation")
    
    # Test case 5: Complex markdown + HTML mix
    test5 = """**Context Summary:** Member asking about super contributions.<br><br>**Suggested Response:** "You can contribute up to $30,000 per year."<br><br>**Compliance:** All clear."""
    
    print("\n📝 Test 5: Simple Markdown + HTML Mix")
    print("-" * 80)
    print("Input:")
    print(test5)
    result5 = format_suggestion_text(test5)
    print("\nOutput:")
    print(result5)
    print("\n✅ Check: Markdown converted to HTML, no raw ** showing")
    
    # Verify results
    print("\n" + "="*80)
    print("📊 VERIFICATION:")
    print("="*80)
    
    checks = []
    
    # Check 1: No raw markdown
    if '**' not in result1 and '**' not in result2 and '**' not in result3 and '**' not in result4a and '**' not in result5:
        checks.append("✅ No raw markdown (**) in any output")
    else:
        checks.append("❌ Raw markdown still present")
        if '**' in result1:
            checks.append("  - Found in Test 1")
        if '**' in result2:
            checks.append("  - Found in Test 2")
        if '**' in result3:
            checks.append("  - Found in Test 3")
        if '**' in result4a:
            checks.append("  - Found in Test 4")
        if '**' in result5:
            checks.append("  - Found in Test 5")
    
    # Check 2: Proper HTML structure
    if '<div class="context-summary">' in result1 or '<div class="context-summary">' in result2:
        checks.append("✅ Context summary properly wrapped")
    else:
        checks.append("❌ Context summary not wrapped")
    
    if '<div class="suggested-response">' in result1 or '<div class="suggested-response">' in result2:
        checks.append("✅ Suggested response properly wrapped")
    else:
        checks.append("❌ Suggested response not wrapped")
    
    # Check 3: No malformed HTML
    if '<strong><div' not in result2 and '<strong></div>' not in result2:
        checks.append("✅ No malformed <strong><div structures")
    else:
        checks.append("❌ Still has malformed <strong><div structures")
    
    if '</div></strong>' not in result2:
        checks.append("✅ No malformed </div></strong> structures")
    else:
        checks.append("❌ Still has malformed </div></strong> structures")
    
    # Check 4: Tab switching consistency
    if result4a == result4b == result4c:
        checks.append("✅ Tab switching: Consistent output (no degradation)")
    else:
        checks.append("❌ Tab switching: Output differs between renders")
    
    # Check 5: Compliance warning handling
    if '[COMPLIANCE WARNING]' in test2:
        if '<div class="compliance-warning">' in result2:
            checks.append("✅ Compliance warning properly wrapped")
        else:
            checks.append("❌ Compliance warning not wrapped")
    
    for check in checks:
        print(check)
    
    # Detailed output for Test 2 (the problematic one)
    print("\n" + "="*80)
    print("🔍 DETAILED ANALYSIS - Test 2 (Problematic Case):")
    print("="*80)
    print("\nFull Output:")
    print(result2)
    print("\n" + "-"*80)
    print("Key Checks:")
    print(f"- Contains '[COMPLIANCE WARNING]': {'[COMPLIANCE WARNING]' in result2}")
    print(f"- Contains '<div class=\"compliance-warning\">': {'<div class=\"compliance-warning\">' in result2}")
    print(f"- Contains '<div class=\"context-summary\">': {'<div class=\"context-summary\">' in result2}")
    print(f"- Contains '<div class=\"suggested-response\">': {'<div class=\"suggested-response\">' in result2}")
    print(f"- Contains raw markdown '**': {'**' in result2}")
    print(f"- Contains malformed '<strong><div': {'<strong><div' in result2}")
    print(f"- Contains malformed '</div></strong>': {'</div></strong>' in result2}")
    
    print("\n" + "="*80)
    print("💡 If all checks pass, HTML rendering should work correctly!")
    print("="*80)

if __name__ == "__main__":
    test_html_rendering()

