# 🛡️ RapidVerify - AI-Powered Misinformation Detection Platform

<div align="center">

![RapidVerify Logo](https://img.shields.io/badge/RapidVerify-AI%20Powered-00f5d4?style=for-the-badge&logo=shield&logoColor=white)
![Mumbai Hacks 25](https://img.shields.io/badge/Mumbai%20Hacks-'25-7b2cbf?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![AI](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

**Stop Misinformation Before It Goes Viral** 🚀

[Live Demo](#) • [Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API](#-api-endpoints)

</div>

---

## 🎯 Problem Statement

During emergencies, festivals, and public health crises, **misinformation spreads faster than facts**. False rumors, panic-inducing claims, and fake news can be **dangerous** - causing public panic, health risks, and even loss of life.

**RapidVerify** is an **Agentic AI platform** built to fight the viral spread of misinformation in real-time, providing communities and authorities with trusted, instantly verified information.

---

## ✨ Key Features

### 🔍 Continuous Social Scanning
- 24/7 monitoring of **Twitter/X, Telegram, Facebook**, and news websites
- Real-time detection of viral claims and emerging misinformation
- AI-powered trend analysis and urgency ranking

### 🧠 AI-Powered Claim Extraction
- Advanced **NLP using Google Gemini Pro** for claim extraction
- Intelligent clustering and categorization of rumors
- Risk assessment and urgency scoring (Critical/High/Medium/Low)

### ✅ Trusted Verification
- Multi-source cross-verification against:
  - Government databases (PIB India)
  - Health authorities (WHO, CDC)
  - Verified news APIs (Reuters, AFP)
  - Historical fact-checks (FactCheck.org)
- **Multi-Agent Architecture**:
  - **Orchestrator Agent**: Coordinates the verification process
  - **Search Agent**: Finds historical evidence using MCP Server
  - **Scorer Agent**: Calculates authenticity scores

### 📢 Public Notifications
- **Dashboard**: Real-time monitoring interface
- **Web App**: User-friendly verification portal
- **Chatbots**: Telegram bot integration
- **SMS Alerts**: For critical misinformation warnings

### ⛓️ Blockchain Transparency
- High-impact advisories anchored on blockchain
- Tamper-proof timestamping for public warnings
- Full traceability and authenticity verification

---

## 🖼️ Screenshots

### Landing Page
Modern glassmorphism design with animated background effects
![Landing Page](./screenshots/landing.png)

### Real-Time Dashboard
Live monitoring of trending claims across platforms
![Dashboard](./screenshots/dashboard.png)

### Verification Interface
AI-powered claim verification with detailed scoring
![Verification](./screenshots/verify.png)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google API Key (for Gemini AI)
- Node.js (optional, for MCP Server)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/rapidverify.git
cd rapidverify

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run the application
python api/app.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
MCP_SERVER_URL=http://localhost:3000  # Optional: Google Search MCP Server
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### Access the Application

- **Landing Page**: http://localhost:5000
- **Dashboard**: http://localhost:5000/dashboard
- **Verify Page**: http://localhost:5000/verify

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        RapidVerify                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────┐    ┌──────────────┐    ┌───────────────────┐    │
│  │  Frontend │    │   Flask API  │    │   AI Agents       │    │
│  │  (HTML/   │◄──►│   Backend    │◄──►│                   │    │
│  │   CSS/JS) │    │              │    │  ┌─────────────┐  │    │
│  └───────────┘    └──────────────┘    │  │Orchestrator │  │    │
│                          │            │  │   Agent     │  │    │
│                          │            │  └──────┬──────┘  │    │
│                          │            │         │         │    │
│                          │            │    ┌────┴────┐    │    │
│                          │            │    │         │    │    │
│                          │            │  ┌─▼──┐   ┌──▼─┐  │    │
│                          │            │  │Search│ │Scorer│ │    │
│                          │            │  │Agent │ │Agent │ │    │
│                          │            │  └──────┘ └──────┘ │    │
│                          │            └───────────────────┘    │
│                          │                      │              │
│                          ▼                      ▼              │
│              ┌──────────────────┐    ┌──────────────────┐     │
│              │  External APIs   │    │   Google Gemini   │     │
│              │  (News, Govt,    │    │   Pro AI Model    │     │
│              │   Fact-checks)   │    └──────────────────┘     │
│              └──────────────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Agent System

| Agent | Responsibility |
|-------|----------------|
| **Orchestrator** | Coordinates the overall process, manages agent communication |
| **Search Agent** | Searches historical news using MCP Server, finds evidence |
| **Scorer Agent** | Analyzes content authenticity using multiple scoring criteria |

### Scoring Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Source Credibility | 25% | Reputation of the news source |
| Evidence Support | 30% | Historical evidence supporting claims |
| Internal Consistency | 20% | Logical coherence within the article |
| Language Analysis | 15% | Detection of sensationalist patterns |
| Factual Accuracy | 10% | Verification of specific facts |

---

## 📡 API Endpoints

### Verify Claim
```http
POST /api/verify
Content-Type: application/json

{
  "claim": "Text to verify",
  "source": "Telegram Message"
}
```

**Response:**
```json
{
  "success": true,
  "verification_score": 0.12,
  "status": "debunked",
  "category": "Likely Fake",
  "detailed_scores": {...},
  "evidence": [...],
  "report": "Analysis summary...",
  "blockchain_hash": "0x..."
}
```

### Get Trending Claims
```http
GET /api/trending?platform=all
```

### Get Statistics
```http
GET /api/statistics
```

### Subscribe to Alerts
```http
POST /api/alerts/subscribe
Content-Type: application/json

{
  "channel": "telegram",
  "username": "@rapidverifybot",
  "topics": ["health", "emergency"]
}
```

---

## 🎨 Design System

### Neomorphism + Glassmorphism

RapidVerify uses a unique combination of **Neomorphism** and **Glassmorphism** design principles:

- **Neomorphism**: Soft shadows and subtle 3D effects for interactive elements
- **Glassmorphism**: Translucent panels with backdrop blur for depth
- **Dark Theme**: Eye-friendly dark mode with vibrant accent colors

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#00f5d4` | Accents, CTAs, success states |
| Secondary | `#7b2cbf` | Highlights, secondary actions |
| Danger | `#ff6b6b` | Debunked claims, critical alerts |
| Warning | `#ffd93d` | Investigating, medium urgency |
| Success | `#6bcb77` | Verified claims, active status |

---

## 📁 Project Structure

```
RapidVerify/
├── api/
│   ├── app.py              # Flask backend & API endpoints
│   └── blockchain_service.py # Blockchain integration service
├── contracts/
│   ├── RapidVerify.sol     # Smart contract for verification records
│   ├── scripts/deploy.js   # Deployment script
│   └── hardhat.config.js   # Hardhat configuration
├── templates/
│   ├── index.html          # Landing page
│   ├── dashboard.html      # Real-time monitoring
│   └── verify.html         # Verification interface
├── static/
│   ├── css/
│   │   └── styles.css      # Neomorphism & Glassmorphism styles
│   └── js/
│       └── app.js          # Frontend JavaScript
├── temp_repo/
│   ├── agents/
│   │   ├── orchestrator.py # Main coordination agent
│   │   ├── search_agent.py # Evidence search agent
│   │   └── scorer_agent.py # Authenticity scoring agent
│   ├── utils/
│   │   ├── helpers.py      # Utility functions
│   │   └── mcp_client.py   # MCP Server client
│   ├── main.py             # CLI interface
│   └── requirements.txt    # Python dependencies
├── .env.example            # Environment template
├── requirements.txt        # Project dependencies
└── README.md               # This file
```

---

## 🔧 Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3 (Custom Neomorphism/Glassmorphism), Vanilla JavaScript |
| **Backend** | Python 3.9+, Flask 2.0+, Flask-CORS |
| **AI/ML** | Google Gemini Pro, LangChain, FAISS Vector Store |
| **NLP** | Google Generative AI Embeddings |
| **Database** | In-memory (demo), extensible to PostgreSQL/MongoDB |
| **Blockchain** | Polygon (Amoy testnet / Mainnet), Web3.py, Solidity |

---

## 🏆 Mumbai Hacks '25 Submission

### Team
- Built with ❤️ for Mumbai Hacks '25

### Problem Track
- **Social Impact / Misinformation Detection**

### Innovation Highlights
1. **Multi-Agent AI Architecture** - First-of-its-kind orchestrated verification system
2. **Real-Time Social Scanning** - Monitors multiple platforms simultaneously
3. **Unique Design System** - Neo + Glass morphism hybrid for modern UI
4. **Blockchain Anchoring** - Tamper-proof verification records

---

## 🛣️ Roadmap

- [x] Core verification engine
- [x] Web dashboard & verification UI
- [x] API endpoints
- [x] Neomorphism/Glassmorphism design
- [x] Telegram Bot integration (@rapidverifybot)
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [x] Blockchain integration (Polygon)
- [ ] Regional language support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Google Gemini AI for powerful NLP capabilities
- Mumbai Hacks '25 organizers
- Open-source community for amazing tools

---

<div align="center">

**Built with 🛡️ to fight misinformation**

[⬆ Back to Top](#-rapidverify---ai-powered-misinformation-detection-platform)

</div>

