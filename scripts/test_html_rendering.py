#!/usr/bin/env python3
"""
Test script to verify HTML rendering fixes for AI suggestions
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the format function
from app.agent_dashboard import format_suggestion_text

def test_html_rendering():
    """Test various HTML rendering scenarios"""
    print("🧪 Testing HTML Rendering Fixes")
    print("="*80)
    
    # Test case 1: Malformed compliance warning
    test1 = """<strong><div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong></strong> Privacy breach and personal advice violations detected!<br><br><strong>Context:</strong> Member Melissa Solis asking about catch-up contributions; positive sentiment but compliance issues flagged.<br><br><strong></div>Suggested Response:</strong> "Catch-up contributions let you contribute more if you didn't use your full $30,000 cap in previous years—your unused amounts from the last 5 years can be carried forward if your balance was under $500,000. This is general information only; for personal advice, I can connect you with a financial adviser."<br><br><strong>Compliance Issues:</strong><br>- Privacy breach detected - review what personal information was shared<br>- Personal advice given - ensure you're providing general information only and include appropriate disclaimers"""
    
    print("\n📝 Test 1: Malformed Compliance Warning")
    print("-" * 80)
    print("Input:")
    print(test1[:200] + "...")
    result1 = format_suggestion_text(test1)
    print("\nOutput:")
    print(result1[:300] + "...")
    print("\n✅ Check: Should have proper <div class=\"compliance-warning\"> structure")
    
    # Test case 2: Immediate Action with malformed HTML
    test2 = """<strong><div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong></strong> <br><br><strong>Context:</strong> Member Tracy Robinson is escalating after agent provided personal investment advice and potentially breached privacy protocols.<br><br><strong></div>Immediate Action:</strong> <br>1. <strong>Stop providing personal advice immediately</strong> - say "I apologize for any confusion. I can provide general information about investment options, but for personal advice you'd need to speak with a financial adviser."<br>2. <strong>Acknowledge the escalation</strong> - "I understand your concern and I'm connecting you with my supervisor right now."<br><br><strong>Compliance Issues Detected:</strong><br>- ❌ Personal advice given (requires licensing)<br>- ❌ Privacy breach indicated<br><br><strong>Next Step:</strong> Transfer to supervisor immediately and document the compliance violations."""
    
    print("\n📝 Test 2: Immediate Action with Malformed HTML")
    print("-" * 80)
    print("Input:")
    print(test2[:200] + "...")
    result2 = format_suggestion_text(test2)
    print("\nOutput:")
    print(result2[:400] + "...")
    print("\n✅ Check: Should have proper <div class=\"immediate-action\"> structure")
    
    # Test case 3: Simple case without HTML
    test3 = """Context Summary: Member Miranda Johnson asking about increasing her death and TPD insurance coverage (current premiums $124.42/month).

Suggested Response: "Yes, you can increase your cover by completing an application form - I can email that to you today. Keep in mind higher cover means higher premiums, but I can provide a quote first so you know the cost before applying."

Compliance: All clear - no issues detected."""
    
    print("\n📝 Test 3: Plain Text (No HTML)")
    print("-" * 80)
    print("Input:")
    print(test3[:200] + "...")
    result3 = format_suggestion_text(test3)
    print("\nOutput:")
    print(result3[:400] + "...")
    print("\n✅ Check: Should wrap sections in proper divs")
    
    # Test case 4: HTML wrapped text
    test4 = """<strong>Context Summary:</strong> Member Miranda Johnson asking about increasing her death and TPD insurance coverage (current premiums $124.42/month).<br><br><strong>Suggested Response:</strong> "Yes, you can increase your cover by completing an application form - I can email that to you today. Keep in mind higher cover means higher premiums, but I can provide a quote first so you know the cost before applying."<br><br><strong>Compliance:</strong> All clear - no issues detected."""
    
    print("\n📝 Test 4: HTML Wrapped Text")
    print("-" * 80)
    print("Input:")
    print(test4[:200] + "...")
    result4 = format_suggestion_text(test4)
    print("\nOutput:")
    print(result4[:400] + "...")
    print("\n✅ Check: Should wrap sections in proper divs")
    
    # Verify results
    print("\n" + "="*80)
    print("📊 VERIFICATION:")
    print("="*80)
    
    checks = []
    
    # Check 1: Compliance warning structure
    if '<div class="compliance-warning">' in result1 and '</div>' in result1:
        if result1.count('<div class="compliance-warning">') == result1.count('</div>') or result1.count('</div>') > result1.count('<div class="compliance-warning">'):
            checks.append("✅ Test 1: Compliance warning properly wrapped")
        else:
            checks.append("❌ Test 1: Compliance warning structure issue")
    else:
        checks.append("❌ Test 1: Compliance warning not found")
    
    # Check 2: Immediate action structure
    if '<div class="immediate-action">' in result2:
        checks.append("✅ Test 2: Immediate action properly wrapped")
    else:
        checks.append("❌ Test 2: Immediate action not wrapped")
    
    # Check 3: Context summary
    if '<div class="context-summary">' in result3 or '<div class="context-summary">' in result4:
        checks.append("✅ Test 3/4: Context summary properly wrapped")
    else:
        checks.append("❌ Test 3/4: Context summary not wrapped")
    
    # Check 4: Suggested response
    if '<div class="suggested-response">' in result3 or '<div class="suggested-response">' in result4:
        checks.append("✅ Test 3/4: Suggested response properly wrapped")
    else:
        checks.append("❌ Test 3/4: Suggested response not wrapped")
    
    # Check 5: No malformed HTML
    if '<strong><div' not in result1 and '<strong><div' not in result2:
        checks.append("✅ No malformed <strong><div structures")
    else:
        checks.append("❌ Still has malformed <strong><div structures")
    
    if '<strong></div>' not in result1 and '<strong></div>' not in result2:
        checks.append("✅ No malformed <strong></div> structures")
    else:
        checks.append("❌ Still has malformed <strong></div> structures")
    
    for check in checks:
        print(check)
    
    print("\n" + "="*80)
    print("💡 If all checks pass, HTML rendering should work correctly!")
    print("="*80)

if __name__ == "__main__":
    test_html_rendering()

