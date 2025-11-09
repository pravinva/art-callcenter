"""
Mock data generator functions for ART Call Center.
Extracted from 02_mock_data_generator.py for reuse.
"""
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_AU')  # Australian locale

# Comprehensive Call Scenarios (100+ variations)
CALL_SCENARIOS = {
    "contribution_inquiry": [
        {
            "complexity": "simple",
            "dialogue": [
                ("agent", "Good morning, Australian Retirement Trust. {agent_name} speaking, how can I help?"),
                ("customer", "Hi {agent_name}, I wanted to check my contribution cap for this year."),
                ("agent", "Of course! Let me pull up your account. Can I confirm your member number?"),
                ("customer", "Yes, it's {member_id}."),
                ("agent", "Thank you. I can see your current balance is ${balance:,.0f}."),
                ("agent", "The concessional contribution cap for 2024-25 is $30,000 per year."),
                ("customer", "Perfect, I'm planning to put in an extra $5,000 before end of financial year."),
                ("agent", "That sounds good. Just remember, employer contributions count toward that cap too."),
                ("customer", "Oh right, I'll check my payslip. Thanks for clarifying!"),
                ("agent", "You're welcome! Anything else I can help with today?"),
                ("customer", "No, that's all. Thanks!"),
                ("agent", "Great! Thanks for calling ART, have a wonderful day."),
            ]
        },
        {
            "complexity": "complex",
            "dialogue": [
                ("agent", "ART member services, this is {agent_name}."),
                ("customer", "Hi, I'm confused about catch-up contributions. Can you explain?"),
                ("agent", "Absolutely. Catch-up contributions allow you to use unused concessional cap from previous years."),
                ("customer", "How do I know if I'm eligible?"),
                ("agent", "You need a total super balance below $500,000 on June 30th of the previous year."),
                ("agent", "Looking at your account, your balance was ${balance:,.0f} last June, so you are eligible."),
                ("customer", "Great! How much can I put in?"),
                ("agent", "You can carry forward unused amounts from the past 5 years, in addition to this year's $30,000 cap."),
                ("customer", "So potentially more than $30,000 this year?"),
                ("agent", "Correct, if you had unused cap amounts. I'd recommend speaking with a financial adviser for specific advice on how much to contribute."),
                ("customer", "That makes sense. Can you send me some information?"),
                ("agent", "I'll email you our catch-up contributions fact sheet right away."),
                ("customer", "Perfect, thank you so much!"),
            ]
        }
    ],
    
    "withdrawal_compassionate": [
        {
            "complexity": "simple",
            "dialogue": [
                ("agent", "Good afternoon, ART. {agent_name} speaking."),
                ("customer", "Hi, I need to access my super for medical treatment."),
                ("agent", "I understand. Medical expenses can qualify under compassionate grounds."),
                ("agent", "Can you tell me a bit more about the situation?"),
                ("customer", "I need surgery that's not fully covered by Medicare. My specialist says it's medically necessary."),
                ("agent", "I see. For a compassionate release, we'll need a letter from your specialist confirming that."),
                ("customer", "How much can I withdraw?"),
                ("agent", "You can apply for the amount needed for the treatment, including any related expenses."),
                ("customer", "How long does it take?"),
                ("agent", "Once we have all documentation, it typically takes 5 to 10 business days."),
                ("agent", "I'll send you the application form and checklist. Your reference number is CG-{ref_num}."),
                ("customer", "Thank you, that's very helpful."),
                ("agent", "You're welcome. We're here if you have any questions during the process."),
            ]
        },
        {
            "complexity": "complex",
            "dialogue": [
                ("agent", "ART speaking, {agent_name} here. How can I assist?"),
                ("customer", "I want to withdraw my super to prevent my house from being sold."),
                ("agent", "I'm sorry to hear you're in this situation. Mortgage assistance can qualify for compassionate release."),
                ("customer", "What do I need to prove?"),
                ("agent", "You'll need documentation showing you're at least three months in arrears and that your lender is threatening sale."),
                ("customer", "I have those letters. How much can I take out?"),
                ("agent", "You can apply for enough to bring your mortgage up to date, typically 3-4 months of repayments."),
                ("customer", "Can I take out extra for other debts?"),
                ("agent", "Unfortunately, compassionate grounds are limited to preventing the home sale. Other debts wouldn't qualify."),
                ("customer", "What if I need to cover legal fees?"),
                ("agent", "Legal fees directly related to preventing the sale can be included in your application."),
                ("customer", "Okay. What happens to my insurance if I withdraw?"),
                ("agent", "Your insurance remains active, but your balance will be lower. You can check your coverage in member portal."),
                ("customer", "This is a lot to take in. Can someone call me back?"),
                ("agent", "Of course. I'll have our hardship team contact you within 24 hours. They specialize in these situations."),
                ("customer", "Thank you, I appreciate that."),
            ]
        }
    ],
    
    "performance_inquiry": [
        {
            "complexity": "simple",
            "dialogue": [
                ("agent", "Good morning, ART. {agent_name} speaking."),
                ("customer", "Hi, I'm checking how my super is performing."),
                ("agent", "I can help with that. Let me pull up your account."),
                ("agent", "You're in our {risk_profile} option, which returned {return_pct}% last financial year."),
                ("customer", "Is that good compared to other funds?"),
                ("agent", "It's in line with the industry average for similar investment options. We can't compare to specific competitors though."),
                ("customer", "How does the {risk_profile} option work?"),
                ("agent", "It invests across Australian and international shares, property, bonds and cash."),
                ("customer", "Should I consider changing options?"),
                ("agent", "That depends on your personal circumstances and goals. We offer general information, but can't provide personal advice."),
                ("customer", "Fair enough. Who can I talk to about personal advice?"),
                ("agent", "I can refer you to our financial advice team. There may be a fee depending on the complexity."),
                ("customer", "Let me think about it. Thanks for the information."),
            ]
        }
    ],
    
    "insurance_inquiry": [
        {
            "complexity": "simple",
            "dialogue": [
                ("agent", "ART member services, {agent_name} speaking."),
                ("customer", "Hi, I want to check what insurance I have through my super."),
                ("agent", "No problem. Can I get your member number?"),
                ("customer", "{member_id}"),
                ("agent", "Thanks. I can see you have our default death and TPD insurance."),
                ("customer", "What's TPD?"),
                ("agent", "TPD stands for Total and Permanent Disability. It pays out if you can't work due to illness or injury."),
                ("customer", "How much coverage do I have?"),
                ("agent", "Your death cover is ${insurance_death:,.0f} and TPD is ${insurance_tpd:,.0f}."),
                ("customer", "Do I pay for this?"),
                ("agent", "Yes, premiums are deducted from your super balance. It's currently ${insurance_premium:.2f} per month."),
                ("customer", "Can I increase it?"),
                ("agent", "Absolutely. You can apply for additional cover through the member portal or I can send you the forms."),
                ("customer", "I'll check the portal first. Thanks!"),
            ]
        }
    ],
    
    "beneficiary_update": [
        {
            "complexity": "simple",
            "dialogue": [
                ("agent", "Good afternoon, ART. This is {agent_name}."),
                ("customer", "Hi, I just got married and need to update my beneficiaries."),
                ("agent", "Congratulations! I can certainly help with that."),
                ("customer", "I want to add my spouse as the primary beneficiary."),
                ("agent", "Great. There are two types of nominations - binding and non-binding. Which would you prefer?"),
                ("customer", "What's the difference?"),
                ("agent", "A binding nomination legally requires us to pay to your nominated beneficiaries. Non-binding gives the trustee discretion."),
                ("customer", "I'll do binding. How long does it last?"),
                ("agent", "Binding nominations need to be renewed every 3 years, or they lapse to non-binding."),
                ("customer", "Okay, how do I set it up?"),
                ("agent", "I'll email you the binding nomination form. It needs to be witnessed by two adults who aren't beneficiaries."),
                ("customer", "Perfect, thank you!"),
            ]
        }
    ],
    
    "complaint": [
        {
            "complexity": "complex",
            "dialogue": [
                ("agent", "ART member services, {agent_name} speaking. How can I help?"),
                ("customer", "I'm extremely frustrated. I've been trying to get through for 3 days about my insurance claim."),
                ("agent", "I sincerely apologize for the wait. I understand how frustrating that must be."),
                ("agent", "Let me help you right now. Can you tell me about your claim?"),
                ("customer", "I lodged a TPD claim 6 weeks ago and haven't heard anything."),
                ("agent", "I'm sorry about that delay. Let me look up your claim status."),
                ("agent", "I can see your claim is with our assessors. They're currently reviewing the medical evidence."),
                ("customer", "6 weeks seems excessive. When will I get an answer?"),
                ("agent", "TPD claims can take 2-3 months as they require thorough medical assessment. I know that's not what you want to hear."),
                ("customer", "I need this money to pay bills. What am I supposed to do?"),
                ("agent", "I completely understand. Let me escalate this to our claims manager to get you an update within 48 hours."),
                ("agent", "I'm also noting this as a formal complaint so we can review our communication on claims."),
                ("customer", "Thank you. I just want to know what's happening."),
                ("agent", "Absolutely. I'll make sure someone calls you by end of business Friday. Is this the best number?"),
                ("customer", "Yes, this number is fine."),
                ("agent", "I've made detailed notes on your file. I'm really sorry for the frustration this has caused."),
            ]
        }
    ],
    
    "compliance_violations": [
        {
            "type": "guarantee_language",
            "dialogue": [
                ("agent", "Hi, ART speaking. {agent_name} here."),
                ("customer", "I'm worried about the sharemarket volatility. Will my super be okay?"),
                ("agent", "I understand your concern. Markets do go up and down."),
                ("customer", "But will I definitely get my money back?"),
                ("agent", "Well, based on our historical performance, I can guarantee your balanced option will definitely grow over the long term."),  # VIOLATION!
                ("customer", "That's reassuring. Should I stay in balanced?"),
                ("agent", "Absolutely, I promise you'll see great returns in the next 5 years."),  # VIOLATION!
                ("customer", "Okay, thanks for the confidence!"),
            ]
        },
        {
            "type": "personal_advice",
            "dialogue": [
                ("agent", "ART, {agent_name} speaking."),
                ("customer", "I'm 55 and wondering if I should change my investment option."),
                ("agent", "Let me look at your account. You're currently in high growth."),
                ("customer", "Should I move to something more conservative?"),
                ("agent", "Yes, at your age, you should definitely move to balanced. That's the best option for you."),  # VIOLATION!
                ("customer", "Are you sure?"),
                ("agent", "Absolutely, I strongly recommend you switch today. It's what I would do."),  # VIOLATION!
                ("customer", "Okay, can you change it for me?"),
                ("agent", "I'll switch you over right now to the balanced option."),  # VIOLATION!
            ]
        },
        {
            "type": "privacy_breach",
            "dialogue": [
                ("agent", "Good morning, ART."),
                ("customer", "Hi, I'm calling about my wife's super account."),
                ("agent", "Sure, what's her member number?"),
                ("customer", "M234567"),
                ("agent", "Okay, I can see she has ${balance:,.0f} in her account."),  # VIOLATION!
                ("customer", "Has she made any withdrawals recently?"),
                ("agent", "Yes, she withdrew $15,000 last month for medical expenses."),  # VIOLATION!
                ("customer", "Great, thanks for confirming."),
            ]
        }
    ],
    
    "general_inquiry": [
        {
            "complexity": "simple",
            "dialogue": [
                ("agent", "Good morning, ART. {agent_name} speaking."),
                ("customer", "Hi, I just changed jobs. What do I need to do with my super?"),
                ("agent", "Congratulations on the new job! You don't necessarily need to do anything."),
                ("customer", "Really? I thought I had to set something up."),
                ("agent", "Your new employer just needs your member number to make contributions to your existing account."),
                ("customer", "Oh, that's easy. Where do I find my member number?"),
                ("agent", "It's on your member statements, or you can find it by logging into the member portal."),
                ("customer", "Perfect. Anything else I should know?"),
                ("agent", "Just make sure you give your new employer your TFN so contributions are taxed correctly."),
                ("customer", "Will do. Thanks!"),
            ]
        }
    ]
}

def generate_member_pool(num_members=50):
    """Generate realistic ART members"""
    members = []
    
    for i in range(num_members):
        member_id = f"M{random.randint(100000, 999999)}"
        age = random.randint(25, 70)
        
        # Life stage based on age
        if age < 35:
            life_stage = "accumulation"
            balance = random.randint(20000, 150000)
        elif age < 60:
            life_stage = "accumulation"
            balance = random.randint(100000, 500000)
        elif age < 65:
            life_stage = "transition"
            balance = random.randint(250000, 800000)
        else:
            life_stage = "pension"
            balance = random.randint(200000, 1000000)
        
        member = {
            "member_id": member_id,
            "name": fake.name(),
            "age": age,
            "life_stage": life_stage,
            "balance": balance,
            "employment_status": random.choice(["employed", "self-employed", "retired", "unemployed"]),
            "risk_profile": random.choice(["conservative", "balanced", "growth", "high-growth"]),
            "has_insurance": random.choice([True, True, False]),  # 66% have insurance
            "contact_preference": random.choice(["email", "phone", "sms", "portal"])
        }
        members.append(member)
    
    return members

def generate_realistic_call(member_pool):
    """Generate a realistic call with context"""
    
    # Pick random member
    member = random.choice(member_pool)
    
    # Pick scenario based on member profile
    if member["age"] > 60 and random.random() < 0.3:
        scenario_type = "withdrawal_compassionate"
    elif member["balance"] < 50000 and random.random() < 0.2:
        scenario_type = "contribution_inquiry"
    elif not member["has_insurance"] and random.random() < 0.15:
        scenario_type = "insurance_inquiry"
    else:
        scenario_type = random.choice(list(CALL_SCENARIOS.keys()))
    
    # Get scenario variation
    scenarios = CALL_SCENARIOS[scenario_type]
    scenario = random.choice(scenarios)
    
    # Generate call context
    agent_names = ["Jessica", "David", "Karen", "Michael", "Sarah", "James", "Emma", "Daniel"]
    
    context = {
        "member_id": member["member_id"],
        "member_name": member["name"],
        "balance": member["balance"],
        "risk_profile": member["risk_profile"],
        "life_stage": member["life_stage"],
        "agent_name": random.choice(agent_names),
        "return_pct": round(random.uniform(6.5, 9.5), 1),
        "ref_num": f"{random.randint(1000, 9999)}",
        "insurance_death": member["balance"] * random.randint(3, 5),
        "insurance_tpd": member["balance"] * random.randint(2, 4),
        "insurance_premium": round(member["balance"] * 0.0004, 2),
    }
    
    # Format dialogue with context
    formatted_dialogue = []
    for speaker, text in scenario["dialogue"]:
        try:
            formatted_text = text.format(**context)
            formatted_dialogue.append((speaker, formatted_text))
        except KeyError:
            formatted_dialogue.append((speaker, text))
    
    return {
        "scenario_type": scenario_type,
        "complexity": scenario.get("complexity", "simple"),
        "violation_type": scenario.get("type", None),
        "member": member,
        "dialogue": formatted_dialogue,
        "metadata": context
    }

