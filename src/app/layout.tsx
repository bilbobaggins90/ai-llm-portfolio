import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI/LLM Portfolio - Developer & Researcher',
  description: 'Portfolio showcasing AI and LLM projects, machine learning applications, and cutting-edge AI research.',
  keywords: ['AI', 'LLM', 'Machine Learning', 'GPT', 'LangChain', 'Portfolio'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
