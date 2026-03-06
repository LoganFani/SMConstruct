import { useEffect, useState } from "react"
import styles from "./ExportAnkiModal.module.css"

const API = import.meta.env.VITE_API_BASE_URL;

interface Props {
  videoId?: string       // if undefined, export all cards globally
  defaultDeckName?: string
  onClose: () => void
}

type Mode = "existing" | "new"

interface ExportResult {
  deck_name: string
  exported: number
  skipped_duplicate: number
  skipped_already_exported: number
}

export default function ExportAnkiModal({ videoId, defaultDeckName = "", onClose }: Props) {
  const [mode, setMode] = useState<Mode>("existing")
  const [decks, setDecks] = useState<string[]>([])
  const [decksLoading, setDecksLoading] = useState(true)
  const [decksError, setDecksError] = useState<string | null>(null)

  const [selectedDeck, setSelectedDeck] = useState<string>("")
  const [newDeckName, setNewDeckName]   = useState(defaultDeckName)

  const [exporting, setExporting]     = useState(false)
  const [result, setResult]           = useState<ExportResult | null>(null)
  const [exportError, setExportError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API}/api/anki/decks`)
      .then(r => {
        if (!r.ok) throw new Error("Could not reach AnkiConnect. Is Anki open?")
        return r.json()
      })
      .then((data: string[]) => {
        setDecks(data)
        if (data.length > 0) setSelectedDeck(data[0])
        setDecksLoading(false)
      })
      .catch(err => {
        setDecksError(err.message || "Failed to load decks")
        setDecksLoading(false)
        setMode("new")   // fall back to new deck if Anki unreachable
      })
  }, [])

  async function handleExport() {
    const deckName = mode === "existing" ? selectedDeck : newDeckName.trim()
    if (!deckName) return

    setExporting(true)
    setExportError(null)
    setResult(null)

    try {
      const res = await fetch(`${API}/api/anki/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: videoId ?? null,
          deck_name: deckName,
        }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "Export failed")
      }
      const data: ExportResult = await res.json()
      setResult(data)
    } catch (err: any) {
      setExportError(err.message || "Export failed")
    } finally {
      setExporting(false)
    }
  }

  const deckName = mode === "existing" ? selectedDeck : newDeckName.trim()
  const canExport = !exporting && !!deckName && !result

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h3>Export to Anki</h3>
        <p>{videoId ? "Export cards from this video to an Anki deck." : "Export all saved cards to an Anki deck."}</p>

        {/* Mode tabs */}
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${mode === "existing" ? styles.active : ""}`}
            onClick={() => setMode("existing")}
          >
            Existing Deck
          </button>
          <button
            className={`${styles.tab} ${mode === "new" ? styles.active : ""}`}
            onClick={() => setMode("new")}
          >
            New Deck
          </button>
        </div>

        {mode === "existing" ? (
          decksLoading ? (
            <p>Loading decks...</p>
          ) : decksError ? (
            <p className={styles.error}>{decksError}</p>
          ) : (
            <div className={styles.deckList}>
              {decks.map(d => (
                <button
                  key={d}
                  className={`${styles.deckOption} ${selectedDeck === d ? styles.selected : ""}`}
                  onClick={() => setSelectedDeck(d)}
                >
                  {d}
                </button>
              ))}
            </div>
          )
        ) : (
          <input
            placeholder="Deck name (e.g. Spanish Vocab)"
            value={newDeckName}
            onChange={e => setNewDeckName(e.target.value)}
          />
        )}

        {result && (
          <div className={styles.result}>
            ✓ Exported <strong>{result.exported}</strong> card{result.exported !== 1 ? "s" : ""} to <strong>{result.deck_name}</strong>
            {result.skipped_already_exported > 0 && (
              <div>{result.skipped_already_exported} already exported to this deck — skipped</div>
            )}
            {result.skipped_duplicate > 0 && (
              <div>{result.skipped_duplicate} duplicate{result.skipped_duplicate !== 1 ? "s" : ""} rejected by Anki</div>
            )}
          </div>
        )}

        {exportError && <p className={styles.error}>{exportError}</p>}

        <div className={styles.actions}>
          <button onClick={onClose}>{result ? "Close" : "Cancel"}</button>
          {!result && (
            <button className={styles.exportBtn} onClick={handleExport} disabled={!canExport}>
              {exporting ? "Exporting..." : "Export"}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}