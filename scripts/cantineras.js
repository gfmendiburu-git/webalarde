(function () {
  const modeInputs = document.querySelectorAll("[name='cantinera-view']");
  const filterLabel = document.querySelector("#cantinera-filter-label");
  const filterSelect = document.querySelector("#cantinera-filter");
  const resultTitle = document.querySelector("#cantinera-result-title");
  const resultMeta = document.querySelector("#cantinera-result-meta");
  const resultBody = document.querySelector("#cantinera-results");
  const defaultPhoto = "assets/cantineras/cantinera-generica.webp";
  const galleryPage = "cantinera-galeria.html";

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
    if (!entry.source_url) {
      const source = document.createElement("span");
      source.className = "cantinera-source-text";
      source.textContent = "Fuente local";
      source.title = entry.source_title || "Fuente documental pendiente de enlace publico";
      return source;
    }

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

  const entryKey = (entry) => {
    const normalizedName = entry.name
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
    return `${entry.year}|${entry.company}|${normalizedName}`;
  };

  const photoForEntry = (entry, photosById) => photosById.get(entryKey(entry));

  const renderCards = (entries, mode, photosById) => {
    const grid = document.createElement("div");
    grid.className = "cantineras-card-grid";

    entries.forEach((entry) => {
      const card = document.createElement("article");
      card.className = "cantinera-card";

      const figure = document.createElement("figure");
      figure.className = "cantinera-card-photo";

      const photoData = photoForEntry(entry, photosById);
      const profile = photoData?.profile;
      const image = document.createElement("img");
      image.src = profile?.full || entry.photo || defaultPhoto;
      image.alt = profile
        ? `${entry.name}, ${entry.company}, ${entry.year}`
        : `Imagen genérica de cantinera para ${entry.name}`;
      image.loading = "lazy";
      image.width = 600;
      image.height = 800;

      if (photoData) {
        const link = document.createElement("a");
        link.className = "cantinera-photo-link";
        link.href = `${galleryPage}?id=${encodeURIComponent(photoData.id)}`;
        link.setAttribute("aria-label", `Ver galería de ${entry.name}`);
        link.append(image);
        figure.append(link);
      } else {
        figure.append(image);
      }

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
      if (photoData) {
        const galleryLink = document.createElement("a");
        galleryLink.href = `${galleryPage}?id=${encodeURIComponent(photoData.id)}`;
        galleryLink.textContent = `${photoData.photos.length} foto${photoData.photos.length === 1 ? "" : "s"}`;
        actions.append(galleryLink);
      }
      if (entry.needs_review) {
        actions.append(reviewBadge());
      }

      content.append(meta, name, actions);
      card.append(figure, content);
      grid.append(card);
    });

    return grid;
  };

  const renderEmptyCompany = (company) => {
    const message = document.createElement("p");
    message.className = "cantineras-empty";
    message.textContent = `No se han encontrado datos de cantineras para ${company}.`;
    return message;
  };

  const companyMatches = (entry, company) => {
    if (!company) {
      return false;
    }
    return entry.company === company.name || (company.aliases || []).includes(entry.company);
  };

  const setFilterOptions = (items, value, fallbackValue) => {
    const fragment = document.createDocumentFragment();
    items.forEach((item) => {
      const option = document.createElement("option");
      option.value = item;
      option.textContent = item;
      fragment.append(option);
    });
    filterSelect.replaceChildren(fragment);
    filterSelect.disabled = items.length === 0;
    filterSelect.value = items.includes(value) ? value : fallbackValue || items[items.length - 1] || "";
  };

  const render = (data, companies, photosById) => {
    const mode = currentMode();

    if (mode === "year") {
      const year = Number(filterSelect.value);
      selected.year = filterSelect.value;
      const entries = data.entries
        .filter((entry) => entry.year === year)
        .sort((a, b) => byCompany(a.company, b.company));
      resultTitle.textContent = `Cantineras de ${year}`;
      resultMeta.textContent = `${entries.length} registros localizados`;
      resultBody.replaceChildren(renderCards(entries, mode, photosById));
      return;
    }

    const companyName = filterSelect.value;
    const company = companies.find((item) => item.name === companyName) || { name: companyName, aliases: [] };
    selected.company = companyName;
    const entries = data.entries
      .filter((entry) => companyMatches(entry, company))
      .sort((a, b) => byYear(a.year, b.year));
    resultTitle.textContent = company.name;
    if (!entries.length) {
      resultMeta.textContent = "Sin registros documentados";
      resultBody.replaceChildren(renderEmptyCompany(company.name));
      return;
    }
    resultMeta.textContent = `${entries.length} años con registro localizado`;
    resultBody.replaceChildren(renderCards(entries, mode, photosById));
  };

  const updateMode = (data, years, companies, photosById) => {
    const mode = currentMode();
    if (mode === "year") {
      filterLabel.textContent = "Año";
      setFilterOptions(years, selected.year);
    } else {
      filterLabel.textContent = "Compañía";
      const companyNames = companies.map((company) => company.name);
      setFilterOptions(companyNames, selected.company, companyNames[0]);
    }
    render(data, companies, photosById);
  };

  const normalizeCompanies = (sourceCompanies, entries) => {
    const companies = new Map();
    (sourceCompanies.entries || []).forEach((company) => {
      if (company.name) {
        companies.set(company.name, {
          name: company.name,
          aliases: company.aliases || [],
        });
      }
    });

    entries.forEach((entry) => {
      const exists = [...companies.values()].some((company) => companyMatches(entry, company));
      if (!exists) {
        companies.set(entry.company, { name: entry.company, aliases: [] });
      }
    });

    return [...companies.values()].sort((a, b) => byCompany(a.name, b.name));
  };

  Promise.all([
    fetch("data/cantineras.json?v=3").then((response) => response.json()),
    fetch("data/cantinera-fotos.json?v=1").then((response) => response.json()).catch(() => ({ entries: [] })),
    fetch("data/companias-cantineras.json?v=1").then((response) => response.json()).catch(() => ({ entries: [] })),
  ])
    .then(([data, photoData, sourceCompanies]) => {
      const photosById = new Map((photoData.entries || []).map((entry) => [entry.id, entry]));
      const years = [...new Set(data.entries.map((entry) => String(entry.year)))].sort(byYear);
      const companies = normalizeCompanies(sourceCompanies, data.entries);

      selected.year = years[years.length - 1];
      selected.company = companies[0]?.name || "";

      modeInputs.forEach((input) => input.addEventListener("change", () => updateMode(data, years, companies, photosById)));
      filterSelect.addEventListener("change", () => render(data, companies, photosById));
      updateMode(data, years, companies, photosById);
    })
    .catch(() => {
      resultTitle.textContent = "No se ha podido cargar el listado";
      resultMeta.textContent = "";
      resultBody.replaceChildren();
    });
})();
