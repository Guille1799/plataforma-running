import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
// import { CoachChat } from "./components/coach-chat";
import { Toaster } from "sonner";

export const metadata: Metadata = {
  title: "RunCoach AI",
  description: "Tu plataforma inteligente de running",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="dark">
      <body>
        <Providers>
          {children}
          {/* <CoachChat /> */}
          <Toaster position="top-right" richColors />
        </Providers>
      </body>
    </html>
  );
}