interface Props {
  onSelect: (text: string) => void
}

const transcript = [
  { id: 1, text: "Hola", start: 0.0 },
  { id: 2, text: "¿qué", start: 0.2 },
  { id: 3, text: "tal?", start: 0.4 }
]

export default function TranscriptPanel({ onSelect }: Props) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 12, maxHeight: 300, overflowY: "auto" }}>
      {transcript.map(word => (
        <span
          key={word.id}
          onClick={() => onSelect(word.text)}
          style={{
            cursor: "pointer",
            marginRight: 6,
            padding: "2px 6px",
            borderRadius: 4,
            background: "#f3f3f3"
          }}
        >
          {word.text}
        </span>
      ))}
    </div>
  )
}