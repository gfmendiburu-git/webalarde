(function () {
  const gallery = document.querySelector("#image-gallery");
  const yearFilter = document.querySelector("#gallery-year-filter");
  const count = document.querySelector("#gallery-count");

  if (!gallery || !yearFilter || !count) {
    return;
  }

  const LICENSE = "CC BY-NC 4.0";

  const normalize = (value, fallback) => {
    const normalized = String(value || "").replace(/\s+/g, " ").trim();
    return normalized || fallback;
  };

  const getFund = (item) => normalize(item.studio || item.archive, "no indicado");
  const getAuthor = (item) => normalize(item.photographer, "autor no indicado");
  const getLicense = (item) => normalize(item.license, LICENSE);
  const getArchive = (item) => normalize(item.archive, "Kutxa Fundazioa Fototeka");
  const getOriginalLabel = (item) => item.source === "archivo-irun" ? "Ficha original" : "Ficha original";

  const appendOriginalLink = (container, item) => {
    container.append(" · ");
    const original = document.createElement("a");
    original.href = item.detail_url;
    original.target = "_blank";
    original.rel = "noopener noreferrer";
    original.textContent = getOriginalLabel(item);
    container.append(original);
  };

  const fragmentFromItem = (item) => {
    const card = document.createElement("article");
    card.className = "image-card";

    const link = document.createElement("a");
    link.className = "image-card-preview";
    link.href = item.full;
    link.dataset.lightbox = "";
    link.dataset.lightboxTitle = item.title || "Fotografía histórica";
    link.dataset.lightboxDate = item.date || "";
    link.dataset.lightboxIdentifier = item.object_id || "";
    link.dataset.lightboxLicense = getLicense(item);
    link.dataset.lightboxFund = getFund(item);
    link.dataset.lightboxAuthor = getAuthor(item);
    link.dataset.lightboxDetailUrl = item.detail_url || "";
    link.dataset.lightboxPreview = item.thumb;
    link.dataset.lightboxArchive = getArchive(item);
    link.dataset.lightboxSource = item.source || "kutxateka";

    const image = document.createElement("img");
    image.src = item.thumb;
    image.alt = item.title || "Fotografía histórica del Alarde de San Marcial";
    image.loading = "lazy";
    image.decoding = "async";

    link.append(image);

    const credit = document.createElement("p");
    credit.className = "image-credit";
    if (item.source === "archivo-irun") {
      credit.append(`${getArchive(item)} · ${getFund(item)} · Ref. ${item.object_id} · ${getLicense(item)}`);
    } else {
      credit.append(`Kutxa Fundazioa Fototeka · Fondo ${getFund(item)} · ${getAuthor(item)} · ${getLicense(item)}`);
    }
    if (item.detail_url) {
      appendOriginalLink(credit, item);
    }

    card.append(link, credit);
    return card;
  };

  const render = (items) => {
    const selectedYear = yearFilter.value;
    const filtered = selectedYear === "todos"
      ? items
      : items.filter((item) => item.year === selectedYear);

    const fragment = document.createDocumentFragment();
    filtered.forEach((item) => fragment.append(fragmentFromItem(item)));
    gallery.replaceChildren(fragment);
    count.textContent = `${filtered.length} imágenes`;
  };

  fetch("data/alarde-imagenes.json?v=3")
    .then((response) => response.json())
    .then((items) => {
      const years = [...new Set(items.map((item) => item.year || "sin-fecha"))].sort((a, b) => {
        if (a === "sin-fecha") return 1;
        if (b === "sin-fecha") return -1;
        return Number(a) - Number(b);
      });

      years.forEach((year) => {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year === "sin-fecha" ? "Sin fecha" : year;
        yearFilter.append(option);
      });

      yearFilter.addEventListener("change", () => render(items));
      render(items);
    })
    .catch(() => {
      count.textContent = "No se ha podido cargar la galería";
    });
})();
