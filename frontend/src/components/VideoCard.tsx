import { Link } from "react-router-dom"
import styles from "./VideoCard.module.css"

interface VideoCardProps {
  id: string
  title: string
  fromLang: string
  toLang: string
}

export default function VideoCard({ id, title, fromLang, toLang }: VideoCardProps) {
  return (
    <Link to={`/video/${id}`}>
      <div className={styles.card}>
        <h3>{title}</h3>
        <p>{fromLang} → {toLang}</p>
      </div>
    </Link>
  )
}