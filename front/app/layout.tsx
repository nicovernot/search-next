import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { SearchProvider } from "./context/SearchContext";
import { I18nProvider } from "./context/I18nContext";
import { ThemeProvider } from "./components/ThemeProvider";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });
const outfit = Outfit({ variable: "--font-outfit", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OpenEdition Search",
  description: "Recherche dans les publications OpenEdition",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={`${inter.variable} ${outfit.variable} font-sans antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <I18nProvider>
            <SearchProvider>{children}</SearchProvider>
          </I18nProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
