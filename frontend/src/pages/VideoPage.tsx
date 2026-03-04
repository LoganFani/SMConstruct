import { useEffect, useRef, useState } from "react"
import { useParams, useLocation } from "react-router-dom"
import type { TranscriptResponse, TranscriptSegment } from "../types/transcript"
import styles from "./VideoPage.module.css"

const API = "http://127.0.0.1:8000"

interface TranslateResponse {
  original_content: string
  translation: string
  context: string
}

interface SelectedWord {
  token: string
  context: string
  start: number
  end: number
}

interface CaptureState {
  framePath: string | null
  audioPath: string | null
  error: string | null
}

function getActiveSegId(segments: TranscriptSegment[], currentTime: number): number | null {
  const seg = segments.find(s => currentTime >= s.start && currentTime < s.end)
  return seg ? seg.id : null
}

export default function VideoPage() {
  const { videoId } = useParams()
  const location = useLocation()
  const { fromLang: stateFromLang, toLang: stateTolLang } = (location.state || {}) as any

  const videoRef = useRef<HTMLVideoElement>(null)
  const segRefs  = useRef<Map<number, HTMLParagraphElement>>(new Map())

  const [fromLang, setFromLang] = useState<string>(stateFromLang || "")
  const [toLang, setToLang]     = useState<string>(stateTolLang || "")

  const [transcript, setTranscript]               = useState<TranscriptResponse | null>(null)
  const [transcriptLoading, setTranscriptLoading] = useState(true)

  const [currentTime, setCurrentTime]   = useState(0)
  const [activeSegId, setActiveSegId]   = useState<number | null>(null)
  const [autoPause, setAutoPause]       = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)

  const [panelOpen, setPanelOpen]           = useState(false)
  const [selectedWord, setSelectedWord]     = useState<SelectedWord | null>(null)
  const [translation, setTranslation]       = useState<TranslateResponse | null>(null)
  const [translating, setTranslating]       = useState(false)
  const [translateError, setTranslateError] = useState<string | null>(null)

  const [capture, setCapture]     = useState<CaptureState>({ framePath: null, audioPath: null, error: null })
  const [capturing, setCapturing] = useState(false)
  const [cardSaving, setCardSaving] = useState(false)
  const [cardSaved, setCardSaved]   = useState(false)
  const [cardError, setCardError]   = useState<string | null>(null)

  useEffect(() => {
    if (!stateFromLang || !stateTolLang) {
      fetch(`${API}/api/video/${videoId}`)
        .then(r => r.json())
        .then(d => { setFromLang(d.from_lang); setToLang(d.to_lang) })
        .catch(console.error)
    }
  }, [videoId])

  useEffect(() => {
    fetch(`${API}/api/transcript/json/${videoId}`)
      .then(r => r.json())
      .then(d => { setTranscript(d); setTranscriptLoading(false) })
      .catch(err => { console.error(err); setTranscriptLoading(false) })
  }, [videoId])

  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    const onTimeUpdate = () => setCurrentTime(video.currentTime)
    video.addEventListener("timeupdate", onTimeUpdate)
    return () => video.removeEventListener("timeupdate", onTimeUpdate)
  }, [])

  useEffect(() => {
    if (!transcript) return
    const newId = getActiveSegId(transcript.segments, currentTime)
    setActiveSegId(prev => prev === newId ? prev : newId)
  }, [currentTime, transcript])

  useEffect(() => {
    if (!autoPause || !activeSegId || !transcript || !videoRef.current) return
    const idx = transcript.segments.findIndex(s => s.id === activeSegId)
    const nextSeg = transcript.segments[idx + 1]
    if (!nextSeg) return
    const video = videoRef.current
    const onTimeUpdate = () => {
      if (video.currentTime >= nextSeg.start) { video.pause(); video.currentTime = nextSeg.start }
    }
    video.addEventListener("timeupdate", onTimeUpdate)
    return () => video.removeEventListener("timeupdate", onTimeUpdate)
  }, [autoPause, activeSegId, transcript])

  useEffect(() => {
    if (activeSegId === null) return
    segRefs.current.get(activeSegId)?.scrollIntoView({ behavior: "smooth", block: "nearest" })
  }, [activeSegId])

  function handleClosePanel() {
    setPanelOpen(false); setSelectedWord(null); setTranslation(null)
    setTranslateError(null); setCapture({ framePath: null, audioPath: null, error: null })
    setCardSaved(false); setCardError(null)
  }

  async function handleTokenClick(token: string, context: string, start: number, end: number) {
    if (videoRef.current) videoRef.current.currentTime = start
    setPanelOpen(true)
    setSelectedWord({ token, context, start, end })
    setTranslation(null); setTranslateError(null); setTranslating(true)
    setCapture({ framePath: null, audioPath: null, error: null }); setCapturing(true)
    setCardSaved(false); setCardError(null)

    const [translateResult, captureResult] = await Promise.allSettled([
      fetch(`${API}/api/llm/translate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from_lang: fromLang, to_lang: toLang, user_input: token, context }),
      }).then(r => { if (!r.ok) throw new Error(`Translate failed: ${r.status}`); return r.json() }),

      Promise.all([
        fetch(`${API}/api/capture/frame`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ video_id: videoId, time_stamp: start }),
        }).then(r => { if (!r.ok) throw new Error("Frame capture failed"); return r.json() }),
        fetch(`${API}/api/capture/audio`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ video_id: videoId, start, end }),
        }).then(r => { if (!r.ok) throw new Error("Audio capture failed"); return r.json() }),
      ])
    ])

    if (translateResult.status === "fulfilled") setTranslation(translateResult.value)
    else setTranslateError(translateResult.reason?.message || "Translation failed")
    setTranslating(false)

    if (captureResult.status === "fulfilled") {
      const [frameData, audioData] = captureResult.value
      setCapture({ framePath: frameData.frame_path, audioPath: audioData.audio_path, error: null })
    } else {
      setCapture({ framePath: null, audioPath: null, error: captureResult.reason?.message || "Capture failed" })
    }
    setCapturing(false)
  }

  async function handleSaveCard() {
    if (!selectedWord || !translation) return
    setCardSaving(true); setCardError(null)
    try {
      const res = await fetch(`${API}/api/cards/`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: videoId, word: selectedWord.token,
          context: selectedWord.context, translation: translation.translation,
          frame_path: capture.framePath ?? null, audio_path: capture.audioPath ?? null,
        }),
      })
      if (!res.ok) throw new Error("Failed to save card")
      setCardSaved(true)
    } catch (err: any) {
      setCardError(err.message || "Error saving card")
    } finally {
      setCardSaving(false)
    }
  }

  const readyToSave = translation && !translating && !capturing

  return (
    <div className={styles.page}>

      <div className={styles.videoWrapper}>
        <video ref={videoRef} controls>
          <source src={`${API}/api/video/stream/${videoId}`} />
        </video>
      </div>

      <div className={styles.toolbar}>
        <span className={styles.toolbarLang}>{fromLang} → {toLang}</span>
        <button>Export Anki</button>
        <button onClick={() => setSettingsOpen(o => !o)}>
          {settingsOpen ? "✕ Settings" : "⚙ Settings"}
        </button>
      </div>

      {settingsOpen && (
        <div className={styles.settings}>
          <label>
            <input type="checkbox" checked={autoPause} onChange={e => setAutoPause(e.target.checked)} />
            Auto-pause after each sentence
          </label>
        </div>
      )}

      <div className={styles.main}>

        <div className={styles.transcript}>
          <h3>Transcript</h3>
          {transcriptLoading && <p className={styles.panelMuted}>Loading transcript...</p>}
          {transcript?.segments.map(seg => (
            <p
              key={seg.id}
              ref={el => { if (el) segRefs.current.set(seg.id, el) }}
              className={`${styles.segment} ${seg.id === activeSegId ? styles.active : ""}`}
            >
              {seg.tokens.map((token, i) => {
                const isSelected = selectedWord?.token === token && selectedWord?.context === seg.text
                return (
                  <span
                    key={i}
                    onClick={() => handleTokenClick(token, seg.text, seg.start, seg.end)}
                    className={`${styles.token} ${isSelected ? styles.selected : ""}`}
                  >
                    {token}
                  </span>
                )
              })}
            </p>
          ))}
        </div>

        {panelOpen && (
          <div className={styles.panel}>

            <div className={styles.panelHeader}>
              <h3>Word Info</h3>
              <button className={styles.closeBtn} onClick={handleClosePanel}>✕</button>
            </div>

            <div className={styles.panelSection}>
              <span className={styles.panelLabel}>Word</span>
              <span className={styles.panelWord}>{selectedWord?.token}</span>
            </div>

            <div className={styles.panelSection}>
              <span className={styles.panelLabel}>Context</span>
              <span className={styles.panelContext}>{selectedWord?.context}</span>
            </div>

            <div className={styles.panelSection}>
              <span className={styles.panelLabel}>Audio</span>
              {capturing && <span className={styles.panelMuted}>Capturing...</span>}
              {capture.error && <span className={styles.panelError}>{capture.error}</span>}
              {capture.audioPath && !capturing && (
                <audio
                  className={styles.audioPlayer}
                  controls
                  src={`${API}/api/capture/audio-file/${encodeURIComponent(capture.audioPath)}`}
                />
              )}
            </div>

            <div className={styles.panelSection}>
              <span className={styles.panelLabel}>Translation</span>
              {translating && <span className={styles.panelMuted}>Translating...</span>}
              {translateError && <span className={styles.panelError}>{translateError}</span>}
              {translation && !translating && <span className={styles.panelTranslation}>{translation.translation}</span>}
            </div>

            <div className={styles.panelSection}>
              <span className={styles.panelLabel}>Frame</span>
              {capturing && <span className={styles.panelMuted}>Capturing...</span>}
              {capture.error && <span className={styles.panelError}>{capture.error}</span>}
              {capture.framePath && !capturing && (
                <img
                  className={styles.frameImg}
                  src={`${API}/api/capture/frame-file/${encodeURIComponent(capture.framePath)}`}
                  alt="Captured frame"
                />
              )}
            </div>

            {readyToSave && (
              <div>
                <button className={styles.saveBtn} onClick={handleSaveCard} disabled={cardSaving || cardSaved}>
                  {cardSaving ? "Saving..." : cardSaved ? "✓ Card Saved" : "Save Card"}
                </button>
                {cardError && <p className={styles.saveError}>{cardError}</p>}
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  )
}