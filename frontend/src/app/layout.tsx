import { Inter, Poppins } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next"

const inter = Inter({ subsets: ["latin"] });
const poppins = Poppins({ 
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  display: 'swap',
});

export const metadata = {
  title: "Notes2Anki - Turn your notes into flashcards",
  description: "Convert your study materials into Anki flashcards automatically",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${poppins.className} min-h-screen bg-background`}>
        {children}
        <Analytics />
      </body>
    </html>
  );
}