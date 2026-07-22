// CareerForge AI — Academic CV Template
// Formal CV layout with research emphasis and publication support.

#set page(
  paper: "us-letter",
  margin: (x: 0.75in, y: 0.65in),
)

#set text(
  font: ("Times New Roman", "Georgia", "serif"),
  size: 11pt,
  fill: rgb("#1a1a1a"),
)

#set par(leading: 0.7em, justify: false)

// ── Header ─────────────────────────────────────────────

#let header(name, email, phone, location, linkedin, github, portfolio) = {
  align(center)[
    #text(size: 20pt, weight: "bold", fill: rgb("#1a1a1a"))[#name]
    #v(6pt)
    #{
      let parts = ()
      if email != "" { parts.push(email) }
      if phone != "" { parts.push(phone) }
      if location != "" { parts.push(location) }
      text(size: 9.5pt, fill: rgb("#444444"))[#parts.join([  |  ])]
    }
    #v(4pt)
    #{
      let links = ()
      if linkedin != "" { links.push(link(linkedin)[#text(fill: rgb("#1a1a1a"))[LinkedIn]]) }
      if github != "" { links.push(link(github)[#text(fill: rgb("#1a1a1a"))[GitHub]]) }
      if portfolio != "" { links.push(link(portfolio)[#text(fill: rgb("#1a1a1a"))[Portfolio]]) }
      if links.len() > 0 {
        text(size: 9pt, fill: rgb("#555555"))[#links.join([  |  ])]
      }
    }
  ]
  v(6pt)
  line(length: 100%, stroke: 1pt + rgb("#1a1a1a"))
  v(8pt)
}

// ── Section Heading ────────────────────────────────────

#let section-heading(name) = {
  text(size: 12pt, weight: "bold", fill: rgb("#1a1a1a"))[#name]
  v(2pt)
  line(length: 100%, stroke: 0.5pt + rgb("#999999"))
  v(6pt)
}

// ── Bullet Point ───────────────────────────────────────

#let bullet(text) = {
  pad(left: 18pt, hanging-indent: 14pt)[
    #text(size: 10.5pt, fill: rgb("#333333"))[• #h(4pt)#text(text)]
  ]
  v(2pt)
}

// ── Section: Skills ────────────────────────────────────

#let skills-section(items) = {
  section-heading("Skills")
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 14pt,
    ..items.map(item => [
      #text(size: 10pt, fill: rgb("#333333"))[#item]
    ])
  )
  v(6pt)
}

// ── Section: Languages ─────────────────────────────────

#let languages-section(items) = {
  section-heading("Languages")
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 14pt,
    ..items.map(item => [
      #text(size: 10pt, fill: rgb("#333333"))[#item]
    ])
  )
  v(6pt)
}

// ── Section: Links ─────────────────────────────────────

#let links-section(items) = {
  section-heading("Links")
  grid(
    columns: (1fr, 1fr),
    column-gutter: 14pt,
    ..items.map(item => [
      #text(size: 10pt, fill: rgb("#333333"))[#item]
    ])
  )
  v(6pt)
}

// ── Section: Publications ──────────────────────────────

#let publications-section(items) = {
  section-heading("Publications")
  for item in items {
    text(size: 10.5pt, fill: rgb("#333333"))[#item]
    v(3pt)
  }
  v(4pt)
}

// ── Section: Awards ────────────────────────────────────

#let awards-section(items) = {
  section-heading("Awards & Honors")
  for item in items {
    bullet(item)
  }
  v(4pt)
}

// ── Section: Generic ───────────────────────────────────

#let generic-section(name, items) = {
  section-heading(name)
  for item in items {
    bullet(item)
  }
  v(4pt)
}

// ── Section: Experience / Projects / Education ─────────

#let detail-section(name, items) = {
  section-heading(name)
  for item in items {
    bullet(item)
  }
  v(4pt)
}
