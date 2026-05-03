import csv
import random
import os

# Create ml directory if it doesn't exist
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.csv")

high_priority_keywords = [
    "urgent",
    "crash",
    "critical",
    "blocker",
    "emergency",
    "production",
    "server down",
    "fatal",
    "immediate",
    "hotfix",
    "security breach",
    "data loss",
    "P0",
]
medium_priority_keywords = [
    "feature",
    "update",
    "improve",
    "refactor",
    "bug",
    "issue",
    "enhancement",
    "design",
    "review",
    "test",
    "optimize",
    "slow",
    "P1",
]
low_priority_keywords = [
    "typo",
    "minor",
    "nice to have",
    "documentation",
    "cleanup",
    "formatting",
    "idea",
    "suggestion",
    "tweak",
    "explore",
    "P2",
]


def generate_text(keywords, label):
    # simple templates
    templates = [
        "Need to fix {kw} in the application.",
        "{kw} reported by user.",
        "Please look into {kw}.",
        "Task related to {kw} handling.",
        "Address {kw} as soon as possible.",
        "Investigate {kw} issue.",
        "Implement new {kw}.",
        "Resolve {kw} to unblock.",
        "Update {kw} for better performance.",
        "Check {kw} logs.",
    ]

    data = []
    for _ in range(300):
        kw = random.choice(keywords)
        template = random.choice(templates)
        title = template.format(kw=kw).capitalize()

        # Add some random padding words to description
        desc_padding = [
            "",
            "This has been happening since yesterday.",
            "Please see attached screenshot.",
            "Steps to reproduce are unclear.",
            "It happens on mobile only.",
            "We need this for the next release.",
            "Low priority for now.",
            "High impact on users.",
        ]
        desc = title + " " + random.choice(desc_padding)

        data.append((title, desc, label))
    return data


data_high = generate_text(high_priority_keywords, "high")
data_medium = generate_text(medium_priority_keywords, "medium")
data_low = generate_text(low_priority_keywords, "low")

all_data = data_high + data_medium + data_low
random.shuffle(all_data)

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["title", "description", "priority"])
    for row in all_data:
        writer.writerow(row)

print(f"Generated {len(all_data)} rows in {output_file}")
