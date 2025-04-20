// src/lib/constants.ts
export const MAX_FILES = Number(process.env.NEXT_PUBLIC_MAX_FILES || 5);
export const MAX_FILE_SIZE = Number(process.env.NEXT_PUBLIC_MAX_FILE_SIZE || 10) * 1024 * 1024; // Convert MB to bytes
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
export const FEEDBACK_FORM_URL = process.env.NEXT_PUBLIC_FEEDBACK_FORM_URL || "https://forms.gle/Qfd6GjMu9huMw6Ts9"