# Knote Voice Engine (Internship Prototype)
Developed at KiotViet Technology Corporation.

### Overview:
This project is a backend prototype designed to upgrade the voice architecture of the current Knote POS system. We re-engineered the feature to move from simple keyword detection to semantic intent parsing.
Instead of relying on rigid commands, this engine uses a server-side NLU pipeline to process natural conversation. It handles mixed dialects (Vinglish), background noise, and complex order corrections in real-time, converting them into structured transaction data for the POS.

### Architecture: Why we rebuilt it
The existing Knote app relies on **client-side processing** (the phone's built-in mic & logic). We moved the "brain" to a **server-side pipeline** to solve three specific problems:

<img width="1382" height="538" alt="image" src="https://github.com/user-attachments/assets/e740f3f6-e0f4-443e-84f7-d2c5173fa7a0" />
<img width="1423" height="507" alt="image" src="https://github.com/user-attachments/assets/98b01324-2cd1-4953-86ab-6d0a1a6c115f" />

| The Problem (Current App) | The Solution (Our Prototype) |
| :--- | :--- |
| **Fails in Noise:** Relies on the device's native speech recognition, which struggles in loud kitchens or cafes. | **Server-Side Whisper:** We send raw audio to the cloud. OpenAI Whisper cleans up background noise and accents better than any phone processor can. |
| **Rigid Commands:** Users must speak like robots (e.g., *"Command: Add 2 Burger"*). | **Semantic Parsing:** The LLM understands natural intent. You can say *"Gimme two burgers, actually make that three,"* and it just works. |
| **Hardcoded Data:** New menu items require app updates or manual entry. | **Dynamic JSON:** The backend enforces a strict **JSON Contract**. If a user orders a new item with a price, the system "learns" it automatically without code changes. |

### Tech Stack
- Backend: Python (Flask)
- AI Pipeline: OpenAI Whisper (Speech-to-Text) + GPT-4o (Semantic Parsing)
- Frontend: HTML5, TailwindCSS, Vanilla JS

### Result: 
To ensure reliability and efficiency, we adopted an Acceptance Test-Driven Development (ATDD) approach.

We defined 27 specific acceptance criteria in Gherkin syntax (covering accents, noise, and logic conflicts) before writing the core code. In the final evaluation, the prototype achieved up to 98% success rate against these scenarios, successfully parsing complex "Singlish" orders that the legacy system failed to recognize.

<img width="1095" height="684" alt="image" src="https://github.com/user-attachments/assets/ba4553da-c88e-4255-a168-98bbc7aed67d" />
<img width="1001" height="706" alt="image" src="https://github.com/user-attachments/assets/9395e019-9cf2-40fe-b9d4-b403a5e764df" />


### Future Recommendation
To transition this prototype into a scalable production environment, the following architectural upgrades are recommended:
1. **Domain Adaptation (Dialects)**: While the current prompt engineering handles general "Vinglish," future iterations should leverage fine-tuning on specific regional datasets. This would significantly improve the model's ability to recognize niche local dish names and rapid-fire dialect switching without relying solely on context.
2. **Model Distillation (Cost & Latency)** The current implementation utilizes the general-purpose GPT-4o model. For high-volume deployment, this should be replaced by a fine-tuned, lightweight model (e.g., GPT-4o-mini or a distilled local model). This would drastically reduce inference costs and latency while maintaining high accuracy for the specific domain of food ordering.
3. **Real-Time Token Streaming** Migrating the client-server communication from REST (HTTP) to WebSockets would significantly improve the user experience. This enables token streaming, allowing the UI to display the order text character-by-character as it is processed, masking backend latency and providing immediate visual feedback.

© KiotViet Corp.
