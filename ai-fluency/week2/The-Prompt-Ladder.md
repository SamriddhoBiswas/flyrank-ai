# W2 — The Prompt Ladder

## What I Tested

I used one real task from my portfolio work: turning the **User Analytics Application** into a concise portfolio case study.

The goal was to see which prompt ingredients actually improved the result instead of adding everything at once.

---

# Run 0 — Weak Baseline

### Prompt

> Write a case study for my User Analytics Application.

### Representative output

> ## User Analytics Application
>
> I developed a powerful user analytics application using modern technologies. The application helps businesses understand user behavior through event tracking, session analysis, and heatmaps. It provides valuable insights into how users interact with a website and helps organizations make data-driven decisions.
>
> The project uses Next.js, TypeScript, MongoDB, and other technologies to provide a scalable and efficient solution.

### What changed

This is the baseline. I gave the AI almost no useful direction.

### What actually improved in the output

Nothing specific to my project came through. It recognized the general category of the application, but the output could describe hundreds of analytics projects.

### What still failed

It was full of generic phrases such as “powerful,” “modern technologies,” and “data-driven decisions.” It did not explain what I actually built or any technical decision I made.

### What I would try next

Add a **clear goal** so the AI knows what the case study is supposed to accomplish.

---

# Run 1 — Layer: Clearer Goal

### Prompt

> Write a case study for my User Analytics Application. The goal is to show a hiring manager what I built, the technical decisions I made, and what the finished application actually demonstrated.

### Representative output

> ## User Analytics Application
>
> I built a full-stack analytics application that tracks user interactions and turns them into session journeys and click heatmaps.
>
> The application uses a client-side tracker to record page views and clicks, stores those events in MongoDB, and presents them through a dashboard. The project demonstrates my ability to connect frontend tracking, backend APIs, database storage, and data visualization into one working system.

### What changed

I explicitly stated the **goal of the case study**: show what I built, why I made decisions, and what the result demonstrated.

### What actually improved in the output

The output became more useful for a portfolio. It stopped describing analytics software in the abstract and started explaining what the project demonstrates about me as a developer.

### What still failed

It still did not understand who the reader was. Some of the explanation remained broad enough to work for a general audience.

### What I would try next

Define the **audience**.

---

# Run 2 — Layer: Defined Audience

### Prompt

> Write a case study for my User Analytics Application. The goal is to show a hiring manager what I built, the technical decisions I made, and what the finished application actually demonstrated. The audience is a software engineering hiring manager who already understands basic web development.

### Representative output

> ## User Analytics Application
>
> I built a full-stack user analytics system that captures page views and click coordinates, persists them by session, and exposes the resulting behavior through a dashboard.
>
> The project connects a browser-side tracking script with Next.js API routes and MongoDB. The dashboard reconstructs individual session journeys and renders click activity as a heatmap. I also changed session ordering to use latest activity rather than event count, making the dashboard more useful for inspecting recent behavior.

### What changed

I added exactly one layer: the **audience**.

### What actually improved in the output

The explanation became more technical without becoming longer. It stopped wasting space explaining why analytics dashboards are useful and focused more on the implementation.

### What still failed

The output was technically better, but the AI still did not have enough **real project context** to distinguish my implementation from a typical analytics tutorial.

### What I would try next

Add the specific context of how the application was actually built and verified.

---

# Run 3 — Layer: Real Context

### Prompt

> Write a case study for my User Analytics Application. The goal is to show a hiring manager what I built, the technical decisions I made, and what the finished application actually demonstrated. The audience is a software engineering hiring manager who already understands basic web development.
>
> Context: I built the application with Next.js 15 App Router, TypeScript, Tailwind CSS, MongoDB Atlas, and Mongoose. The client-side tracker is in `public/tracker.js`. It persists a session ID in localStorage, records `page_view` and `click` events, and stores click x/y coordinates. The backend exposes routes for tracking events, listing sessions, retrieving a session's events, and generating heatmap data. The dashboard has a sessions view and a heatmap view. MongoDB Atlas contained the recorded events and the production build passed successfully.

### Representative output

> ## User Analytics Application
>
> I built a full-stack analytics application with Next.js 15, TypeScript, MongoDB Atlas, and Mongoose. The client-side tracker persists a session ID in localStorage and records page views and click coordinates through a small tracking script.
>
> On the backend, I created API routes for event ingestion, session listing, session-level event retrieval, and heatmap data. The dashboard then turns those events into two useful views: an ordered session journey and a click heatmap.
>
> One implementation decision was to sort sessions by latest activity rather than event count. That makes the dashboard better for finding recently active sessions. I verified the flow by checking that events appeared in MongoDB Atlas and that the production build passed.

### What changed

I added the **real project context**.

### What actually improved in the output

This was the biggest improvement so far. The case became recognizably mine. Details such as `localStorage`, `public/tracker.js`, click coordinates, MongoDB Atlas, and latest-activity sorting could not easily be swapped into a random analytics project without changing the story.

### What still failed

The output was accurate but still read slightly like a technical project summary. It did not yet have a clean structure that could be dropped directly into my portfolio.

### What I would try next

Specify the **output format**.

---

# Run 4 — Layer: Specified Output Format

### Prompt

> Write a case study for my User Analytics Application. The goal is to show a hiring manager what I built, the technical decisions I made, and what the finished application actually demonstrated. The audience is a software engineering hiring manager who already understands basic web development.
>
> Context: I built the application with Next.js 15 App Router, TypeScript, Tailwind CSS, MongoDB Atlas, and Mongoose. The client-side tracker is in `public/tracker.js`. It persists a session ID in localStorage, records `page_view` and `click` events, and stores click x/y coordinates. The backend exposes routes for tracking events, listing sessions, retrieving a session's events, and generating heatmap data. The dashboard has a sessions view and a heatmap view. MongoDB Atlas contained the recorded events and the production build passed successfully.
>
> Format the case study using exactly three sections: **The problem**, **What I did**, and **What came of it**. Keep each section to one short paragraph.

### Representative output

> ## User Analytics Application
>
> **The problem:** A user analytics tool needs to turn raw interactions into something that can actually be inspected. The challenge was to track users by session, preserve their events, and make both individual journeys and click patterns visible.
>
> **What I did:** I built the application with Next.js 15, TypeScript, MongoDB Atlas, and Mongoose. A client-side tracker in `public/tracker.js` persists a session ID and records page views and clicks with coordinates. I built API routes for event ingestion, sessions, individual session events, and heatmap data, then connected them to a dashboard with session and heatmap views. I also sorted sessions by latest activity so recent behavior appeared first.
>
> **What came of it:** The complete flow worked from browser tracking to MongoDB Atlas to the dashboard. I verified that events were stored correctly, sessions could be reconstructed, click data could be visualized, and the production build passed.

### What changed

I added exactly one layer: the **output format**.

### What actually improved in the output

The content became much easier to use. Instead of a technical explanation that would need editing, I now had the exact three-beat structure required for my portfolio assignment.

### What still failed

The structure improved, but the prompt still allowed the model to use phrases that sounded like polished AI portfolio copy. The case was accurate, but it could still be tighter and more like how I naturally explain my work.

### What I would try next

Add **quality criteria** that define what “good” means for my portfolio voice.

---

# Run 5 — Layer: Quality Criteria

### Prompt

> Write a case study for my User Analytics Application. The goal is to show a hiring manager what I built, the technical decisions I made, and what the finished application actually demonstrated. The audience is a software engineering hiring manager who already understands basic web development.
>
> Context: I built the application with Next.js 15 App Router, TypeScript, Tailwind CSS, MongoDB Atlas, and Mongoose. The client-side tracker is in `public/tracker.js`. It persists a session ID in localStorage, records `page_view` and `click` events, and stores click x/y coordinates. The backend exposes routes for tracking events, listing sessions, retrieving a session's events, and generating heatmap data. The dashboard has a sessions view and a heatmap view. MongoDB Atlas contained the recorded events and the production build passed successfully.
>
> Format the case study using exactly three sections: **The problem**, **What I did**, and **What came of it**. Keep each section to one short paragraph.
>
> Quality criteria: Write like a developer explaining their own work, not like marketing copy. Use specific implementation details where they matter. Do not use buzzwords such as “cutting-edge,” “powerful,” “innovative,” “scalable,” “data-driven,” or “results-driven.” Do not invent metrics or business impact. Every claim should be supported by the context above.

### Representative output

> ## User Analytics Application
>
> **The problem:** Raw click events are not very useful on their own. I needed a way to associate events with a session, preserve the user's journey, and turn the stored clicks into something I could actually inspect.
>
> **What I did:** I built the application with Next.js 15, TypeScript, MongoDB Atlas, and Mongoose. The tracker in `public/tracker.js` keeps a session ID in localStorage and records page views and click coordinates. I added API routes for event tracking, session listing, individual session events, and heatmap data. The dashboard shows both the ordered session journey and click heatmaps. I also changed session sorting to use latest activity rather than event count because recent sessions were more useful to inspect.
>
> **What came of it:** The application worked end-to-end. Events were stored in MongoDB Atlas, sessions could be reconstructed from their events, and click coordinates could be displayed as a heatmap. The production build passed successfully.

### What changed

I added only **quality criteria**.

### What actually improved in the output

This was the most useful change after adding context. The wording became much closer to my voice and removed the inflated language from the earlier runs. It also stopped the model from inventing outcomes that were not actually measured.

### What still failed

The result was good enough to use, but I noticed that the prompt had become long. Most of that length was useful context, but a future user should not need to understand my entire project history to reuse the method.

### What I would try next

Clean up the prompt into a reusable version while keeping the layers that actually earned their place.

---

# What the Ladder Taught Me

The improvements were not equal.

**Clear goal:** Made the output more purposeful.

**Audience:** Made the technical depth more appropriate, although the improvement was smaller than the context change.

**Real context:** Made the biggest jump in specificity. This was the point where the case stopped sounding interchangeable.

**Output format:** Made the response directly usable for the assignment.

**Quality criteria:** Removed the remaining generic AI voice and prevented unsupported claims.

The important lesson is that **context did more for the output than simply asking for better writing**. The model could not produce a specific case study until I gave it specific facts to work with.

The audience layer also did not transform the output by itself. It helped, but less than I expected. That is useful to know because I would not automatically add every possible prompt ingredient next time.

---

# Final Reusable Prompt

> Create a portfolio case study from the project information below.
>
> **Goal:** Show a software engineering hiring manager what I built, the important technical decisions I made, and what the finished project demonstrated.
>
> **Audience:** A software engineering hiring manager who already understands basic web development.
>
> **Project context:**  
> [Paste the project's actual problem, stack, implementation details, decisions, verification, and outcome here.]
>
> **Output format:**  
> Use exactly three sections:
> 1. **The problem**
> 2. **What I did**
> 3. **What came of it**
>
> Keep each section concise and specific.
>
> **Quality criteria:**
> - Write like a developer explaining their own work, not like marketing copy.
> - Use concrete implementation details where they help prove what I did.
> - Highlight decisions and the reasoning behind them when the information is available.
> - Do not use buzzwords such as “cutting-edge,” “powerful,” “innovative,” “scalable,” “data-driven,” or “results-driven.”
> - Do not invent metrics, users, business impact, or outcomes.
> - Do not claim anything that is not supported by the project context.
> - Avoid generic statements that could describe another developer's project.
> - Keep my wording direct, technical, practical, and honest.
>
> Before finalizing, check whether every sentence could specifically describe this project. If a sentence could apply to hundreds of unrelated projects, replace it with something concrete from the supplied context.
