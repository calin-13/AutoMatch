const WIKI_MODEL_MAP = {
  'seria 1': '1_Series', 'seria 2': '2_Series', 'seria 3': '3_Series',
  'seria 4': '4_Series', 'seria 5': '5_Series', 'seria 6': '6_Series',
  'seria 7': '7_Series', 'seria 8': '8_Series',
  'clasa a': 'A-Class', 'clasa b': 'B-Class', 'clasa c': 'C-Class',
  'clasa e': 'E-Class', 'clasa s': 'S-Class', 'clasa g': 'G-Class',
  'clasa cls': 'CLS-Class', 'clasa gle': 'GLE', 'clasa glc': 'GLC',
  'clasa gla': 'GLA', 'clasa glb': 'GLB',
}

const WIKI_BRAND_MAP = {
  'mercedes-benz': 'Mercedes-Benz',
  'mercedes benz': 'Mercedes-Benz',
  'vw': 'Volkswagen',
  'skoda': 'Škoda',
}

function titleCase(s) {
  return s.split(/[\s-]+/)
    .filter(Boolean)
    .map(w => w[0].toUpperCase() + w.slice(1).toLowerCase())
    .join('_')
}

function buildWikipediaTitle(brand, model) {
  if (!brand || !model) return null
  const b = brand.trim()
  const m = model.toLowerCase().trim()
  const brandTitle = WIKI_BRAND_MAP[b.toLowerCase()] || b.replace(/\s+/g, '_')
  const modelTitle = WIKI_MODEL_MAP[m] || titleCase(m)
  return `${brandTitle}_${modelTitle}`
}

const imageCache = new Map()

export async function fetchCarImage(brand, model) {
  const title = buildWikipediaTitle(brand, model)
  if (!title) return null

  if (imageCache.has(title)) return imageCache.get(title)

  try {
    const url = `https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=900&titles=${encodeURIComponent(title)}&origin=*`
    const res = await fetch(url)
    if (!res.ok) {
      imageCache.set(title, null)
      return null
    }
    const data = await res.json()
    const pages = data?.query?.pages || {}
    const firstPage = Object.values(pages)[0]
    const imageUrl = firstPage?.thumbnail?.source || null
    imageCache.set(title, imageUrl)
    return imageUrl
  } catch {
    imageCache.set(title, null)
    return null
  }
}
