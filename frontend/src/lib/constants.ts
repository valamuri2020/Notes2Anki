// src/lib/constants.ts
export const MAX_FILES = Number(process.env.NEXT_PUBLIC_MAX_FILES || 5);
export const MAX_FILE_SIZE = Number(process.env.NEXT_PUBLIC_MAX_FILE_SIZE || 10) * 1024 * 1024; // Convert MB to bytes
