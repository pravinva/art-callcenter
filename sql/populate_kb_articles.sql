-- Populate Knowledge Base with ART (Australian Retirement Trust) Articles
-- Run this script to add comprehensive KB articles for call center agents

USE CATALOG member_analytics;
USE SCHEMA knowledge_base;

-- Clear existing articles and insert new meaningful content
DELETE FROM member_analytics.knowledge_base.kb_articles;

-- Insert comprehensive KB articles with detailed, useful content
INSERT INTO member_analytics.knowledge_base.kb_articles VALUES
-- Contribution Limits
('KB-001', 'Contribution Caps and Limits 2024-25', 
'CONCESSIONAL CONTRIBUTIONS: The annual cap is $30,000 for 2024-25 financial year. This includes employer contributions (SG and salary sacrifice), personal deductible contributions, and any other before-tax contributions. Members aged 75+ cannot make concessional contributions. Members aged 67-74 must meet the work test (40 hours in 30 consecutive days) to make contributions. Excess concessional contributions are taxed at the member''s marginal rate plus an excess contributions charge. 

NON-CONCESSIONAL CONTRIBUTIONS: The annual cap is $120,000 for 2024-25. These are after-tax contributions and are not taxed when contributed. Members under 67 can bring forward 3 years of contributions ($360,000 total). Members aged 67-74 must meet the work test. Non-concessional contributions cannot be made if total super balance exceeds $1.9 million.

CATCH-UP CONTRIBUTIONS: Available for members with total super balance under $500,000 on June 30 of previous year. Allows unused concessional cap amounts from previous 5 years to be used. Maximum catch-up amount is $30,000 per year.', 
'contributions', ARRAY('contributions', 'cap', 'limits', 'employer', 'concessional', 'non-concessional', 'catch-up'), 150, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Withdrawals
('KB-002', 'Compassionate Grounds Early Access', 
'Compassionate grounds allow early access to super before preservation age. Eligible circumstances include: (1) Medical treatment for yourself or dependents - must be life-threatening or chronic pain condition, requires medical certificates and quotes; (2) Preventing foreclosure or forced sale of home - must be primary residence, requires bank statements and mortgage documents; (3) Funeral expenses - for dependents only, requires death certificate and funeral invoice; (4) Modifying home for disability - must be for yourself or dependent, requires medical evidence and quotes.

PROCESS: Member must complete application form, provide supporting documentation, and allow 14-21 business days for processing. Maximum withdrawal is amount needed plus reasonable costs. Withdrawals are taxed as normal super withdrawals. Cannot access more than needed for the specific purpose.', 
'withdrawals', ARRAY('withdrawal', 'compassionate', 'medical', 'early access', 'preservation age'), 200, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

('KB-003', 'Financial Hardship Withdrawal', 
'Available for members experiencing severe financial hardship. Eligibility requirements: (1) Must have received eligible government income support payments for 26 continuous weeks (Centrelink payments like JobSeeker, Youth Allowance, etc.); (2) Unable to meet reasonable and immediate family living expenses; (3) Can only access once per 12-month period.

AMOUNT: Maximum $10,000 per 12-month period. Must be minimum $1,000 unless account balance is less. Cannot access more than account balance.

PROCESS: Requires application form, Centrelink income statement showing 26 weeks of payments, bank statements, and evidence of expenses. Processing time is 14-21 business days. Withdrawals are taxed as normal super withdrawals. Members should consider financial counselling before applying.', 
'withdrawals', ARRAY('withdrawal', 'hardship', 'financial difficulty', 'Centrelink'), 180, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Insurance
('KB-004', 'Default Insurance Coverage', 
'ART provides automatic default death and TPD (Total and Permanent Disablement) insurance to eligible members. Coverage starts automatically when account balance reaches $6,000 or member turns 25, whichever comes first.

COVERAGE AMOUNTS: Death cover ranges from $50,000 to $500,000 based on age and account balance. TPD cover is typically 75% of death cover. Coverage reduces as members age. Maximum coverage applies until age 65.

PREMIUMS: Deducted monthly from super balance. Premiums vary by age, gender, and coverage amount. Typical premium is $5-15 per month. Premiums are tax-deductible within super.

OPTIONS: Members can opt out, reduce coverage, or increase coverage (subject to underwriting). Changes can be made online or by phone. Opting out means no insurance protection. Increasing coverage requires health assessment.', 
'insurance', ARRAY('insurance', 'coverage', 'premiums', 'death', 'TPD', 'tpd', 'TPD insurance', 'total permanent disablement', 'default'), 180, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

('KB-005', 'Making an Insurance Claim', 
'DEATH CLAIMS: Beneficiary or estate executor must notify ART within 30 days of death. Required documents: death certificate, claim form, beneficiary nomination form (if applicable), and identification. Processing time is typically 30-60 days. Death benefits are generally tax-free to dependents.

TPD CLAIMS: Member must notify ART and complete claim form. Required documents: medical evidence from treating doctors, employment details, and any relevant reports. ART will arrange independent medical assessment. Processing time is typically 60-90 days. TPD benefits are taxed as normal super withdrawals unless member is over 60.

INCOME PROTECTION: Available as optional cover. Requires medical evidence of inability to work. Waiting periods apply (typically 30-90 days). Benefit is typically 75% of pre-disability income up to maximum monthly benefit.', 
'insurance', ARRAY('insurance', 'claim', 'TPD', 'tpd', 'TPD insurance', 'tpd insurance', 'total permanent disablement', 'death benefit', 'income protection'), 120, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- TPD Insurance Specific Article
('KB-022', 'TPD Insurance - Total and Permanent Disablement', 
'WHAT IS TPD INSURANCE: Total and Permanent Disablement (TPD) insurance provides a lump sum payment if you become totally and permanently disabled and are unlikely to ever work again in any occupation for which you are reasonably suited by education, training, or experience.

COVERAGE DETAILS: ART provides automatic TPD cover as part of default insurance. TPD cover is typically 75% of your death cover amount. Coverage ranges from $37,500 to $375,000 depending on age and account balance. Coverage reduces as you age and stops at age 65.

ELIGIBILITY: TPD insurance starts automatically when your account balance reaches $6,000 or you turn 25, whichever comes first. You must be actively at work (working at least 15 hours per week) when coverage starts. Pre-existing conditions may be excluded.

MAKING A TPD CLAIM: To claim TPD benefits, you must: (1) Notify ART of your disability; (2) Complete TPD claim form; (3) Provide medical evidence from treating doctors showing permanent disability; (4) Provide employment details and any relevant reports; (5) ART will arrange independent medical assessment. Processing typically takes 60-90 days.

TPD DEFINITION: You are considered totally and permanently disabled if: (1) You are unable to work in your own occupation due to injury or illness; AND (2) You are unlikely to ever work again in any occupation for which you are reasonably suited; OR (3) You have lost the use of two limbs, sight in both eyes, or one limb and sight in one eye.

BENEFIT PAYMENT: TPD benefits are paid as a lump sum into your super account. You can then access the funds subject to preservation rules. TPD benefits are taxed as normal super withdrawals unless you are over 60. Tax treatment depends on your age and preservation status.

PREMIUMS: TPD premiums are deducted monthly from your super balance. Premiums vary by age, gender, and coverage amount. Typical premium is $3-10 per month for TPD cover. Premiums are tax-deductible within super.', 
'insurance', ARRAY('TPD', 'tpd', 'TPD insurance', 'tpd insurance', 'total permanent disablement', 'permanent disability', 'disability insurance', 'insurance claim'), 150, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Investment Options
('KB-006', 'Investment Options and Switching', 
'ART offers five investment options: (1) BALANCED (default) - 70% growth assets, 30% defensive, suitable for most members; (2) GROWTH - 85% growth assets, higher risk and potential returns; (3) CONSERVATIVE - 30% growth assets, lower risk, suitable for members near retirement; (4) CASH - 100% cash and fixed interest, lowest risk and returns; (5) ETHICAL - Similar to Balanced but excludes certain industries, for members with ethical preferences.

SWITCHING: Members can switch options online, via mobile app, or by phone. Changes take effect next business day. No switching fees apply. Can switch as often as needed. Switching between options may trigger capital gains tax events.

DEFAULT OPTION: New members are automatically invested in Balanced option unless they choose otherwise. Members should review their investment choice based on age, risk tolerance, and retirement goals.', 
'investments', ARRAY('investment', 'options', 'balanced', 'growth', 'switch', 'conservative', 'cash', 'ethical'), 250, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

('KB-007', 'Understanding Investment Performance', 
'PERFORMANCE REPORTING: Investment performance is reported quarterly in member statements and online. Performance shows returns after fees and taxes. Past performance does not guarantee future returns. Performance varies by investment option and market conditions.

FEES IMPACT: Investment fees reduce returns. ART charges investment fees ranging from 0.30% to 0.60% depending on option. Fees are deducted daily from investment returns. Lower fees generally mean higher net returns over time.

RISK AND RETURN: Higher risk options (Growth) have potential for higher returns but also higher volatility. Lower risk options (Conservative, Cash) have lower potential returns but more stability. Members should choose based on their risk tolerance and time to retirement.', 
'investments', ARRAY('performance', 'returns', 'statements', 'quarterly', 'fees', 'risk'), 140, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Account Management
('KB-008', 'Checking Account Balance and Statements', 
'BALANCE ENQUIRIES: Members can check balance online via member portal, mobile app, or by calling member services. Balance is updated daily and includes all contributions, investment returns, fees, and withdrawals. Balance shown is current as of last business day.

ANNUAL STATEMENTS: Provided annually within 28 days of financial year end (June 30). Statements show: opening and closing balance, contributions received, investment returns, fees charged, insurance premiums, and transactions. Members can request additional statements at any time.

ONLINE ACCESS: Members can register for online access using member number and personal details. Online portal shows real-time balance, transaction history, investment performance, and allows changes to investment options and personal details.', 
'account', ARRAY('balance', 'account', 'enquiry', 'check', 'statements', 'online'), 300, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

('KB-009', 'Updating Personal Details', 
'CHANGES ALLOWED: Members can update address, phone number, email address, and beneficiary nominations. Some changes require identity verification.

ONLINE UPDATES: Available via member portal for address, phone, and email. Changes take effect immediately. No documentation required for these changes.

BENEFICIARY NOMINATIONS: Can be updated online or by completing form. Binding nominations valid for 3 years and require two witnesses. Non-binding nominations can be updated anytime. Default is estate if no nomination made.

IDENTITY VERIFICATION: Required for changes to name, date of birth, or tax file number. Requires certified copies of identification documents. Can be done by mail or in person at ART office.', 
'account', ARRAY('update', 'address', 'phone', 'beneficiary', 'details', 'personal information'), 180, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Fees and Charges
('KB-010', 'Fee Structure and Charges', 
'ADMINISTRATION FEE: $78 per year plus 0.15% of account balance. Maximum administration fee is $900 per year (fee cap). Fee is deducted monthly in equal installments. Lower balances pay proportionally less.

INVESTMENT FEES: Vary by investment option. Balanced option: 0.45% per year. Growth option: 0.50% per year. Conservative option: 0.35% per year. Cash option: 0.30% per year. Ethical option: 0.48% per year. Fees are deducted daily from investment returns.

NO ADDITIONAL FEES: No entry fees, exit fees, contribution fees, or switching fees. All fees are clearly disclosed in Product Disclosure Statement and annual statements. Members can compare fees with other funds using ATO comparison tool.', 
'fees', ARRAY('fees', 'charges', 'administration', 'investment', 'fee cap'), 220, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Retirement
('KB-011', 'Retirement Options and Access', 
'PRESERVATION AGE: Ranges from 55 to 60 depending on date of birth. Members born before July 1, 1960: age 55. Born July 1, 1960 to June 30, 1961: age 56. Born July 1, 1961 to June 30, 1962: age 57. Born July 1, 1962 to June 30, 1963: age 58. Born July 1, 1963 to June 30, 1964: age 59. Born after June 30, 1964: age 60.

ACCESS OPTIONS: Once preservation age reached and retired (or met condition of release): (1) Lump sum withdrawal - take all or part as cash; (2) Account-based pension - regular income payments; (3) Transition to Retirement - access while still working; (4) Leave in accumulation - continue growing super.

TAX IMPLICATIONS: Withdrawals before age 60 are taxed. Withdrawals after age 60 are generally tax-free. Account-based pensions have minimum withdrawal requirements. Members should seek financial advice before making retirement decisions.', 
'retirement', ARRAY('retirement', 'pension', 'preservation age', 'lump sum', 'access', 'age 60'), 190, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

('KB-012', 'Transition to Retirement Pension', 
'TTR allows members to access super while still working, once they reach preservation age. Can work full-time or part-time. Provides regular income payments from super while continuing to work.

WITHDRAWAL REQUIREMENTS: Minimum 4% of account balance per year. Maximum 10% of account balance per year. Payments can be monthly, quarterly, or annually. Amount can be varied within limits each year.

TAX BENEFITS: TTR pensions receive 15% tax offset on income payments. Can salary sacrifice to super while receiving TTR pension. May reduce overall tax liability. After age 60, TTR payments become tax-free.

CONVERSION: TTR pension can be converted to account-based pension once member fully retires. No conversion fees apply. Can also stop TTR and return to accumulation phase.', 
'retirement', ARRAY('TTR', 'transition', 'retirement', 'working', 'pension', 'preservation age'), 160, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Consolidation
('KB-013', 'Consolidating Super Accounts', 
'BENEFITS: Consolidating multiple super accounts into ART reduces fees (only one set of fees instead of multiple), simplifies management (one account to track), and may improve investment returns (consolidated balance may access better investment options).

BEFORE CONSOLIDATING: Check insurance coverage in other funds (may lose insurance if consolidating), check for any exit fees in other funds, compare investment performance, and ensure no lost super in other accounts.

PROCESS: Complete consolidation form or do online via ATO. Provide details of other super funds. ART will arrange transfer. Process takes 2-4 weeks. Member will receive confirmation once transfer complete. Can consolidate multiple accounts at once.', 
'consolidation', ARRAY('consolidate', 'combine', 'transfer', 'multiple accounts', 'ATO'), 170, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Tax
('KB-014', 'Tax on Super Contributions', 
'CONCESSIONAL CONTRIBUTIONS: Taxed at 15% when contributed to super. If member earns over $250,000, additional 15% tax applies (total 30%). Includes employer SG contributions, salary sacrifice, and personal deductible contributions. Tax is deducted before contribution is added to account balance.

NON-CONCESSIONAL CONTRIBUTIONS: Not taxed when contributed (already taxed as income). No tax on these contributions. Includes personal after-tax contributions and spouse contributions.

GOVERNMENT CO-CONTRIBUTION: Available for low-income earners. Government contributes up to $500 if member makes personal after-tax contributions. Maximum co-contribution reduces as income increases. Phases out completely at $58,445 income. Must be under age 71 and meet work test if applicable.', 
'tax', ARRAY('tax', 'contributions', 'concessional', 'co-contribution', 'deductible'), 150, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

('KB-015', 'Tax on Super Withdrawals', 
'BEFORE PRESERVATION AGE: Withdrawals taxed at member''s marginal tax rate minus 30% tax offset. Minimum tax rate is 17% (including Medicare levy). Applies to early access withdrawals and some hardship withdrawals.

AFTER PRESERVATION AGE BUT UNDER 60: First $230,000 (lump sum tax-free threshold) is tax-free if member has met condition of release. Amounts above threshold taxed at 15% (or 0% if low rate cap applies). Account-based pension payments taxed as income with 15% tax offset.

AFTER AGE 60: Withdrawals are generally tax-free. Applies to lump sums and account-based pension payments. No tax on super withdrawals after age 60. This is the most tax-effective time to access super.', 
'tax', ARRAY('tax', 'withdrawal', 'lump sum', 'preservation age', 'age 60', 'tax-free'), 130, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Complaints
('KB-016', 'Complaint and Dispute Resolution', 
'MAKING A COMPLAINT: Members can complain via phone (1800 number), email (complaints@art.com.au), online form, or mail. All complaints are taken seriously and handled confidentially.

ACKNOWLEDGMENT: ART acknowledges complaints within 5 business days. Provides reference number and contact details for complaint handler. Explains process and expected timeframes.

RESOLUTION: ART aims to resolve complaints within 45 days. May request additional information. Will provide written response explaining decision. If complaint upheld, will provide remedy (apology, correction, compensation if appropriate).

AFCA ESCALATION: If unsatisfied with ART''s response, member can escalate to Australian Financial Complaints Authority (AFCA). Must escalate within 2 years of complaint. AFCA is free and independent. AFCA decisions are binding on ART.', 
'complaints', ARRAY('complaint', 'dispute', 'AFCA', 'afca', 'escalation', 'resolution', 'Australian Financial Complaints Authority'), 100, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- AFCA Specific Article
('KB-021', 'AFCA - Australian Financial Complaints Authority', 
'WHAT IS AFCA: Australian Financial Complaints Authority (AFCA) is an independent external dispute resolution scheme for financial services complaints. AFCA is free for consumers and provides binding decisions on financial services providers.

WHEN TO ESCALATE: Members can escalate to AFCA if: (1) Unsatisfied with ART''s response to complaint; (2) ART has not responded within 45 days; (3) Dispute involves financial loss or service issue; (4) Complaint is within AFCA jurisdiction (superannuation, insurance, banking, investments).

TIME LIMITS: Must escalate to AFCA within 2 years of complaint being made to ART. Cannot escalate if complaint is more than 6 years old. AFCA may extend time limits in exceptional circumstances.

AFCA PROCESS: (1) Submit complaint online at afca.org.au or by phone 1800 931 678; (2) AFCA acknowledges complaint and contacts ART; (3) AFCA facilitates resolution (may take 60-90 days); (4) If unresolved, AFCA makes binding decision; (5) ART must comply with AFCA decision.

AFCA POWERS: AFCA can order ART to: pay compensation up to $500,000, correct errors, provide explanations, change processes. AFCA decisions are binding on ART but not on members (members can accept or reject decision). AFCA is independent and impartial.', 
'complaints', ARRAY('AFCA', 'afca', 'Australian Financial Complaints Authority', 'dispute', 'escalation', 'complaint', 'external dispute resolution'), 120, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- APRA Compliance
('KB-017', 'APRA Regulatory Compliance', 
'ART is regulated by Australian Prudential Regulation Authority (APRA). ART must comply with Superannuation Industry (Supervision) Act 1993 and APRA Prudential Standards.

INVESTMENT RETURNS: ART cannot guarantee investment returns. Returns depend on market performance. Past performance does not guarantee future returns. Members bear investment risk.

FINANCIAL ADVICE: ART provides general information only, not personal financial advice. Members should seek licensed financial adviser for personal advice. ART staff cannot provide advice on specific investment decisions or retirement planning.

ANNUAL STATEMENTS: ART must provide annual statements within 28 days of financial year end. Statements must include balance, contributions, returns, fees, and insurance details. Members can request additional statements.', 
'compliance', ARRAY('APRA', 'regulatory', 'compliance', 'standards', 'advice', 'statements'), 90, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Privacy
('KB-018', 'Privacy and Data Protection', 
'ART collects personal information to administer super accounts, process contributions and withdrawals, provide insurance, and comply with legal obligations. Information collected includes name, address, date of birth, tax file number, employment details, and financial information.

USE OF INFORMATION: ART uses information only for super administration purposes. May share with service providers (administrators, insurers, investment managers) under strict confidentiality agreements. Does not sell information to third parties.

ACCESS AND CORRECTION: Members can access their personal information by request. ART will provide copy within 30 days. Members can request corrections if information is inaccurate. No fee for access requests.

PRIVACY POLICY: Full privacy policy available on ART website. Explains collection, use, storage, and disclosure of personal information. Members can opt out of marketing communications.', 
'privacy', ARRAY('privacy', 'data', 'personal information', 'access', 'correction'), 110, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Beneficiaries
('KB-019', 'Beneficiary Nominations', 
'BINDING NOMINATIONS: Valid for 3 years from date of signing. Must be signed by member and two witnesses (over 18, not beneficiaries). Must specify percentage or dollar amount for each beneficiary. If valid, ART must pay according to nomination. Must be renewed every 3 years.

NON-BINDING NOMINATIONS: Can be updated anytime. No witnesses required. ART considers nomination but has discretion. May pay to estate or other dependents if circumstances change. Easier to update than binding nominations.

DEFAULT: If no nomination made, death benefits paid to estate. Estate then distributed according to will or intestacy laws. May take longer and incur legal costs. Members should consider making nomination.

BENEFICIARIES: Can nominate spouse, children, dependents, or legal personal representative. Cannot nominate non-dependents unless they are legal personal representative. Tax implications may vary for different beneficiaries.', 
'beneficiaries', ARRAY('beneficiary', 'nomination', 'death benefit', 'estate', 'binding', 'non-binding'), 140, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),

-- Lost Super
('KB-020', 'Finding and Claiming Lost Super', 
'LOST SUPER: Super accounts become "lost" if fund cannot contact member for 12 months. May occur due to change of address, change of name, or employer not forwarding contributions. Lost super is held by fund or transferred to ATO.

FINDING LOST SUPER: Members can search via ATO online services (myGov account), ART website search tool, or by calling ART or ATO. Search uses name, date of birth, and tax file number. Can find super from multiple funds.

CONSOLIDATION: Once found, members can consolidate lost super into ART account. Complete consolidation form or do online. ART arranges transfer. Process takes 2-4 weeks. No fees for consolidation.

UNCLAIMED SUPER: If fund cannot contact member for 2 years and account balance under $6,000, super may be transferred to ATO. ATO holds unclaimed super. Members can claim from ATO at any time. No time limit on claims.', 
'lost super', ARRAY('lost', 'unclaimed', 'ATO', 'find', 'consolidate', 'myGov'), 120, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- Verify articles were inserted
SELECT COUNT(*) as total_articles, 
       COUNT(DISTINCT category) as categories,
       COLLECT_SET(category) as category_list
FROM member_analytics.knowledge_base.kb_articles;
