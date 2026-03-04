import { Routes, Route } from "react-router-dom"
import HomePage from "./pages/HomePage"
import CreateVideoPage from "./pages/CreateVideoPage"
import VideoPage from "./pages/VideoPage"
import CardsPage from "./pages/CardsPage"

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/new" element={<CreateVideoPage />} />
      <Route path="/video/:videoId" element={<VideoPage />} />
      <Route path="/cards" element={<CardsPage />} />
    </Routes>
  )
}