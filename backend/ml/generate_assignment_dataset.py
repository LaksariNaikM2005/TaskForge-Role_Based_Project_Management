import csv
import random
import os

# Create ml directory if it doesn't exist
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

output_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assignment_dataset.csv"
)

departments = {
    "Engineering": {
        "keywords": [
            "server down",
            "fatal error",
            "API bug",
            "database migration",
            "backend optimization",
            "frontend crash",
            "refactor code",
            "deployment issue",
            "security patch",
            "memory leak",
        ],
        "roles": ["employee", "leader"],
    },
    "Marketing": {
        "keywords": [
            "ad campaign",
            "social media strategy",
            "SEO optimization",
            "blog post",
            "email newsletter",
            "market research",
            "brand awareness",
            "influencer outreach",
            "content calendar",
        ],
        "roles": ["employee", "leader"],
    },
    "HR": {
        "keywords": [
            "interview candidate",
            "onboard new employee",
            "update policies",
            "payroll processing",
            "performance review",
            "benefits administration",
            "employee relations",
            "team building event",
        ],
        "roles": ["employee", "head"],
    },
    "Design": {
        "keywords": [
            "create UI mockups",
            "design new logo",
            "update brand guidelines",
            "user research",
            "wireframing",
            "prototype testing",
            "illustrate landing page",
            "accessibility review",
        ],
        "roles": ["employee", "leader"],
    },
}

templates = [
    "Need to work on {kw} immediately.",
    "User requested {kw}.",
    "Please look into {kw}.",
    "Task related to {kw}.",
    "Address {kw} as soon as possible.",
    "Investigate {kw} requirements.",
    "Implement new {kw}.",
    "Coordinate {kw} with the team.",
    "Update {kw} for Q3.",
    "Review {kw}.",
]

desc_padding = [
    "",
    "This has been pending since yesterday.",
    "Please see attached documents.",
    "Requirements are unclear, needs follow-up.",
    "It has high priority from management.",
    "We need this for the upcoming meeting.",
    "Coordinate with other departments if needed.",
    "Ensure compliance with company standards.",
]


def generate_assignment_data():
    data = []
    # Generate 400 tasks per department
    for dept, info in departments.items():
        for _ in range(400):
            kw = random.choice(info["keywords"])
            template = random.choice(templates)
            title = template.format(kw=kw).capitalize()

            desc = title + " " + random.choice(desc_padding)

            # Bias towards employee role, some leader/head roles
            # Let's say if it contains "review", "strategy", "policies", it's more likely a leader/head task
            is_leadership = any(
                word in kw
                for word in [
                    "strategy",
                    "policies",
                    "review",
                    "event",
                    "administration",
                ]
            )
            if is_leadership:
                role = "head" if dept == "HR" else "leader"
            else:
                role = "employee"

            # Randomness
            if random.random() < 0.1:
                role = random.choice(info["roles"])

            data.append((title, desc, dept, role))
    return data


all_data = generate_assignment_data()
random.shuffle(all_data)

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["title", "description", "department", "role"])
    for row in all_data:
        writer.writerow(row)

print(f"Generated {len(all_data)} rows in {output_file}")
