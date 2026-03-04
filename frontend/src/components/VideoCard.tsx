import { Link } from "react-router-dom"
import styles from "./VideoCard.module.css"

interface VideoCardProps {
  id: string
  title: string
  fromLang: string
  toLang: string
  onDelete: (id: string) => void
}

export default function VideoCard({ id, title, fromLang, toLang, onDelete }: VideoCardProps) {
  return (
    <div className={styles.cardWrapper}>
      <Link to={`/video/${id}`} className={styles.link}>
        <div className={styles.card}>
          <h3>{title}</h3>
          <p>{fromLang} → {toLang}</p>
        </div>
      </Link>
      <button
        className={styles.deleteBtn}
        onClick={e => { e.preventDefault(); onDelete(id) }}
      >
        ✕ Delete
      </button>
    </div>
  )
}