import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import Login from "./pages/Login";
import SellerProfile from "./pages/SellerProfile";
import MyHotel from "./pages/MyHotel";
import RoomTypes from "./pages/RoomTypes";
import Rooms from "./pages/Rooms";
import SellerRoles from "./pages/SellerRoles";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <div className="app-root">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <SellerProfile />
              </ProtectedRoute>
            }
          />

          <Route
            path="/my-hotel"
            element={
              <ProtectedRoute>
                <MyHotel />
              </ProtectedRoute>
            }
          />

          <Route
            path="/room-types"
            element={
              <ProtectedRoute>
                <RoomTypes />
              </ProtectedRoute>
            }
          />

          <Route
            path="/rooms"
            element={
              <ProtectedRoute>
                <Rooms />
              </ProtectedRoute>
            }
          />

          <Route
            path="/seller-staff"
            element={
              <ProtectedRoute allowedRoles={["SELLER"]}>
                <SellerRoles />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;