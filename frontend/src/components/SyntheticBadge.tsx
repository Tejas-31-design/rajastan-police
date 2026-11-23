import { useTranslation } from 'react-i18next'

export default function SyntheticBadge() {
  const { t } = useTranslation()
  return (
    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-saffron/20 border border-saffron/40 text-saffron text-[10px] font-semibold tracking-wide">
      <span>⚗️</span>
      <span className="hidden sm:inline">{t('common.synthetic_badge')}</span>
    </span>
  )
}
