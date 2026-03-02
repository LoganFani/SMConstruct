import { useState } from "react"
import VideoPlayer from "../components/VideoPlayer"
import TranscriptPanel from "../components/TranscriptPannel"
import TranslationPanel from "../components/TranslationPannel"

export default function VideoPage() {
  const [selectedText, setSelectedText] = useState<string | null>(null)

  return (
    <div style={{ padding: 24, display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24 }}>
      
      {/* Left Column */}
      <div>
        <VideoPlayer />
        <TranscriptPanel onSelect={setSelectedText} />
      </div>

      {/* Right Column */}
      <TranslationPanel selectedText={selectedText} />
    </div>
  )
}