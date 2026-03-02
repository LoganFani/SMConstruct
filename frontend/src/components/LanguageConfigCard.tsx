interface LanguageConfigCardProps {
  fromLang: string
  toLang: string
}

export default function LanguageConfigCard({ fromLang, toLang }: LanguageConfigCardProps) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 8,
        padding: 12,
        width: 180,
        textAlign: "center",
      }}
    >
      <strong>{fromLang} → {toLang}</strong>
    </div>
  )
}