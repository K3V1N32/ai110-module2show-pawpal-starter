# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```bash
Welcome to the PawPal+ scheduling system!
Created owner: Kevin
Scheduler created.
Created pet: Tigrex, a cat
Created pet: Bond, a dog
Linked Tigrex to Kevin
Linked Bond to Kevin
Added tasks for Tigrex: ['Feed', 'Feed', 'Feed', 'Vet visit', 'Training']
Added tasks for Bond: ['Feed', 'Feed', 'Feed', 'Walk', 'Walk', 'Vet visit', 'Training']
Starting schedule generation...
Conflict on monday: 1: Vet visit for Tigrex vs 2: Training for Tigrex
Choose which task to keep (1 or 2): 1
Conflict on tuesday: 1: Vet visit for Bond vs 2: Training for Bond
Choose which task to keep (1 or 2): 1
Schedule generation complete.
--Tasks for monday--
Feed for Tigrex at 8:00 for 0.5 hour(s)
Feed for Bond at 8:00 for 0.5 hour(s)
Walk for Bond at 9:00 for 0.5 hour(s)
Vet visit for Tigrex at 10:00 for 1.0 hour(s)
Feed for Tigrex at 15:00 for 0.5 hour(s)
Feed for Bond at 15:00 for 0.5 hour(s)
Walk for Bond at 17:00 for 0.5 hour(s)
Feed for Tigrex at 19:00 for 0.5 hour(s)
Feed for Bond at 19:00 for 0.5 hour(s)
Tigrex happiness: 80%
Bond happiness: 85%
Explanations for scheduling decisions:
- HIGH priority conflict on monday at 10:00: user kept Vet visit over Training.
- HIGH priority conflict on tuesday at 11:00: user kept Vet visit over Training.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
