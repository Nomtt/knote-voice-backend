# Knote Voice Engine (Internship Prototype)
Developed at KiotViet Technology Corporation.

### Overview:
This is an experimental backend for the Knote POS system. The goal was to replace the old keyword-based voice feature (which struggled in noisy kitchens) with a natural, conversational engine.

It doesn't just match keywords; it understands intent. You can speak naturally, use mixed languages ("Vinglish"), or change your mind mid-sentence, and the system will output a clean, structured transaction.

### Architecture: Why we rebuilt it
The existing Knote app relies on **client-side processing** (the phone's built-in mic & logic). We moved the "brain" to a **server-side pipeline** to solve three specific problems:

| The Problem (Current App) | The Solution (Our Prototype) |
| :--- | :--- |
| **Fails in Noise:** Relies on the device's native speech recognition, which struggles in loud kitchens or cafes. | **Server-Side Whisper:** We send raw audio to the cloud. OpenAI Whisper cleans up background noise and accents better than any phone processor can. |
| **Rigid Commands:** Users must speak like robots (e.g., *"Command: Add 2 Burger"*). | **Semantic Parsing:** The LLM understands natural intent. You can say *"Gimme two burgers, actually make that three,"* and it just works. |
| **Hardcoded Data:** New menu items require app updates or manual entry. | **Dynamic JSON:** The backend enforces a strict **JSON Contract**. If a user orders a new item with a price, the system "learns" it automatically without code changes. |

🛠️ Tech Stack
Backend: Python (Flask)

AI Pipeline: OpenAI Whisper (Speech-to-Text) + GPT-4o (Semantic Parsing)

Frontend: HTML5, TailwindCSS, Vanilla JS

© KiotViet Corp.
