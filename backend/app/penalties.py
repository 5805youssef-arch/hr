PENALTY_MAP = {
    "Yellow":        {"label": "Performance Notice", "deduction_hours": 0.0, "deduction_days": 0.0, "freeze_months": 0, "badge": "\U0001F7E1"},
    "Orange":        {"label": "Performance Flag \u2014 4.5 hrs (Half Day) Deduction", "deduction_hours": 4.5, "deduction_days": 0.5, "freeze_months": 0, "badge": "\U0001F7E0"},
    "Red":           {"label": "Performance Alert \u2014 2 Days Deduction", "deduction_hours": 0.0, "deduction_days": 2.0, "freeze_months": 0, "badge": "\U0001F534"},
    "Black":         {"label": "Performance Warning \u2014 4 Days Deduction + 3-Month Freeze", "deduction_hours": 0.0, "deduction_days": 4.0, "freeze_months": 3, "badge": "\u2B1B"},
    "Investigation": {"label": "Suspended \u2014 Transferred to Investigation on Spot", "deduction_hours": 0.0, "deduction_days": 0.0, "freeze_months": 0, "badge": "\U0001F50D"},
}

MATRIX_DATA = {
    "Attendance & Adherence": {
        "Late Arrival":             {"reset": 30,  "escalation": ["Yellow", "Yellow", "Orange", "Red", "Black", "Investigation"], "details": "Arriving late to work."},
        "No-Show":                  {"reset": 90,  "escalation": ["Red", "Red", "Black", "Investigation"], "details": "Missing a scheduled shift without prior notification."},
        "Exceed Breaks":            {"reset": 30,  "escalation": ["Yellow", "Yellow", "Yellow", "Yellow", "Orange", "Red", "Black", "Investigation"], "details": "Taking longer breaks than the permitted duration."},
        "Unscheduled Breaks":       {"reset": 30,  "escalation": ["Yellow", "Red", "Black", "Investigation"], "details": "Taking breaks at unauthorised times."},
        "Out-of-Hours Attendance":  {"reset": 90,  "escalation": ["Yellow", "Red", "Black", "Investigation"], "details": "Remaining in the workplace beyond the end of a shift without approval."},
        "Attendance Manipulation":  {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Falsifying or manipulating attendance records."},
        "Early Leave":              {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Leaving work before end of shift without approval."},
    },
    "Personal Attitude": {
        "Use of Abusive Words":     {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Using offensive or disrespectful language."},
        "Physical Harm":            {"reset": 180, "escalation": ["Investigation"], "details": "Causing physical harm to any person on company premises."},
        "Sleeping on the Job":      {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Sleeping in the workplace during working hours."},
        "Unprofessional Behaviour": {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Conduct that is inappropriate for a professional workplace."},
    },
    "Abusing": {
        "Company Assets":           {"reset": 180, "escalation": ["Investigation"], "details": "Damaging or misusing company property."},
        "Routing Calls / Tickets":  {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Avoiding or incorrectly redirecting assigned calls or tickets."},
        "Releasing Calls / Tickets":{"reset": 180, "escalation": ["Investigation"], "details": "Closing assigned work items without completing them."},
        "Using Colleague Logins":   {"reset": 180, "escalation": ["Investigation"], "details": "Sharing or using another employee's login credentials."},
        "Aux System Abuse":         {"reset": 30,  "escalation": ["Yellow", "Yellow", "Orange", "Red", "Black", "Investigation"], "details": "Misusing auxiliary systems, reports, or tools."},
    },
    "Policy Violations": {
        "Refusing Medical Examination":       {"reset": 180, "escalation": ["Investigation"], "details": "Refusing to undergo a required medical examination."},
        "Unauthorised Visitors":              {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Meeting personal visitors in unauthorised areas."},
        "Smoking in Prohibited Areas":        {"reset": 180, "escalation": ["Black", "Investigation"], "details": "Smoking in areas where it is strictly prohibited."},
        "Alcohol / Drug Influence":           {"reset": 180, "escalation": ["Investigation"], "details": "Being under the influence of alcohol or drugs at work."},
        "Harassment":                         {"reset": 180, "escalation": ["Investigation"], "details": "Engaging in any form of harassment towards colleagues or customers."},
        "Theft":                              {"reset": 180, "escalation": ["Investigation"], "details": "Taking company or personal property without permission."},
        "Social Media Misuse":                {"reset": 180, "escalation": ["Investigation"], "details": "Using social media in a way that damages the company's reputation."},
        "Data Confidentiality Breach":        {"reset": 180, "escalation": ["Investigation"], "details": "Unauthorised data sharing, unethical conduct, or actions causing reputational damage."},
        "Personal Mobile Phone Use":          {"reset": 30,  "escalation": ["Red", "Black", "Investigation"], "details": "Using personal mobile phones for non-work purposes during working hours."},
        "Food & Beverage in Prohibited Areas":{"reset": 30,  "escalation": ["Orange", "Red", "Black", "Investigation"], "details": "Eating or drinking in areas where it is not permitted."},
        "Business Process Failure":           {"reset": 30,  "escalation": ["Orange", "Red", "Black", "Investigation"], "details": "Repeated or severe violation of a critical business process."},
        "End-User Critical Failure":          {"reset": 60,  "escalation": ["Black", "Investigation"], "details": "Severe failure directly impacting end-users (e.g. payouts, customer attitude)."},
        "Cyber Security Breach":              {"reset": 30,  "escalation": ["Red", "Black", "Investigation"], "details": "Downloading unauthorised software, bypassing security, or sharing restricted links."},
    },
}
