import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ImageProcessor from "./ImageProcessor";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ImageProcessor />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
