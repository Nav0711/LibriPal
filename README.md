# LibriPal
Chatbot


✅ Core Features (MVP – 100% do these)

Natural Language Book Search

“find books on compiler design by Aho” → returns matching titles with availability.

Hybrid: keyword + semantic embedding search.

Book Reservation & Hold

Reserve available books.

Join waitlist if all copies are borrowed.

Due Date Tracking

“what books are due?” → shows current loans + due dates.

Renewal Requests

“renew my operating systems book” → extends due date if allowed by policy.

Policy-aware (max renewals, active holds block).

Reminders & Notifications

Automatic due-date reminders (3 days before, 1 day before, overdue).

Supports Telegram DM + Email (maybe .ICS calendar).

Customizable quiet hours (e.g., no 10pm pings).

Library Info & Help

“when is the library open?”

“what’s the fine policy?”

“help” → shows supported commands.

🚀 Advanced Features (adds AI “wow” factor)

Summarize a Book

“summarize Tanenbaum’s distributed systems” → AI-generated short summary.

Personalized Recommendations

Suggest similar books based on past loans.

“I liked Clean Code” → “You might also like Refactoring by Fowler”.

Smart Reminders (AI Scoring)

If a book has high demand (many holds, few copies), bot nudges earlier.

If user often returns late, add stronger early reminders.

Ask about a Topic (Q&A)

“what books explain blockchain basics?” → chatbot finds + recommends relevant ones.

Uses embeddings + summaries (mini-RAG system).

Fine Check

“do I have any fines?” → show amount + payment link (mock for demo).

Multi-channel Support

Works on Telegram & a small web widget (React).

Future: WhatsApp/Slack.
