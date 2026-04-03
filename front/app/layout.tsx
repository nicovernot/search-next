import type { Metadata } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SearchProvider } from "./context/SearchContext";
import { I18nProvider } from "./context/I18nContext";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OpenEdition Search",
  description: "Recherche dans les publications OpenEdition",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className={`${inter.variable} ${geistMono.variable} antialiased`}>
        <I18nProvider>
          <SearchProvider>{children}</SearchProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
