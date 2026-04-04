import { z } from "zod";

export const emailSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
});

export const codeSchema = z.object({
  code: z.string().length(6, "Code must be exactly 6 characters"),
});

export const urlSchema = z.object({
  url: z.string().url("Please enter a valid URL (e.g., https://example.com)"),
});

export type EmailInput = z.infer<typeof emailSchema>;
export type CodeInput = z.infer<typeof codeSchema>;
export type UrlInput = z.infer<typeof urlSchema>;
