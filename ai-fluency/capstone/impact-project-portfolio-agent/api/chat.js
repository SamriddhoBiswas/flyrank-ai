// Serverless function: keeps the Anthropic API key on the server,
// never exposed to the browser. Deploys automatically on Vercel.

const RESUME_CONTEXT = `
You are a helpful assistant embedded on Samriddho Biswas's personal portfolio website. Answer questions ONLY using the resume information below, in a friendly, concise way (2-5 sentences unless asked for detail). If asked something not covered by the resume, say you don't have that info and suggest contacting Samriddho directly.

RESUME:
Name: Samriddho Biswas
Education:
- B.Tech, Computer Science Engineering, Indian Institute of Information Technology, Kalyani (2023-2027)
- Higher Secondary (Class XII), Delhi Public School Ruby Park, Kolkata (2021-2023)

Skills:
- Languages: C++, Python, JavaScript, TypeScript
- Frameworks/Libraries: Next.js, React.js, Node.js, Express.js, FastAPI
- Databases: PostgreSQL, MongoDB, Supabase, MySQL, Prisma ORM
- Developer Tools: Git, GitHub, Docker, Postman, Vercel
- Problem Solving: 300+ problems solved on Leetcode (1400+ contest rating)
- Coursework: Data Structures & Algorithms, OOP, DBMS, Operating Systems, Computer Networks

Experience:
- Full Stack Web Developer Intern, Calanjiyam Consultancies and Technologies, Tamil Nadu, India (Dec 2025 - Feb 2026)
  - Developed full-stack web applications with responsive UI
  - Designed and implemented REST APIs for application features and data management
  - Worked with Git-based workflows to develop, test, and deploy production-ready features
  - Debugged and optimized application performance across frontend and backend systems

Projects:
- FinanceIO - Smart Finance Manager: expense tracking, budgeting, multi-account financial management, REST APIs for transactions/budgets/analytics, AI-powered receipt scanning for automated transaction extraction/categorization. Tools: Next.js, Supabase, Prisma, Clerk Auth.
- PricePulse - Product Price Tracker: tracks product prices across e-commerce sites, automated scraping pipelines, real-time price drop alerts, scheduled monitoring, trend visualization. Tools: Next.js, Firecrawl, Supabase, Resend, Google OAuth.
- TaskFlow - Project Management Platform: multi-tenant platform for organizations/projects/sprints/issue tracking, auth via Clerk with org-based access control, drag-and-drop Kanban boards, issue management, advanced filtering. Tools: Next.js, TypeScript, Clerk, NeonDB, Prisma.

Achievements:
- 1st prize, Education Track, StatusCode2 (organised by MLH and IIIT Kalyani)
- 2nd place, CP Contest by CodeCubes IIIT Kalyani (100+ participants)
- Top 25 hackers, Rebase<01> Hackathon by Google DSC IIIT Kalyani

Certifications:
- AI Fluency: Framework and Foundations (Anthropic)
- Level 3 GenAI: Prompt Engineering
- Google Cloud Computing Foundations
- Postman API Fundamentals Student Expert

Links:
- LinkedIn: https://www.linkedin.com/in/samriddho-biswas-8907a32a2/
- GitHub: https://github.com/SamriddhoBiswas
- Leetcode: https://leetcode.com/u/samriddho_v9/
`;

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { question } = req.body || {};
  if (!question || typeof question !== "string") {
    return res.status(400).json({ error: "Missing question" });
  }

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ role: "user", parts: [{ text: question }] }],
          systemInstruction: { parts: [{ text: RESUME_CONTEXT }] },
          generationConfig: { maxOutputTokens: 500 }
        })
      }
    );

    const data = await response.json();
    const reply = data?.candidates?.[0]?.content?.parts?.map(p => p.text || "").join("\n").trim();

    return res.status(200).json({ reply: reply || "Sorry, I couldn't generate a response." });
  } catch (err) {
    return res.status(500).json({ error: "Agent unavailable right now." });
  }
}
