import { useEffect, useRef, useState } from "react"
import { useParams, useLocation } from "react-router-dom"
import type { TranscriptResponse, TranscriptSegment } from "../types/transcript"
import CardItem, { type Card } from "../components/CardItem"
import ExportAnkiModal from "../components/ExportAnkiModal"
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

interface TokenRange {
  segId: number
  fromIdx: number
  toIdx: number
}

interface FloatPos {
  x: number
  y: number
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

  const [activeTab, setActiveTab] = useState<"transcript" | "cards">("transcript")
  const [cards, setCards]         = useState<Card[]>([])
  const [cardsLoading, setCardsLoading] = useState(false)

  const [panelOpen, setPanelOpen]           = useState(false)
  const [selectedWord, setSelectedWord]     = useState<SelectedWord | null>(null)
  const [translation, setTranslation]       = useState<TranslateResponse | null>(null)
  const [translating, setTranslating]       = useState(false)
  const [translateError, setTranslateError] = useState<string | null>(null)

  const [capture, setCapture]       = useState<CaptureState>({ framePath: null, audioPath: null, error: null })
  const [capturing, setCapturing]   = useState(false)
  const [cardSaving, setCardSaving] = useState(false)
  const [cardSaved, setCardSaved]   = useState(false)
  const [cardError, setCardError]   = useState<string | null>(null)

  const [ankiOpen, setAnkiOpen] = useState(false)

  const [anchorIdx, setAnchorIdx]   = useState<{ segId: number; idx: number } | null>(null)
  const [tokenRange, setTokenRange] = useState<TokenRange | null>(null)
  const [floatPos, setFloatPos]     = useState<FloatPos | null>(null)

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

  // Load cards when tab is switched to cards
  useEffect(() => {
    if (activeTab !== "cards") return
    setCardsLoading(true)
    fetch(`${API}/api/cards/${videoId}`)
      .then(r => r.json())
      .then(d => { setCards(d); setCardsLoading(false) })
      .catch(err => { console.error(err); setCardsLoading(false) })
  }, [activeTab, videoId])

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

  function clearSelection() {
    setAnchorIdx(null); setTokenRange(null); setFloatPos(null)
  }

  function handleClosePanel() {
    setPanelOpen(false); setSelectedWord(null); setTranslation(null)
    setTranslateError(null); setCapture({ framePath: null, audioPath: null, error: null })
    setCardSaved(false); setCardError(null); clearSelection()
  }

  async function triggerTranslate(phrase: string, context: string, start: number, end: number) {
    if (videoRef.current) videoRef.current.currentTime = start
    setSelectedWord({ token: phrase, context, start, end })
    setPanelOpen(true)
    setTranslation(null); setTranslateError(null); setTranslating(true)
    setCapture({ framePath: null, audioPath: null, error: null }); setCapturing(true)
    setCardSaved(false); setCardError(null)

    const [translateResult, captureResult] = await Promise.allSettled([
      fetch(`${API}/api/llm/translate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from_lang: fromLang, to_lang: toLang, user_input: phrase, context }),
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

  function handleTokenClick(e: React.MouseEvent, token: string, tokenIdx: number, seg: TranscriptSegment) {
    if (e.shiftKey && anchorIdx && anchorIdx.segId === seg.id) {
      const from = Math.min(anchorIdx.idx, tokenIdx)
      const to   = Math.max(anchorIdx.idx, tokenIdx)
      setTokenRange({ segId: seg.id, fromIdx: from, toIdx: to })
    } else {
      clearSelection(); handleClosePanel()
      setAnchorIdx({ segId: seg.id, idx: tokenIdx })
      setTokenRange({ segId: seg.id, fromIdx: tokenIdx, toIdx: tokenIdx })
    }
    setFloatPos({ x: e.clientX, y: e.clientY - 44 })
  }

  function handleFloatTranslate() {
    if (!tokenRange || !transcript) return
    const seg = transcript.segments.find(s => s.id === tokenRange.segId)
    if (!seg) return
    const phrase = seg.tokens.slice(tokenRange.fromIdx, tokenRange.toIdx + 1).join(" ")
    clearSelection()
    triggerTranslate(phrase, seg.text, seg.start, seg.end)
  }

  function isTokenSelected(segId: number, tokenIdx: number): boolean {
    if (!tokenRange && anchorIdx?.segId === segId && anchorIdx?.idx === tokenIdx) return true
    if (tokenRange?.segId === segId && tokenIdx >= tokenRange.fromIdx && tokenIdx <= tokenRange.toIdx) return true
    if (!tokenRange && selectedWord && transcript) {
      const seg = transcript.segments.find(s => s.id === segId)
      if (seg) return seg.tokens[tokenIdx] === selectedWord.token && seg.text === selectedWord.context
    }
    return false
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
      const newCard: Card = await res.json()
      setCards(prev => [newCard, ...prev])
      setCardSaved(true)
    } catch (err: any) {
      setCardError(err.message || "Error saving card")
    } finally {
      setCardSaving(false)
    }
  }

  async function handleDeleteCard(cardId: number) {
    await fetch(`${API}/api/cards/${cardId}`, { method: "DELETE" })
    setCards(prev => prev.filter(c => c.id !== cardId))
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
        <button onClick={() => setAnkiOpen(true)}>Export Anki</button>
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

      {/* Tabs */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === "transcript" ? styles.activeTab : ""}`}
          onClick={() => setActiveTab("transcript")}
        >
          Transcript
        </button>
        <button
          className={`${styles.tab} ${activeTab === "cards" ? styles.activeTab : ""}`}
          onClick={() => setActiveTab("cards")}
        >
          Cards {cards.length > 0 && `(${cards.length})`}
        </button>
      </div>

      <div className={styles.main}>

        {activeTab === "transcript" ? (
          <>
            <div className={styles.transcript}>
              {transcriptLoading && <p className={styles.panelMuted}>Loading transcript...</p>}
              {transcript?.segments.map(seg => (
                <p
                  key={seg.id}
                  ref={el => { if (el) segRefs.current.set(seg.id, el) }}
                  className={`${styles.segment} ${seg.id === activeSegId ? styles.active : ""}`}
                >
                  {seg.tokens.map((token, i) => (
                    <span
                      key={i}
                      onClick={e => handleTokenClick(e, token, i, seg)}
                      className={`${styles.token} ${isTokenSelected(seg.id, i) ? styles.selected : ""}`}
                    >
                      {token}
                    </span>
                  ))}
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
                    <audio className={styles.audioPlayer} controls
                      src={`${API}/api/capture/audio-file/${encodeURIComponent(capture.audioPath)}`} />
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
                    <img className={styles.frameImg}
                      src={`${API}/api/capture/frame-file/${encodeURIComponent(capture.framePath)}`}
                      alt="Captured frame" />
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
          </>
        ) : (
          <div className={cardsLoading ? styles.cardsEmpty : styles.cardsGrid}>
            {cardsLoading && <p>Loading cards...</p>}
            {!cardsLoading && cards.length === 0 && <p>No cards saved for this video yet.</p>}
            {!cardsLoading && cards.map(card => (
              <CardItem key={card.id} card={card} onDelete={handleDeleteCard} />
            ))}
          </div>
        )}
      </div>

      {ankiOpen && (
        <ExportAnkiModal
          videoId={videoId}
          defaultDeckName={`${fromLang} - ${toLang}`}
          onClose={() => setAnkiOpen(false)}
        />
      )}

      {floatPos && tokenRange && (
        <button
          className={styles.floatBtn}
          style={{ left: floatPos.x, top: floatPos.y }}
          onClick={handleFloatTranslate}
        >
          Translate
        </button>
      )}
    </div>
  )
}