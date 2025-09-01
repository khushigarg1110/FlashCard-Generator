import React, { useState } from "react";
import "./App.css"; // import CSS

function App() {
  const [file, setFile] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please upload a PDF");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await fetch("http://localhost:5000/generate-flashcards", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setFlashcards(data.flashcards || []);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Flashcard Generator</h1>

      <div className="upload-section">
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Generating..." : "Upload & Generate"}
        </button>
      </div>

      <div className="flashcards-container">
        {flashcards.length > 0 ? (
          flashcards.map((card, i) => (
            <div key={i} className="flashcard">
              <div className="flashcard-inner">
                <div className="flashcard-front">
                  <p>{card.question}</p>
                </div>
                <div className="flashcard-back">
                  <p>{card.answer}</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          !loading && <p className="no-flashcards">No flashcards yet.</p>
        )}
      </div>
    </div>
  );
}

export default App;
