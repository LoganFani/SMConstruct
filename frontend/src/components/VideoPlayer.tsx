export default function VideoPlayer() {
  return (
    <div style={{ marginBottom: 16 }}>
      <video width="100%" controls>
        <source src="http://localhost:8000/api/video/stream/demo.mp4" />
      </video>
    </div>
  )
}