// CareerForge AI — Minimal Clean Template
// A minimalist resume with clean typography and generous whitespace.

#set page(
  paper: "us-letter",
  margin: (x: 0.8in, y: 0.7in),
)

#set text(
  font: ("Georgia", "Times New Roman", "serif"),
  size: 10.5pt,
  fill: rgb("#111111"),
)

#set par(leading: 0.7em, justify: false)

// ── Header ─────────────────────────────────────────────

#let header(name, email, phone, location, linkedin, github, portfolio) = {
  align(center)[
    #text(size: 24pt, weight: "regular", fill: rgb("#111111"))[#name]
    #v(6pt)
    #{
      let parts = ()
      if email != "" { parts.push(email) }
      if phone != "" { parts.push(phone) }
      if location != "" { parts.push(location) }
      text(size: 9.5pt, fill: rgb("#555555"))[#parts.join([  |  ])]
    }
    #v(4pt)
    #{
      let links = ()
      if linkedin != "" { links.push(link(linkedin)[#text(fill: rgb("#333"))[linkedin]]) }
      if github != "" { links.push(link(github)[#text(fill: rgb("#333"))[github]]) }
      if portfolio != "" { links.push(link(portfolio)[#text(fill: rgb("#333"))[portfolio]]) }
      if links.len() > 0 {
        text(size: 9pt, fill: rgb("#777777"))[#links.join([  ·  ])]
      }
    }
  ]
  v(8pt)
}

// ── Section Heading ────────────────────────────────────

#let section-heading(name) = {
  text(size: 10.5pt, weight: "bold", fill: rgb("#111111"))[#upper(name)]
  v(2pt)
  line(length: 100%, stroke: 0.3pt + rgb("#cccccc"))
  v(6pt)
}

// ── Bullet Point ───────────────────────────────────────

#let bullet(content) = {
  pad(left: 16pt, hanging-indent: 12pt)[
    #text(size: 10pt, fill: rgb("#333333"))[- #h(4pt)#text(content)]
  ]
  v(2pt)
}

// ── Section: Skills ────────────────────────────────────

#let skills-section(items) = {
  section-heading("Skills")
  text(size: 9.5pt, fill: rgb("#333333"))[#items.join([  ·  ])]
  v(6pt)
}

// ── Section: Languages ─────────────────────────────────

#let languages-section(items) = {
  section-heading("Languages")
  text(size: 9.5pt, fill: rgb("#333333"))[#items.join([  ·  ])]
  v(6pt)
}

// ── Section: Links ─────────────────────────────────────

#let links-section(items) = {
  section-heading("Links")
  text(size: 9.5pt, fill: rgb("#333333"))[#items.join([  ·  ])]
  v(6pt)
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
