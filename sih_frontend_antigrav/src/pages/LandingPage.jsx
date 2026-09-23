// src/pages/LandingPage.jsx
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import ProblemSection from '../components/ProblemSection';
import HowItWorks from '../components/HowItWorks';
import UseCases from '../components/UseCases';
import Testimonials from '../components/Testimonials';
import FinalCTA from '../components/FinalCTA';
import Footer from '../components/Footer';

export default function LandingPage() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <ProblemSection />
        <HowItWorks />
        <UseCases />
        <Testimonials />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
}
