// In development: empty string (Vite proxy handles /api → localhost:8000)
// In production: set VITE_API_BASE_URL to the Render backend URL
export const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) ?? "";
