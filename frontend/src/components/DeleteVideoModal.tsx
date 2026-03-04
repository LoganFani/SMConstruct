import { useState } from "react"
import styles from "./DeleteVideoModal.module.css"

interface Props {
  title: string
  onConfirm: (full: boolean) => void
  onCancel: () => void
}

export default function DeleteVideoModal({ title, onConfirm, onCancel }: Props) {
  const [deleteAll, setDeleteAll] = useState(false)

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h3>Delete "{title}"?</h3>
        <p>
          This will permanently delete the video file and its transcript.
          This action cannot be undone.
        </p>

        <label className={styles.checkLabel}>
          <input
            type="checkbox"
            checked={deleteAll}
            onChange={e => setDeleteAll(e.target.checked)}
          />
          Also delete all saved cards, frames, and audio clips
        </label>

        {deleteAll && (
          <p className={styles.warning}>
            ⚠ All cards, frame images, and audio clips for this video will be permanently deleted.
          </p>
        )}

        <div className={styles.actions}>
          <button onClick={onCancel}>Cancel</button>
          <button className={styles.deleteBtn} onClick={() => onConfirm(deleteAll)}>
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}