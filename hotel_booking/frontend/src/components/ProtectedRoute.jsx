import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { getMe } from "../api/authApi";
import { clearAuth, getAccessToken } from "../api/http";

function ProtectedRoute({ children, allowedRoles = [] }) {
  const location = useLocation();
  const [status, setStatus] = useState("checking");
  const [user, setUser] = useState(null);

  useEffect(() => {
    let mounted = true;

    const verifyUser = async () => {
      const token = getAccessToken();

      if (!token) {
        if (mounted) setStatus("unauthenticated");
        return;
      }

      try {
        const me = await getMe();

        if (!mounted) return;

        localStorage.setItem("me", JSON.stringify(me));
        setUser(me);

        if (allowedRoles.length > 0 && !allowedRoles.includes(me?.role)) {
          setStatus("forbidden");
          return;
        }

        setStatus("authenticated");
      } catch (error) {
        clearAuth();
        if (mounted) setStatus("unauthenticated");
      }
    };

    verifyUser();

    return () => {
      mounted = false;
    };
  }, [allowedRoles]);

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

  if (status === "forbidden") {
    return <Navigate to="/profile" replace />;
  }

  return children;
}

export default ProtectedRoute;