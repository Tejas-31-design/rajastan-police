import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import i18n from '../i18n'
import SyntheticBadge from './SyntheticBadge'

export default function Navbar() {
  const { t } = useTranslation()
  const location = useLocation()
  const isActive = (path: string) => location.pathname === path

  const toggleLang = () => {
    const newLang = i18n.language === 'en' ? 'hi' : 'en'
    i18n.changeLanguage(newLang)
    localStorage.setItem('fs-lang', newLang)
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-navy/95 backdrop-blur-md border-b border-white/10 h-16">
      <div className="max-w-7xl mx-auto px-4 h-full flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl">🛡️</span>
          <div>
            <span className="font-bold text-saffron text-lg leading-none">Fraud Shield</span>
            <div className="text-[10px] text-teal leading-none">Detect. Connect. Dismantle.</div>
          </div>
        </Link>

        {/* Nav links */}
        <div className="hidden md:flex items-center gap-1">
          <Link
            to="/"
            className={`tab ${isActive('/') ? 'tab-active' : 'tab-inactive'}`}
          >
            {t('nav.home')}
          </Link>
          <Link
            to="/dashboard"
            className={`tab ${isActive('/dashboard') ? 'tab-active' : 'tab-inactive'}`}
          >
            {t('nav.dashboard')}
          </Link>
          <Link
            to="/about"
            className={`tab ${isActive('/about') ? 'tab-active' : 'tab-inactive'}`}
          >
            {t('nav.about')}
          </Link>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          <SyntheticBadge />
          <button
            onClick={toggleLang}
            className="btn-secondary text-xs"
          >
            {t('nav.language')}
          </button>
        </div>
      </div>

      {/* Mobile nav */}
      <div className="md:hidden flex border-t border-white/10 bg-navy/95">
        <Link to="/" className={`flex-1 text-center py-2 text-xs ${isActive('/') ? 'text-saffron' : 'text-white/60'}`}>
          {t('nav.home')}
        </Link>
        <Link to="/dashboard" className={`flex-1 text-center py-2 text-xs ${isActive('/dashboard') ? 'text-saffron' : 'text-white/60'}`}>
          {t('nav.dashboard')}
        </Link>
        <Link to="/about" className={`flex-1 text-center py-2 text-xs ${isActive('/about') ? 'text-saffron' : 'text-white/60'}`}>
          {t('nav.about')}
        </Link>
      </div>
    </nav>
  )
}
