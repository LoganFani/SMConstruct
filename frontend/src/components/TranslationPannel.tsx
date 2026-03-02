interface Props {
  selectedText: string | null
}

export default function TranslationPanel({ selectedText }: Props) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 12 }}>
      <h3>Translation</h3>

      {selectedText ? (
        <>
          <p><strong>Selected:</strong> {selectedText}</p>
          <p><strong>Context:</strong> (sentence here)</p>
          <p><strong>Translation:</strong> (LLM output)</p>
          <button>Create Anki Card</button>
        </>
      ) : (
        <p>Click a word or phrase to translate</p>
      )}
    </div>
  )
}