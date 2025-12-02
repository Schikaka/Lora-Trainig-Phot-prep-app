import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ImageProcessor from "./ImageProcessor";
import ErrorBoundary from "./ErrorBoundary";
import TestDownload from "./TestDownload";

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<ImageProcessor />} />
            <Route path="/test" element={<TestDownload />} />
          </Routes>
        </BrowserRouter>
      </div>
    </ErrorBoundary>
  );
}

export default App;
