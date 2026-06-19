# 🤖 Agentic Supply Chain Control Tower

An enterprise-grade, event-driven multi-agent AI system for automated supply chain management.

## 🌟 Features

- **Multi-Agent Orchestration**: LangGraph workflow with Investigator, Optimizer, Explainer, and Executor agents
- **Real-Time Event Streaming**: Apache Kafka triggers autonomous agent workflows
- **Context-Aware RAG**: Qdrant vector database for supplier contracts and SLAs
- **Deterministic Math**: Python tools prevent LLM hallucinations in financial calculations
- **Human-in-the-Loop**: LangGraph interrupts ensure governance before execution
- **Production Observability**: LangSmith tracing for full transparency

## 🏗️ Architecture

![Architecture Diagram](./architecture.png)

## 🚀 Quick Start

```bash
# 1. Start infrastructure (Kafka, Qdrant)
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed mock data
python src/seed_data.py
python src/generate_mock_pdfs.py
python src/tools/rag_setup.py

# 4. Run the agent
python -m src.main
```
