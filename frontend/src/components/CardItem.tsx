import styles from "./CardItem.module.css"

const API = import.meta.env.VITE_API_BASE_URL;

export interface Card {
  id: number
  video_id: string
  word: string
  context: string
  translation: string
  frame_path: string | null
  audio_path: string | null
  created_at: string
}

interface Props {
  card: Card
  onDelete: (id: number) => void
}

export default function CardItem({ card, onDelete }: Props) {
  return (
    <div className={styles.card}>
      {card.frame_path ? (
        <img
          className={styles.frame}
          src={`${API}/api/capture/frame-file/${encodeURIComponent(card.frame_path)}`}
          alt="card frame"
        />
      ) : (
        <div className={styles.framePlaceholder}>No frame</div>
      )}

      <div className={styles.body}>
        <div className={styles.word}>{card.word}</div>
        <div className={styles.translation}>{card.translation}</div>
        <div className={styles.context}>{card.context}</div>

        {card.audio_path && (
          <audio
            className={styles.audio}
            controls
            src={`${API}/api/capture/audio-file/${encodeURIComponent(card.audio_path)}`}
          />
        )}

        <div className={styles.footer}>
          <button className={styles.deleteBtn} onClick={() => onDelete(card.id)}>
            ✕ Delete
          </button>
        </div>
      </div>
    </div>
  )
}