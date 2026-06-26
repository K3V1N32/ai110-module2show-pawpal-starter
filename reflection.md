# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  - I have written more detailed plans in PawPal+ Plan.md. For this project I decided that I would tackle a full week schedule (Sun-Sat) and started to brainstorm classes, I initially had an Owner class, Pet class, Task class and a Scheduler class. After deliberating on how the app should function with Claude, I came up with a Storage class as well to keep all this data persistent, as an entire weeks worth of availability, tasks and multiple pets being lost on page refresh would be quite frustrating. The Storage class will manage Scheduler, which has a Owner, and many Tasks, while Owner has many Pets and Pet has many Tasks.
- What classes did you include, and what responsibilities did you assign to each?
  - Storage - This class manages storing and loading the app data with JSON formatting
  - Scheduler - This class holds the Owner, and weekly schedule and has methods for generating the schedule, sorting tasks, and providing pet happiness levels.
  - Owner - This class holds the Pets and owner name, and has methods to add/remove pets.
  - Pet - This class holds the Tasks for each pet, their name and species, and has methods to add/remove tasks.
  - Task - This class holds all of the important information for Tasks, such as the task name, the start time and how long the task lasts, as well as priority and preference, it has methods to set/toggle the attributes, as well as a toggle_complete method.

**b. Design changes**

- Did your design change during implementation?
  - Answer.
- If yes, describe at least one change and why you made it.
  - Answer.

**c. ++ Three Actions a user should be able to perform ++**

 1. Adding a pet
 2. Schedule a weekly Medicine dose for a pet
 3. Review daily tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - Answer.
- How did you decide which constraints mattered most?
  - Answer.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - Answer.
- Why is that tradeoff reasonable for this scenario?
  - Answer.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - Answer.
- What kinds of prompts or questions were most helpful?
  - Answer.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - Answer.
- How did you evaluate or verify what the AI suggested?
  - Answer.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  - Answer.
- Why were these tests important?
  - Answer.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - Answer.
- What edge cases would you test next if you had more time?
  - Answer.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - Answer.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - Answer.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - Answer.


## Reflect & AI Interactions
| Prompt | Result | Notes |
|--------|--------|-------|
| "" | result | notes |
