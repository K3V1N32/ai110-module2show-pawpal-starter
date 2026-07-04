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
  - Yes
- If yes, describe at least one change and why you made it.
  - One major change during implementation, was that if we scheduled a night time feeding at 8pm, the algorithm would reject the event since it technically exceeded the daily time blocks, so we adjusted the blocks allowed by 2, letting night time tasks that don't exceed 9pm to be scheduled correctly.

**c. ++ Three Actions a user should be able to perform ++**

I added this due to being asked to write these actions, but not having a spot to put them anywhere.

 1. Adding a pet
 2. Schedule a weekly Medicine dose for a pet
 3. Review daily tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - The scheduler considers start time, time blocks(in half hour sections), priority, and preference. Priority is the main decider on whether one task is scheduled over another, with preference being a tie breaker.
- How did you decide which constraints mattered most?
  - I discussed with Claude, I initially thought that preference should matter more in the priority handling, but if I went with that logic something like a MEDIUM priority feeding could be scheduled over a HIGH priority vet visit if the preference was on the feeding, therefore I decided that Priority would matter more than preference, but preference would matter when 2 tasks have the same priority.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - One tradeoff the scheduler makes is that it uses a greedy single-pass over the tasks rather than trying to optimize tasks globablly, the algorithm touches on each task only once and assigns it for the rest of the run, for example, the algorithm could come up with optimal times later in the week to assign a task or ask the user for input on rescheduling tasks by a certain number of blocks. If given more time I'm sure I could come up with an optimizer that properly resolves against constraints and backtracks to search all possible schedule arrangements, taking more time, but generating a more comprehensive schedule.
- Why is that tradeoff reasonable for this scenario?
  - For this scenario, we are making a household pet-care schedule with a relatively low number of tasks per week, not an industrial or enterprise resource-allocation program. The cost of a sub-optimal task placement is low, and the user can easily re-prioritize the tasks and regenerate in a matter of seconds if needed. The greedy O(n log n + n-blocks) algorithm is simple to give reasons, and fast to run and debug, where a more complex solution would require a significant complexity increase for almost no user-percievable benefit.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - I used Claude for brainstorming, debugging, fleshing out methods, and refacoring.
- What kinds of prompts or questions were most helpful?
  - Brainstomring with Claude in a markdown plan file was absolutely the most helpful part of using AI, the ideas and feedback from Claude helped shape the initial skeleton of the project and continued to be the backbone of the project as I worked on it. The steps and planning that happened in the plan.md are what made this app turn out as good as it did.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - Claude tried to push an edit to the time_blocks to force the blocks to stop at 8pm, but I decided not to accept that edit, and suggested that we keep 26 blocks to let an 8pm task be scheduled at 30min or an hour in case of a late feed-time or walk.
- How did you evaluate or verify what the AI suggested?
  - To evaluate what Claude suggested I manually reviewed the code and explanation, thinking through the logic and user-design choices in my head compared to my expected output/logic. The suggestion that we need a cut off at 8pm immediatly set off alarm against my previous expectation of giving the user time to set an 8pm task.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  1. A pet with no tasks
  2. An owner with no pets
  3. A task with improper start_time
- Why were these tests important?
  1. A pet can be initalized with no tasks, and if we generate a schedule at that point for any reason, we need to make sure the entire program doesn't fail on the user.
  2. An owner has no pets at initilization, we need to make sure that this does not break the UI of our app, and that generate_schedule does not crash the app in case the user tries to generate before a pet/tasks are added.
  3. A task with an improper user input for start_time could corrupt an entire generated schedule, so we have to verify that the start_time is properly set.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - ⭐️⭐️⭐️⭐️⭐️ 5/5 stars. I am very confident that my scheduler works correctly based on over 60 assert tests and extensive manual testing and feature verification.
- What edge cases would you test next if you had more time?
  - The edge cases I would test given more time, I would test the input validation more, such as task total_blocks at certain times. There is also the fact that Pet.get_tasks() just returns the entire task list if the filter string is slightly off, such that "daliy" would give the whole list even though the expected output was likely the tasks for a day instead.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - I am really satisfied with the UI that I came up with, the tabs, and dialog popups make the UI standout against a long one-page input screen that could take a long time to scroll through.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - If given more time and another iteration I would try to improve the scheduling logic and algorithm and redesign the UI with more custom layout and colors.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - One important thing I learned about designing systems is the initial plan phase, I've found that the more you flesh out how the systems will work together and what the final UI may look like, it can really help speed up the rest of the process of writing out the actual code and designing the UI/CLI output. The plan streamlined the process of linking different backend systems to their respective frontend inputs/outputs making it easier to debug, and find flaws in the logic during implementation.


## Reflect & AI Interactions
This is a list of every Propmt I used with Claude to help complete this project for complete transparency.

| Prompt |
|--------|
| "Alright Claude, I have this PawPal Project that I am working on, you will be my senior engineer on this project, and help guide me. Please read over the information in PawPal+ Plan.md and for now, under the AI Planning header please put your critique and guidance from a senior perspective. Only generate what I've told you to for now, I will ask for more after we go over the plans." |
| "Could you review my changes and let me know if my plan makes more sense now and put your notes under the heading AI Planning part 2?" |
| "Ok I've addressed the next set of concerns, please let me know how the plan looks now, and if my streamlit UI ideas can work within the limitations of streamlit. Please put notes under the heading AI Planning part 3." |
| "Quick question, would a python generator engine work well for the generate_schedule function?" |
| "Alright I've resolved the current issues, please advise and let me know if we are ready to generate the mermaid UML diagram for our program! Please put notes under the header AI Planning part 4." |
| "Fixes applied, please make a Mermaid.js class diagram and write it to diagrams/uml.mmd." |
| "Now that we have the UML Diagram, please create the class skeletons in pawpal_system.py to match the diagram and plan." |
| "Please write 2 pytest tests in test_pawpal that verify that calling toggle_complete on a Task properly changes the tasks status and verify that adding a Task to a Pet increases it's task count." |
| "I would like to start fleshing out the plan we made and fill in the skeleton in pawpal_system.py. I've added a PATH for our json file, and started a CLI test function to test our classes and make sure everything works as intended before moving on to the streamlit implementation." |
| "We should allow up to one hour after 8pm scheduling to account for an event happening at 8pm such as feeding." |
| "Do you think it would be smart to allow 2 tasks to happen at the same time if they have the same name, such that if 2 different pets have a "feed" task at the same time, say 9am occuring every day, because otherwise a pet owner using this scheduler would be feeding or walking their pets at different times, but in the real world, owners will often combine pet tasks to save time if they are the same task." |
| "Please add 1-line docstrings to the methods in pawpal_system.py" |
| "I'm working on creating the UI for PawPal+ and I need some help. My current implementation is working for the UI side of things, I've started with a debug tool, and some app progression with tabs, but I'm running into an issue with how to properly convert the UI availability information into the correct format for our availability blocks, I could either change the way the input works or I could change the way availability is stored, I will let you decide. I would also like feedback on my implementation so far" |
| "I'm noticing that the schedule is not properly representing if there are 2 feed or walk tasks in the same time slot, for example if 2 pets share a feed time for 8am daily, the schedule will only show one of those pets/tasks in the schedule instead of both as intended." |
| "I've found that the generation does not find conflict if I assign 2 different tasks to the same block when it's 2 different pets and 2 different task names. We should make sure that if one pet has a 12pm feeding, and another pet has a 12pm vet visit, we assign only one of those tasks instead of both." |
| "Input: Pet1 with Feed at 12pm, Pet2 with Feed at 12pm and Vet Visit on wednesday at 12pm, all tasks are High Priority and preference.

Expected output: Only Vet Visit for Pet2, or Feed for both pets should be scheduled on wednesday.

Actual output: The schedule seems to have both Feed(Pet1) and Vet Visit(Pet2) on wednesday

Can you help me fix this bug" |
| "I'd like to handle the Pet and Task adding with st.dialog instead of having a crowded UI in the pet tab. Implement an add pet/add task button that brings up a st.dialog to add in pet/task objects." |
| "I'm running into a small bug after using the render_add_owner_dialog, the UI on the owner tab does not update to reflect the new owner even though I set the selected_scheduler to the new scheduler" |
| "I have loading implemented and seems to be working upon manual testing, I now want to setup saving to file, I would like to save to file any time the user makes a change to make sure their progress is saved throughout the process. I would also like to make sure that when a pet, owner, or task is deleted that we properly update the schedule and any ids or indexes associated with that element to make sure no future bugs pop up from object deletion." |
| "Small UI bug I noticed, when loading from json, it seems the pet happiness does not show correctly on the schedule page, it shows 0% happiness until a new schedule is generated, then upon refresh, it goes back to 0%" |
| "Running streamlit is giving me this error in the terminal:

2026-07-02 15:00:09.389 The widget with key "owner_selectbox" was created with a default value but also had its value set via the Session State API." |
| "Come up with a full suite of pytest tests to make sure the backend works as intended and use tests/test_pawpal.py for the suite " |
| "I would like to run the pytest file myself, but I am getting a "ImportError: attempted relative import with no known parent package" when importing pawpal_system, how do I run the pytest myself?" |
| "Based on my final implementation, what updates should I make to my initial UML diagram to accurately show how my classes interact? Apply the changes to diagrams/uml.mmd " |
