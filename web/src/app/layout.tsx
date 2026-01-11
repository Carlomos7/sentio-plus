import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Sentio | AI-Powered Review Intelligence",
  description: "Transform thousands of customer reviews into actionable insights with AI. Chat with your reviews, discover patterns, and make data-driven decisions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${outfit.variable} font-[var(--font-outfit)] antialiased`}>
        {children}
      </body>
    </html>
  );
}
