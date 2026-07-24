(function () {
  const modeInputs = document.querySelectorAll("[name='cantinera-view']");
  const filterLabel = document.querySelector("#cantinera-filter-label");
  const filterSelect = document.querySelector("#cantinera-filter");
  const resultTitle = document.querySelector("#cantinera-result-title");
  const resultMeta = document.querySelector("#cantinera-result-meta");
  const resultBody = document.querySelector("#cantinera-results");
  const defaultPhoto = "assets/cantineras/cantinera-generica.webp";
  const galleryPage = "cantinera-galeria.html";
  const initialParams = new URLSearchParams(window.location.search);

  if (!modeInputs.length || !filterLabel || !filterSelect || !resultBody) {
    return;
  }

  const collator = new Intl.Collator("es", { sensitivity: "base" });

  const byYear = (a, b) => Number(a) - Number(b);
  const byCompany = (a, b) => collator.compare(a, b);
  const noCantineraCompanyNames = new Set(["Comandante del Batallón", "Estado Mayor", "General"]);

  const normalizeText = (value) => String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/ñ/g, "n")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");

  const currentMode = () => {
    const checked = document.querySelector("[name='cantinera-view']:checked");
    return checked ? checked.value : "year";
  };

  const selected = {
    year: "",
    company: "",
  };

  const currentListParams = () => {
    const params = new URLSearchParams();
    const mode = currentMode();
    params.set("view", mode);
    if (mode === "year") {
      params.set("year", filterSelect.value);
    } else {
      params.set("company", filterSelect.value);
    }
    return params;
  };

  const updateAddress = () => {
    const params = currentListParams();
    window.history.replaceState(null, "", `${window.location.pathname}?${params.toString()}#listado-historico`);
  };

  const galleryHref = (photoData) => {
    const params = currentListParams();
    params.set("id", photoData.id);
    return `${galleryPage}?${params.toString()}`;
  };

  const sourceLink = (entry) => {
    if (entry.no_data) {
      const source = document.createElement("span");
      source.className = "cantinera-source-text";
      source.textContent = "Sin datos";
      source.title = entry.note || "Compañía documentada ese año; cantinera pendiente de identificar";
      return source;
    }

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
    const normalizedName = normalizeText(entry.name);
    return `${entry.year}|${entry.company}|${normalizedName}`;
  };

  const photoForEntry = (entry, photosById) => photosById.get(entryKey(entry));

  const companyMatches = (entry, company) => {
    if (!company) {
      return false;
    }
    return entry.company === company.name || (company.aliases || []).includes(entry.company);
  };

  const buildCompanyLookup = (companies) => {
    const lookup = new Map();
    companies.forEach((company) => {
      lookup.set(normalizeText(company.name), company);
      (company.aliases || []).forEach((alias) => lookup.set(normalizeText(alias), company));
    });
    return lookup;
  };

  const canonicalCompanyName = (value, companyLookup) => companyLookup.get(normalizeText(value))?.name || value;

  const knownCompaniesForYear = (entries, year, companies) => {
    const companyLookup = buildCompanyLookup(companies);
    return new Set(entries
      .filter((entry) => entry.year === year)
      .map((entry) => canonicalCompanyName(entry.company, companyLookup)));
  };

  const knownYearsForCompany = (entries, company) => new Set(entries
    .filter((entry) => companyMatches(entry, company))
    .map((entry) => Number(entry.year)));

  const placeholderEntry = (year, companyName) => ({
    year,
    company: companyName,
    name: "Sin datos",
    no_data: true,
    note: "Compañía documentada ese año; cantinera pendiente de identificar.",
  });

  const buildParticipation = (captainData, companies) => {
    const companyLookup = buildCompanyLookup(companies);
    const participation = new Map();
    (captainData.entries || []).forEach((entry) => {
      const company = companyLookup.get(normalizeText(entry.company));
      if (!company || noCantineraCompanyNames.has(company.name)) {
        return;
      }
      const from = Number(entry.from);
      const to = Number(entry.to || entry.from);
      if (!Number.isInteger(from) || !Number.isInteger(to) || from < 1800 || to < from || to - from > 200) {
        return;
      }
      if (!participation.has(company.name)) {
        participation.set(company.name, new Set());
      }
      for (let year = from; year <= to; year += 1) {
        participation.get(company.name).add(year);
      }
    });
    return participation;
  };

  const enrichByYear = (entries, year, companies, participation) => {
    const known = knownCompaniesForYear(entries, year, companies);
    const placeholders = [];
    participation.forEach((years, companyName) => {
      if (years.has(year) && !known.has(companyName)) {
        placeholders.push(placeholderEntry(year, companyName));
      }
    });
    return [...entries, ...placeholders].sort((a, b) => byCompany(a.company, b.company));
  };

  const enrichByCompany = (entries, company, participation) => {
    const known = knownYearsForCompany(entries, company);
    const placeholders = [...(participation.get(company.name) || [])]
      .filter((year) => !known.has(year))
      .map((year) => placeholderEntry(year, company.name));
    return [...entries, ...placeholders].sort((a, b) => byYear(a.year, b.year));
  };

  const renderCards = (entries, mode, photosById) => {
    const grid = document.createElement("div");
    grid.className = "cantineras-card-grid";

    entries.forEach((entry) => {
      const card = document.createElement("article");
      card.className = "cantinera-card";
      if (entry.no_data) {
        card.classList.add("is-missing");
      }

      const figure = document.createElement("figure");
      figure.className = "cantinera-card-photo";

      const photoData = photoForEntry(entry, photosById);
      const profile = photoData?.profile;
      const image = document.createElement("img");
      image.src = entry.no_data ? defaultPhoto : profile?.full || entry.photo || defaultPhoto;
      image.alt = profile
        ? `${entry.name}, ${entry.company}, ${entry.year}`
        : entry.no_data
          ? `Sin datos de cantinera para ${entry.company}, ${entry.year}`
          : `Imagen genérica de cantinera para ${entry.name}`;
      image.loading = "lazy";
      image.width = 600;
      image.height = 800;

      if (photoData) {
        const link = document.createElement("a");
        link.className = "cantinera-photo-link";
        link.href = galleryHref(photoData);
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
      if (photoData && !entry.no_data) {
        const galleryLink = document.createElement("a");
        galleryLink.href = galleryHref(photoData);
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

  const resultCountLabel = (entries) => {
    const identified = entries.filter((entry) => !entry.no_data).length;
    const missing = entries.length - identified;
    if (!missing) {
      return `${identified} registros localizados`;
    }
    return `${identified} registros localizados · ${missing} sin datos`;
  };

  const render = (data, companies, photosById, participation) => {
    const mode = currentMode();

    if (mode === "year") {
      const year = Number(filterSelect.value);
      selected.year = filterSelect.value;
      const documentedEntries = data.entries
        .filter((entry) => entry.year === year)
        .sort((a, b) => byCompany(a.company, b.company));
      const entries = enrichByYear(documentedEntries, year, companies, participation);
      resultTitle.textContent = `Cantineras de ${year}`;
      resultMeta.textContent = resultCountLabel(entries);
      resultBody.replaceChildren(renderCards(entries, mode, photosById));
      updateAddress();
      return;
    }

    const companyName = filterSelect.value;
    const company = companies.find((item) => item.name === companyName) || { name: companyName, aliases: [] };
    selected.company = companyName;
    const documentedEntries = data.entries
      .filter((entry) => companyMatches(entry, company))
      .sort((a, b) => byYear(a.year, b.year));
    const entries = enrichByCompany(documentedEntries, company, participation);
    resultTitle.textContent = company.name;
    if (!entries.length) {
      resultMeta.textContent = "Sin registros documentados";
      resultBody.replaceChildren(renderEmptyCompany(company.name));
      updateAddress();
      return;
    }
    resultMeta.textContent = resultCountLabel(entries);
    resultBody.replaceChildren(renderCards(entries, mode, photosById));
    updateAddress();
  };

  const updateMode = (data, years, companies, photosById, participation) => {
    const mode = currentMode();
    if (mode === "year") {
      filterLabel.textContent = "Año";
      setFilterOptions(years, selected.year);
    } else {
      filterLabel.textContent = "Compañía";
      const companyNames = companies.map((company) => company.name);
      setFilterOptions(companyNames, selected.company, companyNames[0]);
    }
    render(data, companies, photosById, participation);
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
    fetch("data/cantinera-fotos.json?v=3").then((response) => response.json()).catch(() => ({ entries: [] })),
    fetch("data/companias-cantineras.json?v=1").then((response) => response.json()).catch(() => ({ entries: [] })),
    fetch("data/capitanes-companias.json?v=3").then((response) => response.json()).catch(() => ({ entries: [] })),
  ])
    .then(([data, photoData, sourceCompanies, captainData]) => {
      const photosById = new Map((photoData.entries || []).map((entry) => [entry.id, entry]));
      const companies = normalizeCompanies(sourceCompanies, data.entries);
      const participation = buildParticipation(captainData, companies);
      const participationYears = [...participation.values()].flatMap((years) => [...years].map(String));
      const years = [...new Set([...data.entries.map((entry) => String(entry.year)), ...participationYears])].sort(byYear);
      const companyNames = companies.map((company) => company.name);
      const initialMode = initialParams.get("view") === "company" ? "company" : "year";
      const initialYear = initialParams.get("year") || "";
      const initialCompany = initialParams.get("company") || "";

      selected.year = years.includes(initialYear) ? initialYear : years[years.length - 1];
      selected.company = companyNames.includes(initialCompany) ? initialCompany : companies[0]?.name || "";
      modeInputs.forEach((input) => {
        input.checked = input.value === initialMode;
      });

      modeInputs.forEach((input) => input.addEventListener("change", () => updateMode(data, years, companies, photosById, participation)));
      filterSelect.addEventListener("change", () => render(data, companies, photosById, participation));
      updateMode(data, years, companies, photosById, participation);
    })
    .catch(() => {
      resultTitle.textContent = "No se ha podido cargar el listado";
      resultMeta.textContent = "";
      resultBody.replaceChildren();
    });
})();
