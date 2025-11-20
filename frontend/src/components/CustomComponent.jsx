import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

// Lazy load heavy libraries
let Three = null
let Canvas = null
let useFrame = null
let OrbitControls = null
let Recharts = null
let d3 = null
let motion = null
let Icons = null

// Dynamic imports
const loadThree = async () => {
  if (!Three) {
    Three = await import('three')
    const fiber = await import('@react-three/fiber')
    const drei = await import('@react-three/drei')
    Canvas = fiber.Canvas
    useFrame = fiber.useFrame
    OrbitControls = drei.OrbitControls
  }
  return { Three: Three.default || Three, Canvas, useFrame, OrbitControls }
}

const loadRecharts = async () => {
  if (!Recharts) {
    Recharts = await import('recharts')
  }
  return Recharts
}

const loadD3 = async () => {
  if (!d3) {
    d3 = await import('d3')
  }
  return d3
}

const loadMotion = async () => {
  if (!motion) {
    motion = await import('framer-motion')
  }
  return motion
}

const loadIcons = async () => {
  if (!Icons) {
    Icons = await import('react-icons/fa')
  }
  return Icons
}

function CustomComponent({ data, onComplete, onTrackEvent }) {
  const [error, setError] = useState(null)
  const [ComponentToRender, setComponentToRender] = useState(null)
  const [loading, setLoading] = useState(true)
  const componentStartTime = useRef(Date.now())

  useEffect(() => {
    // Track component view
    if (onTrackEvent) {
      onTrackEvent('custom_component_view', { 
        hasCode: !!data.code,
        codeLength: data.code?.length || 0
      })
    }
  }, [])

  useEffect(() => {
    const loadComponent = async () => {
      if (data.code) {
        try {
          setLoading(true)
          
          // Load libraries based on what's needed
          const libs = {}
          
          if (data.code.includes('Three') || data.code.includes('Canvas') || data.code.includes('useFrame')) {
            libs.three = await loadThree()
          }
          if (data.code.includes('LineChart') || data.code.includes('BarChart') || data.code.includes('PieChart')) {
            libs.recharts = await loadRecharts()
          }
          if (data.code.includes('d3.')) {
            libs.d3 = await loadD3()
          }
          if (data.code.includes('motion.')) {
            libs.motion = await loadMotion()
          }
          if (data.code.includes('Fa') || data.code.includes('Icon')) {
            libs.icons = await loadIcons()
          }
          
          // Create a function that returns the React component
          const componentFunction = new Function(
            'React',
            'useState',
            'useEffect',
            'useRef',
            'useMemo',
            'useCallback',
            'ReactMarkdown',
            'remarkMath',
            'rehypeKatex',
            'onComplete',
            'trackEvent',
            'Three',
            'Canvas',
            'useFrame',
            'OrbitControls',
            'Recharts',
            'd3',
            'motion',
            'Icons',
            `
            const { createElement: h } = React;
            ${data.code}
            `
          )
          
          // Create a tracking wrapper
          const wrappedTrackEvent = (eventType, eventData) => {
            if (onTrackEvent) {
              onTrackEvent(eventType, { 
                ...eventData, 
                customComponent: true,
                timeInComponent: (Date.now() - componentStartTime.current) / 1000
              })
            }
          }
          
          // Execute the function to get the component
          const generatedComponent = componentFunction(
            React,
            useState,
            useEffect,
            useRef,
            useMemo,
            useCallback,
            ReactMarkdown,
            remarkMath,
            rehypeKatex,
            onComplete,
            wrappedTrackEvent,
            libs.three?.Three,
            libs.three?.Canvas,
            libs.three?.useFrame,
            libs.three?.OrbitControls,
            libs.recharts,
            libs.d3,
            libs.motion,
            libs.icons
          )
          
          setComponentToRender(() => generatedComponent)
          setLoading(false)
        } catch (err) {
          console.error('Error rendering custom component:', err)
          setError(err.message)
          setLoading(false)
        }
      }
    }
    
    loadComponent()
  }, [data.code, onComplete])

  if (error) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-error">Error Rendering Component</h2>
          <div className="alert alert-error">
            <span>{error}</span>
          </div>
          <details className="mt-4">
            <summary className="cursor-pointer font-semibold">View Code</summary>
            <pre className="text-xs bg-base-200 p-4 rounded overflow-auto mt-2">
              {data.code}
            </pre>
          </details>
        </div>
      </div>
    )
  }

  if (loading || !ComponentToRender) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body flex items-center justify-center min-h-[200px]">
          <span className="loading loading-spinner loading-lg"></span>
          <p className="text-sm text-gray-500 mt-4">Loading interactive component...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <ComponentToRender />
      </div>
    </div>
  )
}

export default CustomComponent