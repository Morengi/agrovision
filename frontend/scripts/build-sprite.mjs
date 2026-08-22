// Concatenates every src/assets/icons/*.svg into a single public/sprites.svg
// sprite of <symbol id="icon-<filename>"> entries, referenced at runtime as
// <svg><use href="/sprites.svg#icon-<name>" /></svg> (see IconSvg.vue).
import { readdirSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const root = fileURLToPath(new URL('..', import.meta.url))
const iconsDir = path.join(root, 'src/assets/icons')
const outDir = path.join(root, 'public')
const outFile = path.join(outDir, 'sprites.svg')

mkdirSync(outDir, { recursive: true })
mkdirSync(iconsDir, { recursive: true })

const files = readdirSync(iconsDir).filter((f) => f.endsWith('.svg')).sort()

const symbols = files.map((file) => {
  const name = path.basename(file, '.svg')
  const raw = readFileSync(path.join(iconsDir, file), 'utf-8')

  const viewBoxMatch = raw.match(/viewBox="([^"]+)"/)
  const viewBox = viewBoxMatch ? viewBoxMatch[1] : '0 0 24 24'

  const inner = raw
    .replace(/^[\s\S]*?<svg[^>]*>/, '')
    .replace(/<\/svg>\s*$/, '')
    .trim()

  return `  <symbol id="icon-${name}" viewBox="${viewBox}">\n    ${inner}\n  </symbol>`
})

const sprite = `<svg xmlns="http://www.w3.org/2000/svg" style="display:none">\n${symbols.join('\n')}\n</svg>\n`

writeFileSync(outFile, sprite, 'utf-8')
console.log(`[build-sprite] wrote ${files.length} icon(s) to ${path.relative(root, outFile)}`)
