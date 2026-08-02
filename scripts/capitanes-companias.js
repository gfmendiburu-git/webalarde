(function () {
  const article = document.querySelector(".company-page");
  if (!article) return;

  const slug = window.location.pathname.split("/").pop().replace(/\.html$/, "");
  if (!slug) return;

  const formatYears = (entry) => {
    if (entry.from && entry.to && entry.from !== entry.to) return `${entry.from}-${entry.to}`;
    if (entry.from) return String(entry.from);
    return "Año pendiente";
  };

  const makeSource = (entry) => {
    if (!entry.source) return null;
    if (!entry.source_url) return document.createTextNode(entry.source);
    const link = document.createElement("a");
    link.href = entry.source_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = entry.source;
    return link;
  };

  const insertBeforeNote = (section) => {
    const note = article.querySelector(".company-note");
    if (note) {
      article.insertBefore(section, note);
    } else {
      article.append(section);
    }
  };

  fetch("../data/participacion-companias.json?v=3")
    .then((response) => response.json())
    .then((data) => {
      const company = (data.entries || []).find((entry) => entry.company_slug === slug);
      if (!company || !company.records || !company.records.length) return;

      const section = document.createElement("section");
      section.className = "company-participation";

      const heading = document.createElement("h2");
      heading.textContent = "Participación documentada";
      section.append(heading);

      const list = document.createElement("div");
      list.className = "participation-list";

      company.records.forEach((record) => {
        const card = document.createElement("article");
        card.className = "participation-entry";

        const years = document.createElement("p");
        years.className = "participation-years";
        years.textContent = record.years;
        card.append(years);

        if (record.evidence) {
          const evidence = document.createElement("p");
          evidence.textContent = record.evidence;
          card.append(evidence);
        }

        if (record.source) {
          const source = document.createElement("p");
          source.className = "source-note";
          source.textContent = `Fuente: ${record.source}`;
          card.append(source);
        }

        list.append(card);
      });

      section.append(list);
      insertBeforeNote(section);
    })
    .catch(() => {});

  const headingBySlug = {
    hacheros: "Cabos documentados",
    tamborrada: "Tambores Mayores documentados",
    banda: "Directores documentados",
    general: "Generales documentados",
    "estado-mayor": "Mandos documentados",
    comandante: "Comandantes documentados",
  };

  fetch("../data/capitanes-companias.json?v=15")
    .then((response) => response.json())
    .then((data) => {
      const entries = (data.entries || [])
        .filter((entry) => entry.company_slug === slug)
        .sort((a, b) => {
          const ay = a.from || 9999;
          const by = b.from || 9999;
          return ay - by || a.name.localeCompare(b.name, "es");
        });

      if (!entries.length) return;

      const section = document.createElement("section");
      section.className = "company-captains";

      const heading = document.createElement("h2");
      heading.textContent = headingBySlug[slug] || "Capitanes documentados";
      section.append(heading);

      const list = document.createElement("div");
      list.className = "captains-list";

      entries.forEach((entry) => {
        const card = document.createElement("article");
        card.className = "captain-entry";

        const years = document.createElement("p");
        years.className = "captain-years";
        years.textContent = formatYears(entry);
        card.append(years);

        const name = document.createElement("h3");
        name.textContent = entry.name;
        card.append(name);

        if (entry.role) {
          const role = document.createElement("p");
          role.className = "captain-role";
          role.textContent = entry.role;
          card.append(role);
        }

        if (entry.status === "needs_review") {
          const status = document.createElement("p");
          status.className = "captain-status";
          status.textContent = "Pendiente de contraste";
          card.append(status);
        }

        if (entry.notes) {
          const notes = document.createElement("p");
          notes.textContent = entry.notes;
          card.append(notes);
        }

        const source = makeSource(entry);
        if (source) {
          const sourceNote = document.createElement("p");
          sourceNote.className = "source-note";
          sourceNote.append("Fuente: ", source);
          card.append(sourceNote);
        }

        list.append(card);
      });

      section.append(list);

      insertBeforeNote(section);
    })
    .catch(() => {});
})();
