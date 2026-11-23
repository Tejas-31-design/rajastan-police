import { useTranslation } from 'react-i18next'
import SyntheticBadge from '../components/SyntheticBadge'

const TEAM = [
  { name: 'Tejas Bhadait', role: 'ML & Backend Lead', emoji: '🧠' },
  { name: 'Jatin Sonawane', role: 'Frontend & UX', emoji: '🎨' },
  { name: 'Bhavarth Baviskar', role: 'Clustering & Graph', emoji: '🔗' },
  { name: 'Shreyash Dube', role: 'PDF, Integration & Testing', emoji: '🧪' },
]

const TECH = [
  { layer: 'API', tech: 'Python 3.11 · FastAPI · Uvicorn', color: 'text-teal' },
  { layer: 'Database', tech: 'SQLite · SQLAlchemy 2.0', color: 'text-blue-400' },
  { layer: 'ML', tech: 'scikit-learn · RandomForest · TF-IDF · LogReg', color: 'text-saffron' },
  { layer: 'Similarity', tech: 'rapidfuzz · tldextract', color: 'text-purple-400' },
  { layer: 'Graph', tech: 'NetworkX · react-force-graph-2d', color: 'text-pink-400' },
  { layer: 'Export', tech: 'ReportLab PDF', color: 'text-orange-400' },
  { layer: 'Frontend', tech: 'React 18 · Vite · TypeScript · Tailwind', color: 'text-cyan-400' },
  { layer: 'Maps', tech: 'Leaflet.js', color: 'text-green-400' },
  { layer: 'Charts', tech: 'Recharts', color: 'text-yellow-400' },
  { layer: 'i18n', tech: 'i18next (English + Hindi)', color: 'text-teal' },
]

export default function About() {
  const { t } = useTranslation()

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="text-center mb-10">
        <div className="text-6xl mb-4">🛡️</div>
        <h1 className="text-4xl font-extrabold text-white mb-2">{t('about.title')}</h1>
        <p className="text-teal font-semibold text-lg">Detect. Connect. Dismantle.</p>
        <p className="text-white/40 text-sm mt-2">
          Rajasthan Police Hackathon 2026 · PS01: Cyber Fraud, Phishing & Malicious Apps
        </p>
        <div className="flex justify-center mt-4">
          <SyntheticBadge />
        </div>
      </div>

      {/* Problem */}
      <div className="card p-6 mb-6 border-alert-red/20">
        <h2 className="text-xl font-bold text-alert-red mb-3">⚠️ {t('about.problem_title')}</h2>
        <p className="text-white/70 leading-relaxed">
          Cyber fraud through phishing URLs, smishing (SMS scams), and malicious Android apps is rising rapidly
          in Rajasthan. Citizens receive deceptive messages impersonating SBI, HDFC, RTO, JVVNL, and India Post —
          tricking them into revealing credentials and transferring money. Law enforcement lacks a unified platform
          to detect, cluster, and dismantle these coordinated fraud campaigns before they scale.
        </p>
      </div>

      {/* Solution */}
      <div className="card p-6 mb-6 border-teal/20">
        <h2 className="text-xl font-bold text-teal mb-3">✅ {t('about.solution_title')}</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { icon: '🔍', title: 'Detect', desc: 'Explainable ML + rules analyze URLs and SMS messages in real time, returning risk scores, reasons, and signal weights.' },
            { icon: '🔗', title: 'Connect', desc: 'NetworkX graph clustering links reports by shared indicators (domains, phones, UPI IDs) to reveal coordinated campaigns.' },
            { icon: '💥', title: 'Dismantle', desc: 'Takedown evidence PDFs, campaign graphs, and district hotspot maps give law enforcement actionable intelligence.' },
          ].map(item => (
            <div key={item.title} className="bg-navy/60 rounded-xl p-4">
              <div className="text-3xl mb-2">{item.icon}</div>
              <h3 className="font-bold text-saffron mb-1">{item.title}</h3>
              <p className="text-white/60 text-sm leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture */}
      <div className="card p-6 mb-6">
        <h2 className="text-xl font-bold text-white mb-4">🏗️ {t('about.arch_title')}</h2>
        <div className="bg-navy rounded-xl p-4 text-xs font-mono text-white/60 leading-7">
          <div><span className="text-saffron">Citizen / Officer</span> → React Frontend [:5173]</div>
          <div className="pl-4">↓ axios REST + EventSource SSE</div>
          <div><span className="text-teal">FastAPI Backend</span> [:8000]</div>
          <div className="pl-4">├─ <span className="text-purple-400">POST /api/check/url</span> → URL Analyzer (RF + Rules, 0.6+0.4)</div>
          <div className="pl-4">├─ <span className="text-purple-400">POST /api/check/sms</span> → SMS Classifier (TF-IDF + LR + Regex)</div>
          <div className="pl-4">├─ <span className="text-purple-400">GET  /api/dashboard/*</span> → KPIs, Trend, Hotspots</div>
          <div className="pl-4">├─ <span className="text-purple-400">GET  /api/campaigns/*</span> → List, Detail, Graph, PDF</div>
          <div className="pl-4">└─ <span className="text-purple-400">GET  /api/live-feed</span> → SSE stream (3s events)</div>
          <div className="pl-4">↓ SQLAlchemy</div>
          <div><span className="text-blue-400">SQLite</span> [fraud_shield.db] — Reports, Campaigns, Indicators</div>
          <div className="pl-4">↑ NetworkX clustering (connected components + TF-IDF cosine ≥ 0.7)</div>
        </div>
      </div>

      {/* Scoring */}
      <div className="card p-6 mb-6">
        <h2 className="text-xl font-bold text-white mb-4">🧮 Detection Logic</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-navy/60 rounded-xl p-4">
            <h3 className="font-semibold text-saffron mb-2">URL Scoring</h3>
            <code className="text-xs text-white/70 block">
              Score = 0.6 × ML (RandomForest) <br/>
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.4 × Rules<br/><br/>
              Features: TLD, keywords, HTTPS,<br/>
              lookalike (rapidfuzz), homoglyph,<br/>
              domain age, subdomain depth, length
            </code>
          </div>
          <div className="bg-navy/60 rounded-xl p-4">
            <h3 className="font-semibold text-saffron mb-2">SMS Scoring</h3>
            <code className="text-xs text-white/70 block">
              Score = 0.6 × ML (TF-IDF + LogReg)<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.4 × Rules<br/><br/>
              Themes: KYC, Prize, Loan, Electricity,<br/>
              Parcel, Job, UPI<br/>
              Languages: English, Hindi, Hinglish
            </code>
          </div>
        </div>
        <div className="flex gap-4 mt-4 text-sm">
          <span className="text-teal">🟢 0–39 → Safe</span>
          <span className="text-saffron">🟡 40–69 → Suspicious</span>
          <span className="text-alert-red">🔴 70–100 → High Risk</span>
        </div>
      </div>

      {/* Tech Stack */}
      <div className="card p-6 mb-6">
        <h2 className="text-xl font-bold text-white mb-4">⚙️ {t('about.tech_title')}</h2>
        <div className="grid md:grid-cols-2 gap-2">
          {TECH.map(item => (
            <div key={item.layer} className="flex items-center gap-3 bg-navy/60 rounded-lg p-3">
              <span className={`text-xs font-bold uppercase w-20 flex-shrink-0 ${item.color}`}>{item.layer}</span>
              <span className="text-white/70 text-sm">{item.tech}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Team */}
      <div className="card p-6">
        <h2 className="text-xl font-bold text-white mb-6">👥 {t('about.team_title')}</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {TEAM.map(member => (
            <div key={member.name} className="flex items-center gap-4 bg-navy/60 rounded-xl p-4">
              <div className="text-4xl">{member.emoji}</div>
              <div>
                <div className="font-semibold text-white">{member.name}</div>
                <div className="text-saffron text-sm">{member.role}</div>
                <div className="text-white/40 text-xs mt-0.5">MIT Academy of Engineering</div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 text-center text-white/40 text-sm">
          <p>Team Dholakpurwale · Rajasthan Police Hackathon 2026</p>
          <p className="mt-1">PS01: Cyber Fraud, Phishing & Malicious Apps</p>
        </div>
      </div>
    </div>
  )
}
