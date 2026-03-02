import { Link } from "react-router-dom"

interface VideoCardProps {
  id: string
  title: string
  fromLang: string
  toLang: string
}

export default function VideoCard({ id, title, fromLang, toLang }: VideoCardProps) {
  return (
    <Link to={`/video/${id}`} style={{ textDecoration: "none", color: "inherit" }}>
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 8,
          padding: 16,
          width: 220,
          cursor: "pointer",
        }}
      >
        <h3>{title}</h3>
        <p>{fromLang} → {toLang}</p>
      </div>
    </Link>
  )
}