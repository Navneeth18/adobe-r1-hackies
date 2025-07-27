# Adobe "Connecting the Dots" Hackathon - Round 1 Submission  
### A Message from Team "Hackies"

Welcome, esteemed judges, to our submission for the Adobe "Connecting the Dots" Hackathon.  
We are **Team Hackies**, a group of passionate builders who believe that the future of knowledge isn't just about accessing information—it's about interacting with it. For us, a document is not a static endpoint; it's a dynamic gateway to understanding.

This competition was more than just a challenge; it was an invitation to reimagine how we connect with the written word. We were inspired by the mission to transform PDFs from simple pages into intelligent, responsive companions. With every line of code, we aimed to build not just a functional solution, but a glimpse into that future.  
We are incredibly proud of what we've built and thrilled to share our journey with you.

---

## 🚀 Project Overview

This repository contains our complete, containerized solutions for both challenges in Round 1.  
We tackled each challenge as a step towards a more intelligent and interactive document experience.

---

### 📄 Challenge 1A: Understand Your Document

In this first step, we taught our system to **see structure**.  
We learned that to truly understand a document, we must look beyond simple text and analyze its visual layout.

🔧 Our solution uses **PyMuPDF** to parse documents, identifying headings and outlines based on their structural properties rather than fragile font-based rules.

📁 For a detailed explanation, code, and execution instructions, please see the `Challenge_1a/` directory.

---

### 🧠 Challenge 1B: Persona-Driven Document Intelligence

Here, we taught our system to **understand context**.  
We discovered the power of **semantic search** to connect a user's unique intent with the most relevant content.

📌 Our three-stage pipeline:
1. Extracts logical sections from multiple documents  
2. Uses the `all-MiniLM-L6-v2` model to rank them by relevance to a specific **persona**  
3. Provides concise summaries of the most important findings

📁 The complete solution, including detailed documentation and Docker instructions, is available in the `Challenge_1b/` directory.

---

## 🙏 Thank You

Thank you for the opportunity to participate in this incredible event.  
We hope our work reflects our commitment and passion for building the future of digital experiences.

Sincerely,  
**Team Hackies**
