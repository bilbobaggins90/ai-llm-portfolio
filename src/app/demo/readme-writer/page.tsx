'use client'

import { useState } from 'react'
import Link from 'next/link'
import { demoExamples, metrics, DemoExample } from '@/data/readme-demo-examples'

function MetricBar({ label, base, finetuned, unit = '', isPercent = false }: {
  label: string
  base: number
  finetuned: number
  unit?: string
  isPercent?: boolean
}) {
  const max = Math.max(base, finetuned)
  const improvement = base > 0 ? Math.round(((finetuned - base) / base) * 100) : 0

  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-gray-700">{label}</span>
        <span className="text-green-600 font-semibold">+{improvement}%</span>
      </div>
      <div className="flex gap-2 items-center">
        <div className="flex-1">
          <div className="h-5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gray-400 rounded-full transition-all duration-700"
              style={{ width: `${(base / max) * 100}%` }}
            />
          </div>
          <span className="text-xs text-gray-500 mt-0.5 block">{base}{unit}</span>
        </div>
        <div className="flex-1">
          <div className="h-5 bg-blue-50 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-700"
              style={{ width: `${(finetuned / max) * 100}%` }}
            />
          </div>
          <span className="text-xs text-blue-600 mt-0.5 block">{finetuned}{unit}</span>
        </div>
      </div>
    </div>
  )
}

function MarkdownPreview({ content }: { content: string }) {
  // Simple markdown to HTML for demo purposes
  const html = content
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="bg-gray-900 text-gray-100 p-3 rounded-lg text-sm overflow-x-auto my-3"><code>$2</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm">$1</code>')
    // Tables
    .replace(/\|(.+)\|\n\|[-| ]+\|\n((?:\|.+\|\n?)*)/g, (_match, header, body) => {
      const headers = header.split('|').map((h: string) => h.trim()).filter(Boolean)
      const rows = body.trim().split('\n').map((row: string) =>
        row.split('|').map((c: string) => c.trim()).filter(Boolean)
      )
      return `<div class="overflow-x-auto my-3"><table class="min-w-full text-sm border border-gray-200 rounded-lg"><thead><tr>${headers.map((h: string) => `<th class="px-3 py-2 bg-gray-50 text-left font-semibold border-b">${h}</th>`).join('')}</tr></thead><tbody>${rows.map((row: string[]) => `<tr>${row.map((c: string) => `<td class="px-3 py-2 border-b border-gray-100">${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`
    })
    // Headers
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-bold text-gray-800 mt-5 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold text-gray-900 mt-6 mb-3">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold text-gray-900 mb-3">$1</h1>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Links
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="text-blue-600 underline">$1</a>')
    // Bullet lists
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc text-gray-700">$1</li>')
    // Paragraphs (lines that aren't already HTML)
    .replace(/^(?!<[a-z/])(.+)$/gm, '<p class="text-gray-700 my-1.5">$1</p>')
    // Wrap consecutive <li> in <ul>
    .replace(/((?:<li[^>]*>.*?<\/li>\n?)+)/g, '<ul class="my-2 space-y-1">$1</ul>')

  return (
    <div
      className="prose prose-sm max-w-none"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

export default function ReadmeWriterDemo() {
  const [selectedExample, setSelectedExample] = useState<DemoExample>(demoExamples[0])
  const [activeTab, setActiveTab] = useState<'side-by-side' | 'input'>('side-by-side')
  const [showRaw, setShowRaw] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors">
              AI Portfolio
            </Link>
            <div className="flex items-center gap-4">
              <span className="hidden sm:inline text-sm text-gray-500">Code README Writer Demo</span>
              <Link
                href="/#projects"
                className="text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
              >
                Back to Projects
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
          <h1 className="text-3xl sm:text-4xl font-bold mb-3">Code README Writer</h1>
          <p className="text-blue-100 text-lg max-w-2xl">
            SFT fine-tuned TinyLlama-1.1B to generate README.md files from repository
            structure and code. See the before/after comparison below.
          </p>
          <div className="flex flex-wrap gap-2 mt-5">
            {['TinyLlama-1.1B', 'QLoRA', 'SFT', 'PEFT', 'TRL'].map(tag => (
              <span key={tag} className="px-3 py-1 bg-white/15 rounded-full text-sm font-medium">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Example selector */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Select an example repository:</h2>
          <div className="flex flex-wrap gap-3">
            {demoExamples.map(example => (
              <button
                key={example.id}
                onClick={() => setSelectedExample(example)}
                className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all ${
                  selectedExample.id === example.id
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-white text-gray-700 border border-gray-200 hover:border-blue-300 hover:text-blue-600'
                }`}
              >
                <span className="block">{example.name}</span>
                <span className={`text-xs ${
                  selectedExample.id === example.id ? 'text-blue-200' : 'text-gray-400'
                }`}>
                  {example.language}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab toggle */}
        <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
          <button
            onClick={() => setActiveTab('side-by-side')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'side-by-side'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Before / After
          </button>
          <button
            onClick={() => setActiveTab('input')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === 'input'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Model Input
          </button>
        </div>

        {activeTab === 'input' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h3 className="font-semibold text-gray-800">File Structure</h3>
              </div>
              <pre className="p-4 text-sm text-gray-700 overflow-x-auto whitespace-pre font-mono leading-relaxed">
                {selectedExample.fileTree}
              </pre>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h3 className="font-semibold text-gray-800">Key Code Files</h3>
              </div>
              <pre className="p-4 text-sm text-gray-700 overflow-x-auto whitespace-pre font-mono leading-relaxed max-h-[500px] overflow-y-auto">
                {selectedExample.codeSnippet}
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'side-by-side' && (
          <>
            {/* Raw/Rendered toggle */}
            <div className="flex justify-end mb-3">
              <button
                onClick={() => setShowRaw(!showRaw)}
                className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1.5"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                {showRaw ? 'Show Rendered' : 'Show Raw Markdown'}
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
              {/* Base model output */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="px-4 py-3 bg-red-50 border-b border-red-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
                    <h3 className="font-semibold text-red-900">Before</h3>
                  </div>
                  <span className="text-xs text-red-600 font-medium">Base TinyLlama-1.1B</span>
                </div>
                <div className="p-5 max-h-[600px] overflow-y-auto">
                  {showRaw ? (
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                      {selectedExample.baseOutput}
                    </pre>
                  ) : (
                    <MarkdownPreview content={selectedExample.baseOutput} />
                  )}
                </div>
              </div>

              {/* Fine-tuned output */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="px-4 py-3 bg-green-50 border-b border-green-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-green-500" />
                    <h3 className="font-semibold text-green-900">After</h3>
                  </div>
                  <span className="text-xs text-green-600 font-medium">SFT Fine-tuned + QLoRA</span>
                </div>
                <div className="p-5 max-h-[600px] overflow-y-auto">
                  {showRaw ? (
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                      {selectedExample.fineTunedOutput}
                    </pre>
                  ) : (
                    <MarkdownPreview content={selectedExample.fineTunedOutput} />
                  )}
                </div>
              </div>
            </div>
          </>
        )}

        {/* Metrics */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 mb-10">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Evaluation Metrics</h2>
          <p className="text-sm text-gray-500 mb-6">
            Averaged across 100 held-out test repositories.
            <span className="inline-flex items-center gap-3 ml-3">
              <span className="inline-flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-gray-400 inline-block" /> Base</span>
              <span className="inline-flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" /> Fine-tuned</span>
            </span>
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-10">
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">ROUGE Scores</h3>
              <MetricBar label="ROUGE-1" base={metrics.rouge1.base} finetuned={metrics.rouge1.finetuned} />
              <MetricBar label="ROUGE-2" base={metrics.rouge2.base} finetuned={metrics.rouge2.finetuned} />
              <MetricBar label="ROUGE-L" base={metrics.rougeL.base} finetuned={metrics.rougeL.finetuned} />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Structural Quality</h3>
              <MetricBar label="Avg Headings" base={metrics.avgHeadings.base} finetuned={metrics.avgHeadings.finetuned} />
              <MetricBar label="Has Install Section" base={metrics.hasInstall.base} finetuned={metrics.hasInstall.finetuned} unit="%" />
              <MetricBar label="Has Usage Section" base={metrics.hasUsage.base} finetuned={metrics.hasUsage.finetuned} unit="%" />
              <MetricBar label="Avg Code Blocks" base={metrics.avgCodeBlocks.base} finetuned={metrics.avgCodeBlocks.finetuned} />
            </div>
          </div>
        </div>

        {/* Training details */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 mb-10">
          <h2 className="text-xl font-bold text-gray-900 mb-5">Training Details</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Base Model', value: 'TinyLlama-1.1B' },
              { label: 'Method', value: 'SFT + QLoRA (4-bit)' },
              { label: 'LoRA Rank', value: '16 (alpha 32)' },
              { label: 'Training Data', value: '5K+ repo-README pairs' },
              { label: 'Epochs', value: '3' },
              { label: 'Learning Rate', value: '2e-4 (cosine)' },
              { label: 'Effective Batch', value: '16' },
              { label: 'Hardware', value: 'Single T4 GPU' },
              { label: 'Trainable Params', value: '~8M (0.7%)' },
              { label: 'Adapter Size', value: '~20MB' },
              { label: 'Max Seq Length', value: '2048 tokens' },
              { label: 'Languages', value: '10 (Python, JS, Go...)' },
            ].map(item => (
              <div key={item.label} className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 font-medium uppercase tracking-wider">{item.label}</div>
                <div className="text-sm font-semibold text-gray-900 mt-1">{item.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Architecture diagram */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 mb-10">
          <h2 className="text-xl font-bold text-gray-900 mb-5">Architecture</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-50 rounded-lg p-5">
              <h3 className="font-semibold text-gray-800 mb-3">Training Pipeline</h3>
              <div className="space-y-3">
                {[
                  { step: '1', label: 'Data Collection', desc: '5K+ GitHub repos across 10 languages' },
                  { step: '2', label: 'Preprocessing', desc: 'Extract file trees + key source files' },
                  { step: '3', label: 'QLoRA Setup', desc: '4-bit NF4 quantization, rank-16 adapters' },
                  { step: '4', label: 'SFT Training', desc: 'Completion-only loss on README output' },
                  { step: '5', label: 'Evaluation', desc: 'ROUGE + structural metrics on test set' },
                ].map(item => (
                  <div key={item.step} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-600 text-white text-sm font-bold flex items-center justify-center">
                      {item.step}
                    </span>
                    <div>
                      <div className="font-medium text-gray-800 text-sm">{item.label}</div>
                      <div className="text-xs text-gray-500">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-5">
              <h3 className="font-semibold text-gray-800 mb-3">Inference Pipeline</h3>
              <div className="space-y-3">
                {[
                  { step: '1', label: 'Scan Repository', desc: 'Local path or GitHub URL' },
                  { step: '2', label: 'Extract Structure', desc: 'File tree + top-level source files' },
                  { step: '3', label: 'Build Prompt', desc: 'System/user/assistant chat template' },
                  { step: '4', label: 'Generate', desc: 'TinyLlama + LoRA adapter inference' },
                  { step: '5', label: 'Output README', desc: 'Well-structured markdown document' },
                ].map(item => (
                  <div key={item.step} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-7 h-7 rounded-full bg-indigo-600 text-white text-sm font-bold flex items-center justify-center">
                      {item.step}
                    </span>
                    <div>
                      <div className="font-medium text-gray-800 text-sm">{item.label}</div>
                      <div className="text-xs text-gray-500">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="text-center py-8">
          <Link
            href="/#projects"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            <svg className="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
            Back to all projects
          </Link>
        </div>
      </div>
    </div>
  )
}
