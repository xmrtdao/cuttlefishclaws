/**
 * Parse the Obsidian TrustGraph vault into a structured JSON file
 * that the React component can import instead of mock data.
 *
 * Usage: node scripts/parse-obsidian-graph.mjs
 * Output: src/lib/trustGraphData.json
 */

import { readFileSync, writeFileSync, readdirSync, statSync } from 'fs'
import { join, resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const VAULT = resolve(__dirname, '..', 'components', 'TrustGraph')
const OUT = resolve(__dirname, '..', 'src', 'lib', 'trustGraphData.json')

// ── Type color mapping (mirrors TrustGraphSection.tsx) ────────────────
const TYPE_COLOR = {
  governance: '#00ffcc',
  investor: '#ffaa00',
  system: '#aa88ff',
  unknown: '#ffbb33',
}

// ── Parse a single markdown file ──────────────────────────────────────
function parseNote(filePath) {
  const raw = readFileSync(filePath, 'utf-8')
  const lines = raw.split('\n')

  // Title: first # heading
  const titleMatch = raw.match(/^# (.+)$/m)
  const title = titleMatch ? titleMatch[1].trim() : ''

  // Metadata fields: **Role:**, **Type:**, **Status:**, **TrustGraph Score:**
  const roleMatch = raw.match(/\*\*Role:\*\*\s*(.+)/)
  const typeMatch = raw.match(/\*\*Type:\*\*\s*(.+)/)
  const statusMatch = raw.match(/\*\*Status:\*\*\s*(.+)/)
  const scoreMatch = raw.match(/\*\*TrustGraph Score:\*\*\s*(\d+)/)

  const role = roleMatch ? roleMatch[1].trim() : ''
  const type = typeMatch ? typeMatch[1].trim().toLowerCase() : 'unknown'
  const status = statusMatch ? statusMatch[1].trim().toLowerCase() : 'unknown'
  const trustScore = scoreMatch ? parseInt(scoreMatch[1], 10) : undefined

  // Description: first paragraph after the metadata block
  const descLines = []
  let inDesc = false
  for (const line of lines) {
    if (line.startsWith('## ')) break // stop at first section heading
    if (line.startsWith('# ') || line.startsWith('**')) continue
    if (line.trim() && !line.startsWith('|') && !line.startsWith('-') && !line.startsWith('[')) {
      if (inDesc || line.trim().length > 10) {
        inDesc = true
        descLines.push(line.trim())
      }
    }
  }
  const description = descLines.join(' ').slice(0, 300)

  // Files: ## Files section → bullet list items with `name — status`
  const files = []
  const filesSection = raw.match(/## Files\n([\s\S]*?)(?=\n## |$)/)
  if (filesSection) {
    const fileLines = filesSection[1].split('\n')
    for (const fl of fileLines) {
      const fMatch = fl.match(/^- \[\[(.+?)\]\]\s*—\s*(.+)/)
      if (fMatch) {
        files.push({ name: fMatch[1].trim(), status: fMatch[2].trim().toLowerCase() })
      }
    }
  }

  // Wiki links: [[Target]] or [[Target|Alias]]
  const links = [...raw.matchAll(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g)]
    .map(m => ({
      target: m[1].trim(),
      alias: m[2] ? m[2].trim() : null,
    }))
    // Don't count self-references
    .filter(l => l.target !== title)

  return { title, role, type, status, trustScore, description, files, links }
}

// ── Main ──────────────────────────────────────────────────────────────
function main() {
  const files = readdirSync(VAULT)
    .filter(f => f.endsWith('.md') && f !== 'Welcome.md')
    .sort()

  const notes = {}
  const edges = []
  const edgeSet = new Set()

  for (const f of files) {
    const fp = join(VAULT, f)
    if (!statSync(fp).isFile()) continue
    const note = parseNote(fp)
    const id = f.replace(/\.md$/, '').replace(/[ .]/g, '-').toLowerCase()
    notes[id] = { ...note, id, filename: f }
  }

  // Build edges from wiki links
  for (const [id, note] of Object.entries(notes)) {
    for (const link of note.links) {
      const targetKey = link.target.replace(/[ .]/g, '-').toLowerCase()
      if (notes[targetKey]) {
        const edgeKey = [id, targetKey].sort().join('::')
        if (!edgeSet.has(edgeKey)) {
          edgeSet.add(edgeKey)
          edges.push({
            source: id,
            target: targetKey,
            strength: 0.5 + Math.random() * 0.5,
          })
        }
      }
    }
  }

  // Build node list
  const nodes = Object.entries(notes).map(([id, note]) => ({
    id,
    label: note.title,
    role: note.role,
    type: note.type,
    status: note.status,
    trustScore: note.trustScore ?? 50,
    color: TYPE_COLOR[note.type] || TYPE_COLOR.unknown,
    description: note.description,
    files: note.files,
    linkCount: note.links.length,
  }))

  const output = { nodes, edges }

  writeFileSync(OUT, JSON.stringify(output, null, 2), 'utf-8')
  console.log(`✓ Wrote ${nodes.length} nodes and ${edges.length} edges to ${OUT}`)
}

main()
