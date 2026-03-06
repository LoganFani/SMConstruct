
export default function VideoPlayer() {

  const API = import.meta.env.VITE_API_BASE_URL;

  return (
    <div style={{ marginBottom: 16 }}>
      <video width="100%" controls>
        <source src={`${API}/video/stream/demo.mp4`} type="video/mp4" />
      </video>
    </div>
  )
}