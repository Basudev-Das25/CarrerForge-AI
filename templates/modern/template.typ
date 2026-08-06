// CareerForge AI — Modern Professional Template
// A clean, modern resume with professional typography and balanced whitespace.

#set page(
  paper: "us-letter",
  margin: (x: 0.7in, y: 0.6in),
)

#set text(
  font: ("Inter", "Helvetica Neue", "Helvetica", "Arial"),
  size: 10pt,
  fill: rgb("#1a1a2e"),
)

#set par(leading: 0.6em, justify: false)

// ── Header ─────────────────────────────────────────────

#let header(name, email, phone, location, linkedin, github, portfolio) = {
  align(center)[
    #text(size: 22pt, weight: "bold", fill: rgb("#1a1a2e"))[#name]
    #v(4pt)
    #{
      let parts = ()
      if email != "" { parts.push(link("mailto:" + email)[#email]) }
      if phone != "" { parts.push(phone) }
      if location != "" { parts.push(location) }
      text(size: 9pt, fill: rgb("#4a5568"))[#parts.join([#h(6pt)•#h(6pt)])]
    }
    #v(3pt)
    #{
      let links = ()
      if linkedin != "" { links.push(link(linkedin)[#text(fill: rgb("#0077b5"))[LinkedIn]]) }
      if github != "" { links.push(link(github)[#text(fill: rgb("#333"))[GitHub]]) }
      if portfolio != "" { links.push(link(portfolio)[#text(fill: rgb("#0077b5"))[Portfolio]]) }
      if links.len() > 0 {
        text(size: 9pt)[#links.join([#h(8pt)])]
      }
    }
  ]
  v(4pt)
  line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
  v(6pt)
}

// ── Section Heading ────────────────────────────────────

#let section-heading(name) = {
  text(size: 11pt, weight: "bold", fill: rgb("#1a1a2e"))[#upper(name)]
  v(2pt)
  line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
  v(4pt)
}

// ── Bullet Point ───────────────────────────────────────

#let bullet(content) = {
  pad(left: 0pt)[
    #text(size: 10pt, fill: rgb("#2d3748"))[• #h(4pt)#text(content)]
  ]
  v(1.5pt)
}

// ── Section: Skills ────────────────────────────────────

#let skills-section(items) = {
  section-heading("Skills")
  grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    ..items.map(item => [
      #text(size: 9.5pt, fill: rgb("#2d3748"))[#item]
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
      #text(size: 9.5pt, fill: rgb("#2d3748"))[#item]
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
      #text(size: 9.5pt, fill: rgb("#2d3748"))[#item]
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
  v(2pt)
}

// ── Section: Experience / Projects / Education ─────────

#let detail-section(name, items) = {
  section-heading(name)
  for item in items {
    bullet(item)
  }
  v(2pt)
}
