import json
import re

# Read the FAQ file
with open("faq.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split FAQs by the --- separator
blocks = text.split("\n---")

faqs = []

for i, block in enumerate(blocks, start=1):
    block = block.strip()

    if not block:
        continue

    lines = block.splitlines()

    if len(lines) < 2:
        continue

    # First line contains number + question
    first_line = lines[0]

    question = re.sub(r"^\d+\.\s*", "", first_line).strip()

    # Everything else is the answer
    answer = "\n".join(lines[1:]).strip()

    faqs.append({
        "id": len(faqs) + 1,
        "question": question,
        "answer": answer
    })

# Save JSON
with open("faq.json", "w", encoding="utf-8") as f:
    json.dump(faqs, f, indent=4, ensure_ascii=False)

print(f"✅ Converted {len(faqs)} FAQs successfully!")