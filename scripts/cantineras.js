(function () {
  const modeInputs = document.querySelectorAll("[name='cantinera-view']");
  const filterLabel = document.querySelector("#cantinera-filter-label");
  const filterSelect = document.querySelector("#cantinera-filter");
  const resultTitle = document.querySelector("#cantinera-result-title");
  const resultMeta = document.querySelector("#cantinera-result-meta");
  const resultBody = document.querySelector("#cantinera-results");
  const defaultPhoto = "assets/cantineras/cantinera-generica.webp";

  if (!modeInputs.length || !filterLabel || !filterSelect || !resultBody) {
    return;
  }

  const collator = new Intl.Collator("es", { sensitivity: "base" });

  const byYear = (a, b) => Number(a) - Number(b);
  const byCompany = (a, b) => collator.compare(a, b);

  const currentMode = () => {
    const checked = document.querySelector("[name='cantinera-view']:checked");
    return checked ? checked.value : "year";
  };

  const selected = {
    year: "",
    company: "",
  };

  const sourceLink = (entry) => {
    const link = document.createElement("a");
    link.href = entry.source_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Fuente";
    return link;
  };

  const reviewBadge = () => {
    const badge = document.createElement("span");
    badge.className = "review-badge";
    badge.textContent = "Revisar";
    return badge;
  };

  const createMeta = (value) => {
    const item = document.createElement("span");
    item.className = "cantinera-card-meta-item";
    item.textContent = value;
    return item;
  };

  const renderCards = (entries, mode) => {
    const grid = document.createElement("div");
    grid.className = "cantineras-card-grid";

    entries.forEach((entry) => {
      const card = document.createElement("article");
      card.className = "cantinera-card";

      const figure = document.createElement("figure");
      figure.className = "cantinera-card-photo";

      const image = document.createElement("img");
      image.src = entry.photo || defaultPhoto;
      image.alt = `Imagen genérica de cantinera para ${entry.name}`;
      image.loading = "lazy";
      image.width = 600;
      image.height = 800;
      figure.append(image);

      const content = document.createElement("div");
      content.className = "cantinera-card-content";

      const meta = document.createElement("div");
      meta.className = "cantinera-card-meta";
      if (mode === "year") {
        meta.append(createMeta(entry.company));
      } else {
        meta.append(createMeta(entry.year));
      }

      const name = document.createElement("h4");
      name.textContent = entry.name;

      const actions = document.createElement("div");
      actions.className = "cantinera-card-actions";
      actions.append(sourceLink(entry));
      if (entry.needs_review) {
        actions.append(reviewBadge());
      }

      content.append(meta, name, actions);
      card.append(figure, content);
      grid.append(card);
    });

    return grid;
  };

  const setFilterOptions = (items, value) => {
    const fragment = document.createDocumentFragment();
    items.forEach((item) => {
      const option = document.createElement("option");
      option.value = item;
      option.textContent = item;
      fragment.append(option);
    });
    filterSelect.replaceChildren(fragment);
    filterSelect.value = items.includes(value) ? value : items[items.length - 1];
  };

  const render = (data) => {
    const mode = currentMode();

    if (mode === "year") {
      const year = Number(filterSelect.value);
      selected.year = filterSelect.value;
      const entries = data.entries
        .filter((entry) => entry.year === year)
        .sort((a, b) => byCompany(a.company, b.company));
      resultTitle.textContent = `Cantineras de ${year}`;
      resultMeta.textContent = `${entries.length} registros localizados`;
      resultBody.replaceChildren(renderCards(entries, mode));
      return;
    }

    const company = filterSelect.value;
    selected.company = company;
    const entries = data.entries
      .filter((entry) => entry.company === company)
      .sort((a, b) => byYear(a.year, b.year));
    resultTitle.textContent = company;
    resultMeta.textContent = `${entries.length} años con registro localizado`;
    resultBody.replaceChildren(renderCards(entries, mode));
  };

  const updateMode = (data, years, companies) => {
    const mode = currentMode();
    if (mode === "year") {
      filterLabel.textContent = "Año";
      setFilterOptions(years, selected.year);
    } else {
      filterLabel.textContent = "Compañía";
      setFilterOptions(companies, selected.company);
    }
    render(data);
  };

  fetch("data/cantineras.json?v=1")
    .then((response) => response.json())
    .then((data) => {
      const years = [...new Set(data.entries.map((entry) => String(entry.year)))].sort(byYear);
      const companies = [...new Set(data.entries.map((entry) => entry.company))].sort(byCompany);

      selected.year = years[years.length - 1];
      selected.company = companies[0];

      modeInputs.forEach((input) => input.addEventListener("change", () => updateMode(data, years, companies)));
      filterSelect.addEventListener("change", () => render(data));
      updateMode(data, years, companies);
    })
    .catch(() => {
      resultTitle.textContent = "No se ha podido cargar el listado";
      resultMeta.textContent = "";
      resultBody.replaceChildren();
    });
})();
