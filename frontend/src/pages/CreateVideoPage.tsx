import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import type { LanguageConfig } from "../types/language"
import styles from "./CreateVideoPage.module.css"

const API = "http://127.0.0.1:8000"

export default function CreateVideoPage() {
  const navigate = useNavigate()

  const [url, setUrl] = useState("")
  const [title, setTitle] = useState("")
  const [transcript, setTranscript] = useState("")
  const [configs, setConfigs] = useState<LanguageConfig[]>([])
  const [selectedConfig, setSelectedConfig] = useState<LanguageConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API}/api/language-configs/`)
      .then(r => r.json())
      .then((data: LanguageConfig[]) => {
        setConfigs(data)
        if (data.length > 0) setSelectedConfig(data[0])
      })
      .catch(console.error)
  }, [])

  async function handleCreate() {
    if (!url || !title || !transcript) { setError("Please provide a URL, title, and transcript."); return }
    if (!selectedConfig) { setError("Please select a language configuration."); return }
    setLoading(true)
    setError(null)
    try {
      const videoRes = await fetch(`${API}/api/video/load`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_url: url, title, from_lang: selectedConfig.from_lang, to_lang: selectedConfig.to_lang }),
      })
      if (!videoRes.ok) throw new Error("Video download failed")
      const { video_id } = await videoRes.json()

      const transcriptRes = await fetch(`${API}/api/transcript/convert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id, transcript }),
      })
      if (!transcriptRes.ok) throw new Error("Transcript conversion failed")

      navigate(`/video/${video_id}`, {
        state: { fromLang: selectedConfig.from_lang, toLang: selectedConfig.to_lang },
      })
    } catch (err: any) {
      setError(err.message || "Failed to create video")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <h1>Create New Video</h1>

      <div className={styles.form}>
        <label>YouTube URL</label>
        <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://youtube.com/watch?v=..." />

        <label>Video Title</label>
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="My Spanish Podcast Ep. 1" />

        <label>Paste Transcript</label>
        <textarea rows={8} value={transcript} onChange={e => setTranscript(e.target.value)} placeholder="Paste YouTube transcript here..." />

        <label>Language Configuration</label>
        {configs.length === 0 ? (
          <p className={styles.emptyMsg}>No language configs found. <a href="/">Create one on the home page first.</a></p>
        ) : (
          <select
            value={selectedConfig?.id ?? ""}
            onChange={e => setSelectedConfig(configs.find(c => c.id === Number(e.target.value))!)}
          >
            {configs.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        )}

        {error && <p className={styles.error}>{error}</p>}

        <button className={styles.submitBtn} onClick={handleCreate} disabled={loading || configs.length === 0}>
          {loading ? "Processing..." : "Create Video"}
        </button>
      </div>
    </div>
  )
}