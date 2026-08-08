(function () {
  const article = document.querySelector(".composition-article");
  if (!article) return;

  const formatYears = (entry) => {
    if (entry.from && entry.to && entry.from !== entry.to) return `${entry.from}-${entry.to}`;
    if (entry.from) return String(entry.from);
    return "Año pendiente";
  };

  const normalize = (value) =>
    String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();

  fetch("data/capitanes-companias.json?v=15")
    .then((response) => response.json())
    .then((data) => {
      const entries = (data.entries || [])
        .filter((entry) => entry.company_slug === "general")
        .filter((entry) => normalize(entry.role) === "general")
        .filter((entry) => !/no hubo alarde|desconocido/i.test(entry.name || ""))
        .sort((a, b) => (a.from || 9999) - (b.from || 9999) || (a.name || "").localeCompare(b.name || "", "es"));

      if (!entries.length) return;

      const section = document.createElement("section");
      section.className = "company-captains";

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

        if (entry.needs_review || entry.status === "needs_review") {
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

        if (entry.source) {
          const source = document.createElement("p");
          source.className = "source-note";
          source.textContent = `Fuente: ${entry.source}`;
          card.append(source);
        }

        list.append(card);
      });

      section.append(list);
      article.append(section);
    })
    .catch(() => {});
})();
