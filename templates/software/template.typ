// CareerForge AI — Software Engineer Template
// Technical resume with skills grid and project emphasis.

#set page(
  paper: "us-letter",
  margin: (x: 0.65in, y: 0.55in),
)

#set text(
  font: ("SF Mono", "JetBrains Mono", "Consolas", "monospace"),
  size: 9.5pt,
  fill: rgb("#0f172a"),
)

#set par(leading: 0.55em, justify: false)

// ── Header ─────────────────────────────────────────────

#let header(name, email, phone, location, linkedin, github, portfolio) = {
  grid(
    columns: (1fr, auto),
    align: (left, right),
    [
      #text(size: 20pt, weight: "bold", fill: rgb("#0f172a"))[#name]
      #v(2pt)
      #text(size: 9pt, fill: rgb("#475569"))[#phone #h(6pt)| #h(6pt)#email]
      #v(1pt)
      #text(size: 9pt, fill: rgb("#475569"))[#location]
    ],
    {
      let links = ()
      if linkedin != "" { links.push(link(linkedin)[LinkedIn]) }
      if github != "" { links.push(link(github)[GitHub]) }
      if portfolio != "" { links.push(link(portfolio)[Portfolio]) }
      if links.len() > 0 {
        text(size: 8.5pt, fill: rgb("#3b82f6"))[#links.join([ #h(4pt)])]
      }
    },
  )
  v(6pt)
  line(length: 100%, stroke: 1.5pt + rgb("#0f172a"))
  v(6pt)
}

// ── Section Heading ────────────────────────────────────

#let section-heading(name) = {
  text(size: 10pt, weight: "bold", fill: rgb("#0f172a"))[#upper(name)]
  v(2pt)
  line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
  v(4pt)
}

// ── Bullet Point ───────────────────────────────────────

#let bullet(content) = {
  pad(left: 12pt, hanging-indent: 10pt)[
    #text(size: 9.5pt, fill: rgb("#1e293b"))[#sym.bullet.r #h(6pt)#text(content)]
  ]
  v(1pt)
}

// ── Section: Skills ────────────────────────────────────

#let skills-section(items) = {
  section-heading("Technical Skills")
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    ..items.map(item => [
      #text(size: 9pt, fill: rgb("#1e293b"))[#item]
    ])
  )
  v(4pt)
}

// ── Section: Languages ─────────────────────────────────

#let languages-section(items) = {
  section-heading("Languages")
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    ..items.map(item => [
      #text(size: 9pt, fill: rgb("#1e293b"))[#item]
    ])
  )
  v(4pt)
}

// ── Section: Links ─────────────────────────────────────

#let links-section(items) = {
  section-heading("Links")
  grid(
    columns: (1fr, 1fr),
    column-gutter: 12pt,
    ..items.map(item => [
      #text(size: 9pt, fill: rgb("#1e293b"))[#item]
    ])
  )
  v(4pt)
}

// ── Section: Generic ───────────────────────────────────

#let generic-section(name, items) = {
  section-heading(name)
  for item in items {
    bullet(item)
  }
  v(3pt)
}

// ── Section: Experience / Projects / Education ─────────

#let detail-section(name, items) = {
  section-heading(name)
  for item in items {
    bullet(item)
  }
  v(3pt)
}
