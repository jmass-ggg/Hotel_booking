import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { getMe } from "../api/authApi";
import { clearAuth, getAccessToken } from "../api/http";

function ProtectedRoute({ children }) {
  const location = useLocation();
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    let mounted = true;

    const verifyUser = async () => {
      const token = getAccessToken();

      if (!token) {
        if (mounted) setStatus("unauthenticated");
        return;
      }

      try {
        await getMe();
        if (mounted) setStatus("authenticated");
      } catch (error) {
        clearAuth();
        if (mounted) setStatus("unauthenticated");
      }
    };

    verifyUser();

    return () => {
      mounted = false;
    };
  }, []);

  if (status === "checking") {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "grid",
          placeItems: "center",
          fontSize: "16px",
        }}
      >
        Loading...
      </div>
    );
  }

  if (status === "unauthenticated") {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

export default ProtectedRoute;