import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard/Dashboard'
import ErrorBoundary from './components/Common/ErrorBoundary'
import './App.css'

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">
                  Clean Energy Predictor
                </h1>
              </div>
              <nav className="hidden md:flex space-x-8">
                <a href="#dashboard" className="text-gray-500 hover:text-gray-900">
                  Dashboard
                </a>
                <a href="#about" className="text-gray-500 hover:text-gray-900">
                  About
                </a>
              </nav>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </main>

        <footer className="bg-white border-t mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-500">
              <p>
                © {new Date().getFullYear()} Clean Energy Predictor · Built for the Code with Kiro Hackathon
              </p>
              <p className="text-sm text-gray-400 mt-1">
                Forecast the cleanest hours for electricity use — save CO₂, plant trees 🌱🌳, and power up responsibly.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  )
}

export default App