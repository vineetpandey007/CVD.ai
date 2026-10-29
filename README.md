 
# CVD.ai — Neural C/C++ Vulnerability Scanner & Semantic Auditor

[![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Groq](https://img.shields.io/badge/Groq-NLG%20Engine-f37b34?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![React](https://img.shields.io/badge/React-Vite%20%2B%20TS-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)

**CVD.ai** is an enterprise-grade, full-stack static analysis and AI security auditing platform. It unifies fine-tuned deep learning (CodeBERT), explainable AI (LIME token weights), lightning-fast Large Language Model threat report generation (Groq LLM), and semantic vector database search (ChromaDB) to detect, explain, and patch vulnerabilities in C/C++ codebases in real-time.

---

## 🚀 Neural Architecture & Pipeline

1. **CodeBERT Deep Learning Classification**
   - Fine-tuned `RoBERTa` transformer model trained on ~1.27M C/C++ source code functions (Draper VDISC / Devign datasets).
   - Intelligently detects memory corruption, buffer overflows, and logic flaws with high validation accuracy.

2. **Explainable AI (LIME)**
   - Integrates Local Interpretable Model-agnostic Explanations (LIME) to isolate exactly which syntax tokens, variables, or function calls triggered the vulnerability flag, mapping mathematical probabilistic risk to human-readable lines.

3. **Semantic Vector Search (ChromaDB)**
   - Converts pasted C/C++ functions into 768-dimensional mathematical vector embeddings (`[CLS]` pooling).
   - Queries a persistent local ChromaDB vector store to instantly surface structurally similar vulnerable functions across historical databases.

4. **Seq2Seq NLG Executive Threat Reports (Groq LLM)**
   - Synthesizes structured security audit reports instantly using Groq’s high-speed inference engine (`gpt-oss-20b`).
   - Enforces strict constraints (**The Issue**, **The Danger**, **The Fix**) alongside production-ready, null-terminated C/C++ code patches.

5. **Cyber-Brutalist UI & PDF Export**
   - Built with React, Vite, and Tailwind CSS.
   - Features instantaneous executive PDF report generation (via `html2canvas` / `jsPDF`) omitting interactive terminal UI elements for clean exports.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Uvicorn, Pydantic, Python 3.13
- **Machine Learning & NLP:** PyTorch, Transformers (HuggingFace CodeBERT), Scikit-learn, LIME
- **Vector Database:** ChromaDB (Persistent Client)
- **AI Inference Engine:** Groq API 
- **Frontend:** React, TypeScript, Tailwind CSS, Vite, Lucide Icons

---

## ⚙️ Local Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/vineetpandey007/CVD.ai.git](https://github.com/vineetpandey007/CVD.ai.git)
cd CVD.ai