# W2 — Frame It As Cases: Work That Speaks for Itself

## Voice Card

**Direct, technical, curious, practical, no fluff.**

I want my portfolio to sound like a developer explaining what he actually built: clear about the problem, specific about technical decisions, and honest about what worked and what did not. No inflated claims, corporate filler, or generic AI language.

---

# Case Studies

## User Analytics Application

**The problem:**  
A user analytics system needs to do more than collect clicks. It needs to preserve a user's session, turn raw events into an understandable journey, and make interaction patterns easy to inspect. The assignment required tracking page views and clicks, storing the data, and exposing both session-level activity and click heatmaps.

**What I did:**  
I built the application end-to-end with Next.js, TypeScript, MongoDB, and Mongoose. On the client side, I created a tracking script that generates and persists a session ID in localStorage and records page views and click coordinates. On the backend, I built API routes for receiving events, listing sessions, retrieving a session's ordered events, and serving heatmap data. I then built the dashboard around two views: a session view showing the user's journey and a heatmap view showing where clicks happened. I also changed the session query to sort by latest activity rather than simply by event count, because recent activity is more useful when inspecting sessions.

**What came of it:**  
The full application worked locally from tracking through MongoDB storage to the dashboard. Events appeared in MongoDB Atlas, sessions could be inspected as ordered journeys, and click data could be visualized as a heatmap. The production build also passed successfully. The project gave me a concrete example of connecting a small client-side data collector to a backend API, database, and usable analytics interface rather than treating each layer as a separate exercise.

---

## Reed–Solomon Decomposition Analysis

**The problem:**  
Reed–Solomon codes have a fixed relationship between code length, data symbols, and error-correction capability. We wanted to determine when a valid RS(n, k, t) code can be decomposed into two smaller valid Reed–Solomon codes while preserving the overall structure. The interesting part was not just finding individual valid splits, but identifying a general rule behind them.

**What I did:**  
I worked as part of a four-person team on a brute-force analysis of possible decompositions. We systematically checked candidate splits, verified that the resulting sub-codes remained valid, and analyzed the patterns produced by the experiments. From those patterns, we derived the condition that an RS(n, k, t) code is decomposable exactly when `k >= 2` and `t >= 2`. We then turned the observation into a generalized algorithm and compared its output against exhaustive brute-force results. The final algorithm achieved `O(n · t)` complexity and agreed with the tested brute-force cases.

**What came of it:**  
The project moved from brute-force experimentation to a general theorem and an efficient algorithm. The important part for me was the reasoning process: use computation to find the pattern, question why the pattern holds, then turn it into something that no longer needs exhaustive search. It is one of the clearest examples in my work of DSA-style problem solving being used to reach a general result rather than just solve one input.

---

## FinanceIO — Smart Finance Manager

**The problem:**  
Personal finance applications often separate transaction tracking, budgeting, and financial insights into disconnected features. I wanted to build them as one system while also using AI where it could remove repetitive work instead of adding AI just for the sake of it.

**What I did:**  
I designed and implemented a full-stack finance platform covering expense tracking, budgeting, and multi-account financial management. I built REST APIs for transaction management, budget tracking, and financial analytics, then connected them to the application interface. I also integrated AI-powered receipt scanning so that transaction information could be extracted and categorized instead of being entered manually. The application uses Next.js, Supabase, Prisma, and Clerk for the application, data, ORM, and authentication layers.

**What came of it:**  
The project brought together the kind of work I want to keep doing: application logic, APIs, database-backed features, authentication, and a practical AI feature in one product. More importantly, the AI component has a specific job in the workflow—reducing manual transaction entry—rather than being a generic chatbot added to a normal CRUD application.

---

## TaskFlow — Project Management Platform

**The problem:**  
A project management tool becomes difficult once it has multiple organizations, projects, sprints, issues, permissions, and different ways to filter and organize work. A simple task list is easy to build; keeping those relationships and access rules consistent is the harder part.

**What I did:**  
I built a multi-tenant project management platform with organizations, projects, sprints, and issue tracking. I used Clerk for authentication and organization-based access control, Prisma for database access, and NeonDB for persistence. On the product side, I implemented drag-and-drop Kanban boards, issue management workflows, and advanced filtering so users could work with projects rather than just store tasks in a database.

**What came of it:**  
The project pushed me beyond basic CRUD into multi-tenant application structure and access control. It also gave me experience with the kind of state and relationship-heavy features that show up in real software: an issue belongs to a project, a project belongs to an organization, and what a user can see depends on that organization context.

---

# How the Proof Connects

My portfolio is not meant to present DSA, full-stack development, and GenAI as three unrelated skill lists.

The pattern I want a hiring manager to see is:

**Algorithmic thinking → technical decisions → working software → useful outcome**

The Reed–Solomon project shows the algorithmic side directly: brute-force exploration led to a generalized theorem and an `O(n · t)` algorithm.

The User Analytics Application shows that same problem-solving approach inside a full-stack system: session state, event collection, API design, database queries, and dashboard behavior all had to work together.

FinanceIO shows where I am taking that foundation with GenAI: use AI for a concrete part of a product workflow rather than making the AI itself the entire product.

TaskFlow shows the application side of the same thinking through multi-tenant structure, authorization, relational data, and non-trivial UI workflows.

---

# Bio

I’m Samriddho, a Computer Science student. I build full-stack software and I’m especially interested in SDE and GenAI work. I like understanding how things work underneath the interface—from algorithms and APIs to databases and AI-powered features—and then turning that understanding into working software.

---

# Contact / CTA

I’m looking for SDE and GenAI opportunities where I can build real software, learn quickly, and take ownership of technical problems.

**Want to talk?**  
Email me or connect with me on **LinkedIn**.

---

# Before / After: Generic AI vs. My Voice

### Generic AI version

> “I am a results-driven Computer Science student passionate about leveraging cutting-edge technologies to build innovative, scalable solutions that create meaningful impact.”

### My edited version

> “I build full-stack software and I care about what happens underneath the interface. I like taking a problem, working through the technical details, and turning it into something that actually runs.”

The difference is deliberate. The first sentence could describe almost any computer science student. The second tells the reader how I actually approach building software without claiming more than I can prove.
