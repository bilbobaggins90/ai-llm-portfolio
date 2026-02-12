import Navbar from '@/components/Navbar'
import Hero from '@/components/Hero'
import ProjectsGrid from '@/components/ProjectsGrid'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <Hero />
      <ProjectsGrid />
      <Footer />
    </main>
  )
}
