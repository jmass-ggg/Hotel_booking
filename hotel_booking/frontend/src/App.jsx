import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import Login from "./pages/Login";
import SellerProfile from "./pages/SellerProfile";
import MyHotel from "./pages/MyHotel";
import RoomTypes from "./pages/RoomTypes";
import Rooms from "./pages/Rooms";

function App() {
  return (
    <div className="app-root">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<SellerProfile />} />
          <Route path="/my-hotel" element={<MyHotel />} />
          <Route path="/room-types" element={<RoomTypes />} />
          <Route path="/rooms" element={<Rooms />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;