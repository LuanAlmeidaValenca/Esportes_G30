import { createClient } from "@libsql/client";
import dotenv from "dotenv";

dotenv.config();

const url = process.env.TURSO_DATABASE_URL || "file:./local.db";
const authToken = process.env.TURSO_AUTH_TOKEN;

if (!process.env.TURSO_DATABASE_URL) {
  console.warn("⚠️ TURSO_DATABASE_URL not set. Falling back to local SQLite at ./local.db");
}

export const db = createClient({
  url,
  authToken,
});
