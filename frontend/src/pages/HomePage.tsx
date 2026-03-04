import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import VideoCard from "../components/VideoCard"
import DeleteVideoModal from "../components/DeleteVideoModal"
import type { LanguageConfig, VideoRecord } from "../types/language"
import styles from "./HomePage.module.css"

const API = "http://127.0.0.1:8000"

export default function HomePage() {
  const [videos, setVideos] = useState<VideoRecord[]>([])
  const [configs, setConfigs] = useState<LanguageConfig[]>([])

  const [pendingDelete, setPendingDelete] = useState<VideoRecord | null>(null)

  const [showConfigForm, setShowConfigForm] = useState(false)
  const [newName, setNewName] = useState("")
  const [newFromLang, setNewFromLang] = useState("")
  const [newToLang, setNewToLang] = useState("")
  const [configSaving, setConfigSaving] = useState(false)
  const [configError, setConfigError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API}/api/video/all`).then(r => r.json()).then(setVideos).catch(console.error)
    fetch(`${API}/api/language-configs/`).then(r => r.json()).then(setConfigs).catch(console.error)
  }, [])

  async function handleConfirmDelete(full: boolean) {
    if (!pendingDelete) return
    await fetch(`${API}/api/video/${pendingDelete.id}?full=${full}`, { method: "DELETE" })
    setVideos(prev => prev.filter(v => v.id !== pendingDelete.id))
    setPendingDelete(null)
  }

  async function handleAddConfig() {
    if (!newName || !newFromLang || !newToLang) { setConfigError("All fields are required."); return }
    setConfigSaving(true); setConfigError(null)
    try {
      const res = await fetch(`${API}/api/language-configs/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName, from_lang: newFromLang, to_lang: newToLang }),
      })
      if (!res.ok) throw new Error("Failed to save config")
      const created: LanguageConfig = await res.json()
      setConfigs(prev => [created, ...prev])
      setNewName(""); setNewFromLang(""); setNewToLang("")
      setShowConfigForm(false)
    } catch (err: any) {
      setConfigError(err.message || "Error saving config")
    } finally {
      setConfigSaving(false)
    }
  }

  async function handleDeleteConfig(id: number) {
    await fetch(`${API}/api/language-configs/${id}`, { method: "DELETE" })
    setConfigs(prev => prev.filter(c => c.id !== id))
  }

  return (
    <div className={styles.page}>
      <h1>Penguino</h1>

      <div className={styles.headerActions}>
        <Link to="/new"><button>+ New Video</button></Link>
        <Link to="/cards"><button>🗂 View All Cards</button></Link>
      </div>

      <h2>Your Videos</h2>
      {videos.length === 0
        ? <p className={styles.emptyMsg}>No videos yet. Add one above.</p>
        : <div className={styles.grid}>
            {videos.map(v => (
              <VideoCard
                key={v.id} id={v.id} title={v.title}
                fromLang={v.from_lang} toLang={v.to_lang}
                onDelete={() => setPendingDelete(v)}
              />
            ))}
          </div>
      }

      <h2>Language Configurations</h2>
      <div className={styles.grid}>
        {configs.map(c => (
          <div key={c.id} className={styles.configCard}>
            <strong>{c.name}</strong>
            <p>{c.from_lang} → {c.to_lang}</p>
            <button className={styles.removeBtn} onClick={() => handleDeleteConfig(c.id)}>✕ Remove</button>
          </div>
        ))}
        {!showConfigForm ? (
          <div className={styles.addCard} onClick={() => setShowConfigForm(true)}>+ Add New</div>
        ) : (
          <div className={styles.configForm}>
            <input placeholder="Name (e.g. Spanish → English)" value={newName} onChange={e => setNewName(e.target.value)} />
            <input placeholder="From (e.g. Spanish)" value={newFromLang} onChange={e => setNewFromLang(e.target.value)} />
            <input placeholder="To (e.g. English)" value={newToLang} onChange={e => setNewToLang(e.target.value)} />
            {configError && <p className={styles.error}>{configError}</p>}
            <div className={styles.formActions}>
              <button onClick={handleAddConfig} disabled={configSaving}>{configSaving ? "Saving..." : "Save"}</button>
              <button onClick={() => { setShowConfigForm(false); setConfigError(null) }}>Cancel</button>
            </div>
          </div>
        )}
      </div>

      {pendingDelete && (
        <DeleteVideoModal
          title={pendingDelete.title}
          onConfirm={handleConfirmDelete}
          onCancel={() => setPendingDelete(null)}
        />
      )}
    </div>
  )
}