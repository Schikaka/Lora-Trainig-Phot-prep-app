import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ImageProcessor from "./ImageProcessor";
import ErrorBoundary from "./ErrorBoundary";

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<ImageProcessor />} />
          </Routes>
        </BrowserRouter>
      </div>
    </ErrorBoundary>
  );
}

export default App;
