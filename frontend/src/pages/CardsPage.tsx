import { useEffect, useState } from "react"
import CardItem, { type Card } from "../components/CardItem"
import ExportAnkiModal from "../components/ExportAnkiModal"
import type { VideoRecord } from "../types/language"
import styles from "./CardsPage.module.css"

const API = import.meta.env.VITE_API_BASE_URL;

interface VideoWithCards extends VideoRecord {
  cards: Card[]
}

export default function CardsPage() {
  const [sections, setSections]   = useState<VideoWithCards[]>([])
  const [loading, setLoading]     = useState(true)
  const [ankiOpen, setAnkiOpen]   = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const videos: VideoRecord[] = await fetch(`${API}/api/video/all`).then(r => r.json())
        const withCards = await Promise.all(
          videos.map(async v => {
            const cards: Card[] = await fetch(`${API}/api/cards/${v.id}`).then(r => r.json())
            return { ...v, cards }
          })
        )
        setSections(withCards.filter(v => v.cards.length > 0))
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  async function handleDelete(cardId: number, videoId: string) {
    await fetch(`${API}/api/cards/${cardId}`, { method: "DELETE" })
    setSections(prev =>
      prev
        .map(v => v.id === videoId ? { ...v, cards: v.cards.filter(c => c.id !== cardId) } : v)
        .filter(v => v.cards.length > 0)
    )
  }

  const totalCards = sections.reduce((acc, v) => acc + v.cards.length, 0)

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1>🗂 Saved Cards</h1>
          <p className={styles.subtitle}>
            {loading ? "Loading..." : `${totalCards} card${totalCards !== 1 ? "s" : ""} across ${sections.length} video${sections.length !== 1 ? "s" : ""}`}
          </p>
        </div>
        {!loading && totalCards > 0 && (
          <button onClick={() => setAnkiOpen(true)}>Export All to Anki</button>
        )}
      </div>

      {!loading && sections.length === 0 && (
        <p className={styles.empty}>No cards saved yet. Go to a video and save some words!</p>
      )}

      {sections.map(v => (
        <div key={v.id} className={styles.videoSection}>
          <h2>{v.title} — {v.from_lang} → {v.to_lang}</h2>
          <div className={styles.grid}>
            {v.cards.map(card => (
              <CardItem key={card.id} card={card} onDelete={id => handleDelete(id, v.id)} />
            ))}
          </div>
        </div>
      ))}

      {ankiOpen && (
        <ExportAnkiModal
          defaultDeckName="LangReader"
          onClose={() => setAnkiOpen(false)}
        />
      )}
    </div>
  )
}