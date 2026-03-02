import { Link } from "react-router-dom"
import VideoCard from "../components/VideoCard"
import LanguageConfigCard from "../components/LanguageConfigCard"

export default function HomePage() {
  // Mock data (replace with API later)
  const videos = [
    { id: "abc123", title: "How to Spanish Podcast Ep 1", fromLang: "Spanish", toLang: "English" },
    { id: "xyz456", title: "Beginner Conversations", fromLang: "Spanish", toLang: "English" },
  ]

  const languageConfigs = [
    { fromLang: "Spanish", toLang: "English" },
    { fromLang: "Japanese", toLang: "English" },
  ]

  return (
    <div style={{ padding: 32 }}>
      <h1>🎓 Language Video Trainer</h1>

      <div style={{ marginTop: 16 }}>
        <Link to="/new">
          <button style={{ padding: "8px 16px" }}>+ New Video</button>
        </Link>
      </div>

      <h2 style={{ marginTop: 32 }}>Your Videos</h2>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        {videos.map(v => (
          <VideoCard key={v.id} {...v} />
        ))}
      </div>

      <h2 style={{ marginTop: 40 }}>Language Configurations</h2>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        {languageConfigs.map((c, i) => (
          <LanguageConfigCard key={i} {...c} />
        ))}

        <div
          style={{
            border: "1px dashed #aaa",
            borderRadius: 8,
            padding: 12,
            width: 180,
            textAlign: "center",
            cursor: "pointer",
          }}
        >
          + Add New
        </div>
      </div>
    </div>
  )
}