import { useState, useEffect } from 'react'
import { CAC_TIERS, STACK_LAYERS, CONTRACTS, SCENARIOS } from './mockData'
import type { CACTier, Contract, StackLayer, Scenario } from './types'

function useApiData<T>(url: string, fallback: T[]): { data: T[]; loading: boolean } {
  const [data, setData] = useState<T[]>(fallback)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    fetch(url)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (cancelled) return
        if (d && d.data && Array.isArray(d.data) && d.data.length > 0) {
          setData(d.data)
        } else if (d && d.layers && Array.isArray(d.layers) && d.layers.length > 0) {
          // Capital stack endpoint uses { layers: [...] }
          setData(d.layers as T[])
        }
        setLoading(false)
      })
      .catch(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [url])

  return { data, loading }
}

export function useCACTiers() {
  return useApiData<CACTier>('/api/cuttlefishclaws/cac-tiers', CAC_TIERS as unknown as CACTier[])
}

export function useCapitalStack() {
  return useApiData<StackLayer>('/api/cuttlefishclaws/capital-stack', STACK_LAYERS as StackLayer[])
}

export function useContracts() {
  return useApiData<Contract>('/api/cuttlefishclaws/contracts', CONTRACTS as Contract[])
}

export function useScenarios() {
  return useApiData<Scenario>('/api/cuttlefishclaws/scenarios', SCENARIOS as Scenario[])
}
