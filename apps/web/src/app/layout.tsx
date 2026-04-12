import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Sports Tracker",
  description: "Sistema de Acompanhamento Esportivo",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-slate-50 min-h-screen text-slate-900 flex`}>
        <Sidebar />
        <main className="ml-64 flex-1 p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
