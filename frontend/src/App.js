import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ImageProcessor from "./ImageProcessor";
import ErrorBoundary from "./ErrorBoundary";
import TestDownload from "./TestDownload";
import FilesBrowser from "./FilesBrowser";

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<FilesBrowser />} />
            <Route path="/upload" element={<ImageProcessor />} />
            <Route path="/test" element={<TestDownload />} />
          </Routes>
        </BrowserRouter>
      </div>
    </ErrorBoundary>
  );
}

export default App;
