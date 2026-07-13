/**
 * build-collective-graph.mjs
 *
 * Unifies the XMRT-DAO Obsidian vault and the Cuttlefish Labs TrustGraph vault
 * into a single collective graph. XMRT-DAO ecosystem forms the innermost
 * concentric ring (galaxy core). Cuttlefish Labs governance layer orbits
 * around it.
 *
 * Output: src/lib/collectiveGraphData.json
 *
 * Usage: node scripts/build-collective-graph.mjs
 */

import { readFileSync, writeFileSync, readdirSync, statSync } from 'fs'
import { join, resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const XMRT_VAULT = resolve(__dirname, '..', '..', 'xmrt-dao')
const CF_VAULT = resolve(__dirname, '..', 'components', 'TrustGraph')
const OUT = resolve(__dirname, '..', 'src', 'lib', 'collectiveGraphData.json')

// ── Ring assignment ──────────────────────────────────────────────
// Ring 0 (innermost): XMRT-DAO ecosystem core
// Ring 1: XMRT-DAO infrastructure & applications
// Ring 2: XMRT-DAO agents
// Ring 3 (outermost): Cuttlefish Labs governance layer
const RING_ASSIGNMENTS = {
  // XMRT-DAO core (ring 0)
  'XMRT DAO': 0, 'Relay Server': 0, 'Index': 0,
  // XMRT-DAO infrastructure (ring 1)
  'Postgres Database': 1, 'Local Supabase': 1, 'Cloudflare Tunnel': 1,
  'Cloudflare Workers': 1, 'Cloudflare Accounts': 1, 'Mesh Network': 1,
  'Ollama': 1, 'Supervisor': 1, 'Cron Engine': 1, 'Relay Dashboard': 1,
  'Watchdog': 1, 'Fleet Heartbeat': 1, 'Knowledge Backfill': 1,
  // XMRT-DAO applications (ring 1)
  'Suite Dashboard': 1, 'CuttlefishClaws': 1, 'CashDApp': 1, 'HottieHouse': 1,
  '31Harbor Agency Dashboards': 1, 'Zero-Claw': 1, 'Party Favor Photo': 1,
  'TempCashDapp': 1, '31Harbor': 1, '31Harbor Scraper': 1,
  // XMRT-DAO email/campaign (ring 1)
  'Resend Email': 1, 'Inbound Email': 1, 'Campaign Schedulers': 1,
  // XMRT-DAO database (ring 1)
  'app Schema': 1, 'public Schema': 1,
  // XMRT-DAO API docs (ring 1)
  'Relay API': 1, 'Relay API - CashDApp Routes': 1, 'Relay API - CuttlefishClaws Routes': 1,
  'Relay API - Fleet Routes': 1, 'Relay API - Inbox Routes': 1, 'Relay API - Static Routes': 1,
  'Relay API - Suite Routes': 1, 'Relay API - System Routes': 1,
  // XMRT-DAO governance/system (ring 1)
  'DAO Governance': 1, 'Trust Graph': 1, 'Agent Authorization': 1,
  'XMRT University': 1, 'Revenue Model': 1, 'Conversation Memory': 1,
  // XMRT-DAO agents (ring 2)
  'Vex Agent': 2, 'Alice Agent': 2, 'Eliza Agent': 2, 'Hermes Agent': 2,
  'CuttlefishClaws Agents': 2, 'Executive Persona Agents': 2, 'Fleet Chat': 2,
  'Isabella Rodriguez': 2,
  // People (ring 2)
  'Joe': 2, 'David': 2,
  // Organizations (ring 2)
  'Cuttlefish Labs': 2,
  // Cuttlefish Labs governance layer (ring 3)
  'Trib': 3, 'Arch': 3, 'Builder Agent': 3, 'Sovereign Agent': 3,
  'TrustGraph': 3, 'DAO Gov': 3, 'GlobalCommunicator': 3, 'Navigator': 3,
  'Agent': 3, 'CAC': 3, 'CONSTITUTION': 3, 'SOUL': 3,
  'AgentBillOfRights.sol': 3, 'CACToken.sol': 3, 'CACTransferProtocol.sol': 3,
  'Canonical Reconciliation': 3, 'Contracts': 3, 'FeeRouter.sol': 3,
  'FounderShare.sol': 3, 'GovernanceModule.sol': 3, 'Legislation Tracker': 3,
  'Product Thesis': 3, 'TributaryProperty.sol': 3, 'TrustGraph.sol': 3,
  'TrustGraph': 3, 'Two Stack Architecture': 3,
}

const RING_COLORS = {
  0: '#ff6600', // core — orange (XMRT DAO)
  1: '#44aaff', // infrastructure/apps — blue
  2: '#44ffaa', // agents/people — green
  3: '#aa88ff', // governance — purple (Cuttlefish Labs)
}

const RING_LABELS = {
  0: 'XMRT DAO CORE',
  1: 'INFRASTRUCTURE & APPLICATIONS',
  2: 'AGENTS & PEOPLE',
  3: 'CUTTLEFISH GOVERNANCE',
}

// ── Parse XMRT-DAO vault ──────────────────────────────────────────
function parseXmrtVault() {
  const vault = XMRT_VAULT
  const files = readdirSync(vault).filter(f => f.endsWith('.md'))
  const nodes = []
  const edges = []
  const nodeSet = new Set()
  const linkMap = {}

  for (const f of files) {
    const name = f.replace(/\.md$/, '')
    const content = readFileSync(join(vault, f), 'utf8')
    const linkRegex = /\[\[([^\]]+)\]\]/g
    let match
    const links = []
    while ((match = linkRegex.exec(content)) !== null) {
      links.push(match[1])
    }
    linkMap[name] = links

    const typeMatch = content.match(/\*\*Type:\*\* (.+)/)
    const typeVal = typeMatch ? typeMatch[1].trim() : ''
    let category = 'other'
    if (typeVal.startsWith('Vite React SPA') || typeVal.startsWith('Next.js')) category = 'spa'
    else if (typeVal === 'Express.js server' || typeVal === 'Express.js route documentation') category = 'backend'
    else if (typeVal.startsWith('AI agent') || typeVal === '7 specialized AI agents') category = 'agent'
    else if (typeVal.includes('Cloudflare') || typeVal === 'libp2p gossipsub' || typeVal === 'Local LLM server' || typeVal === 'Local Supabase replacement' || typeVal === 'PostgreSQL') category = 'infra'
    else if (typeVal === 'Trust-level access control' || typeVal === 'Per-session conversation history' || typeVal === 'Agent self-registration & liveness' || typeVal === 'Service manager' || typeVal === 'Relay health monitor' || typeVal === 'Suite memory pipeline' || typeVal === 'Local cron executor' || typeVal === 'Inline HTML dashboard' || typeVal === 'AI agent conversation system') category = 'system'
    else if (typeVal === 'Decentralized mining pool') category = 'mining'
    else if (typeVal === 'Agent certification system') category = 'cert'
    else if (typeVal === 'Real estate contact scraper' || typeVal === 'Email campaign automation' || typeVal === 'Photo booth business' || typeVal === 'Email receiving & forwarding system' || typeVal === 'Email sending service') category = 'email'
    else if (typeVal === 'PostgreSQL schema' || content.includes('**Schema:**')) category = 'db'
    else if (typeVal === 'DAO governance system' || typeVal === 'Trust & reputation system' || typeVal === 'DAO revenue model' || typeVal === 'DAO organization system' || typeVal === 'Software development organization' || typeVal === 'Real estate property listing system') category = 'system'
    else if (typeVal === 'Human developer' || typeVal === 'Human developer founder') category = 'people'

    const ring = RING_ASSIGNMENTS[name] !== undefined ? RING_ASSIGNMENTS[name] : 1
    const descMatch = content.match(/^# .+\n+(.+)/m)
    const description = descMatch ? descMatch[1].trim() : ''

    nodes.push({
      id: name,
      label: name,
      category,
      ring,
      source: 'xmrt-vault',
      description,
      color: RING_COLORS[ring] || '#6b6b80',
    })
    nodeSet.add(name)
  }

  // Wiki-link edges
  for (const n of nodes) {
    for (const target of (linkMap[n.id] || [])) {
      if (nodeSet.has(target)) {
        edges.push({ source: n.id, target, type: 'wiki-link' })
      }
    }
  }

  // Cross-link: XMRT DAO connects to Cuttlefish Labs governance agents
  const crossLinks = [
    ['XMRT DAO', 'Trib'],
    ['XMRT DAO', 'DAO Gov'],
    ['Trust Graph', 'TrustGraph'],
    ['CuttlefishClaws Agents', 'Trib'],
    ['CuttlefishClaws Agents', 'Arch'],
    ['Cuttlefish Labs', 'Navigator'],
    ['David', 'Navigator'],
    ['DAO Governance', 'DAO Gov'],
    ['Agent Authorization', 'CAC'],
  ]
  for (const [src, tgt] of crossLinks) {
    edges.push({ source: src, target: tgt, type: 'cross-vault' })
  }

  return { nodes, edges }
}

// ── Parse Cuttlefish TrustGraph vault ────────────────────────────
function parseCfVault() {
  const vault = CF_VAULT
  const files = readdirSync(vault).filter(f => f.endsWith('.md') && f !== 'Welcome.md')
  const nodes = []
  const edges = []
  const nodeSet = new Set()
  const linkMap = {}

  for (const f of files) {
    const name = f.replace(/\.md$/, '')
    const content = readFileSync(join(vault, f), 'utf8')

    const titleMatch = content.match(/^# (.+)$/m)
    const title = titleMatch ? titleMatch[1].trim() : name

    const roleMatch = content.match(/\*\*Role:\*\*\s*(.+)/)
    const typeMatch = content.match(/\*\*Type:\*\*\s*(.+)/)
    const scoreMatch = content.match(/\*\*TrustGraph Score:\*\*\s*(\d+)/)
    const statusMatch = content.match(/\*\*Status:\*\*\s*(.+)/)

    const role = roleMatch ? roleMatch[1].trim() : ''
    const type = typeMatch ? typeMatch[1].trim().toLowerCase() : 'unknown'
    const trustScore = scoreMatch ? parseInt(scoreMatch[1], 10) : 50
    const status = statusMatch ? statusMatch[1].trim().toLowerCase() : 'unknown'

    // Wiki links
    const links = [...content.matchAll(/\[\[([^\\]|]+)(?:\\|([^\\]]+))?\]\]/g)]
      .map(m => m[1].trim())
      .filter(l => l !== title)
    linkMap[name] = links

    const ring = RING_ASSIGNMENTS[title] !== undefined ? RING_ASSIGNMENTS[title] : 3

    nodes.push({
      id: title,
      label: title,
      category: type === 'governance' ? 'agent' : type === 'investor' ? 'agent' : 'system',
      ring,
      source: 'cf-vault',
      description: role,
      trustScore,
      status,
      color: RING_COLORS[ring] || '#aa88ff',
    })
    nodeSet.add(title)
  }

  // Wiki-link edges
  for (const n of nodes) {
    for (const target of (linkMap[n.id] || [])) {
      // Try to match by title or filename
      const matched = nodes.find(nd => nd.id === target || nd.id === target.replace(/[ .]/g, '-'))
      if (matched) {
        edges.push({ source: n.id, target: matched.id, type: 'wiki-link' })
      }
    }
  }

  return { nodes, edges }
}

// ── Main ──────────────────────────────────────────────────────────
function main() {
  const xmrt = parseXmrtVault()
  const cf = parseCfVault()

  // Merge — dedup by node id (case-insensitive)
  const allNodes = [...xmrt.nodes, ...cf.nodes]
  const seen = new Map()
  const dedupedNodes = []
  for (const n of allNodes) {
    const key = n.id.toLowerCase()
    if (!seen.has(key)) {
      seen.set(key, n)
      dedupedNodes.push(n)
    }
  }

  // Merge edges — dedup by source::target::type
  const allEdges = [...xmrt.edges, ...cf.edges]
  const edgeSet = new Set()
  const dedupedEdges = []
  for (const e of allEdges) {
    const key = e.source + '::' + e.target + '::' + e.type
    if (!edgeSet.has(key)) {
      edgeSet.add(key)
      dedupedEdges.push(e)
    }
  }

  // Ring metadata
  const rings = [
    { ring: 0, label: RING_LABELS[0], color: RING_COLORS[0], radius: 80 },
    { ring: 1, label: RING_LABELS[1], color: RING_COLORS[1], radius: 180 },
    { ring: 2, label: RING_LABELS[2], color: RING_COLORS[2], radius: 280 },
    { ring: 3, label: RING_LABELS[3], color: RING_COLORS[3], radius: 380 },
  ]

  // Node count per ring
  const ringCounts = {}
  for (const n of dedupedNodes) {
    ringCounts[n.ring] = (ringCounts[n.ring] || 0) + 1
  }

  const output = {
    nodes: dedupedNodes,
    edges: dedupedEdges,
    rings,
    summary: {
      totalNodes: dedupedNodes.length,
      totalEdges: dedupedEdges.length,
      byRing: ringCounts,
      bySource: {
        'xmrt-vault': xmrt.nodes.length,
        'cf-vault': cf.nodes.length,
      },
    },
  }

  writeFileSync(OUT, JSON.stringify(output, null, 2), 'utf-8')
  console.log(`Collective graph: ${dedupedNodes.length} nodes, ${dedupedEdges.length} edges`)
  console.log(`  Ring 0 (XMRT DAO Core): ${ringCounts[0] || 0} nodes`)
  console.log(`  Ring 1 (Infrastructure): ${ringCounts[1] || 0} nodes`)
  console.log(`  Ring 2 (Agents & People): ${ringCounts[2] || 0} nodes`)
  console.log(`  Ring 3 (Cuttlefish Governance): ${ringCounts[3] || 0} nodes`)
  console.log(`  Output: ${OUT}`)
}

main()