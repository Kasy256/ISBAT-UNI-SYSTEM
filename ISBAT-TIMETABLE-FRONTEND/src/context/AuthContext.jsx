import { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "@/lib/api";

const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Check if user is authenticated on mount
    return authAPI.isAuthenticated();
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verify authentication status on mount
    setIsAuthenticated(authAPI.isAuthenticated());
    setIsLoading(false);

    // Listen for logout events (e.g., when API returns 401)
    const handleLogout = () => {
      setIsAuthenticated(false);
    };

    window.addEventListener('auth:logout', handleLogout);

    return () => {
      window.removeEventListener('auth:logout', handleLogout);
    };
  }, []);

  const login = (token) => {
    if (token) {
      // The login API already sets the token in localStorage
      // Just update the authentication state
      setIsAuthenticated(true);
    }
  };

  const logout = () => {
    authAPI.logout();
    setIsAuthenticated(false);
  };

  const checkAuth = () => {
    const authenticated = authAPI.isAuthenticated();
    setIsAuthenticated(authenticated);
    return authenticated;
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        login,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

