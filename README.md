# MLJ Results Compiler

**Intelligent conversational document processing bot with advanced test consolidation capabilities.**

Version: 0.2.0 | Status: **Alpha** | License: MIT

---

## 🌟 Core Features

- 🤖 **Telegram Bot**: Upload files directly and interact via natural language.
- 💾 **Persistence**: All sessions and results are stored in a persistent SQLite database.
- 🛠️ **Consolidation**: Automated matching and merging of multi-test Excel results.
- 💬 **AI Assistant**: Intent detection and agentic data manipulation.

## 🚀 Quick Start

1. **Telegram**: Find your bot, send `/start`, and upload your `.xlsx` files.
2. **Web**: Visit your deployment URL and follow the upload prompts.
3. **Local Development**:
   ```bash
   pip install -r requirements.txt
   uvicorn server:app --reload
   ```

## 📖 Documentation

For technical details, design mechanics, and deployment guides, please see the [docs/](docs/) directory:

- [**Design Mechanics**](docs/DESIGN_MECHANICS.md): How the Hybrid Bridge, SQLite layer, and AI system work.
- [**Architecture**](docs/ARCHITECTURE.md): Service breakdown and data schemas.
- [**Deployment**](docs/DEPLOYMENT.md): Guide for deploying to Render or other cloud providers.
- [**Security**](docs/SECURITY.md): Protocols and safety measures.

---
*Developed for efficient academic result management.*
