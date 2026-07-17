(function () {
  const title = document.querySelector("#cantinera-gallery-title");
  const meta = document.querySelector("#cantinera-gallery-meta");
  const gallery = document.querySelector("#cantinera-gallery");

  if (!title || !meta || !gallery) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const id = params.get("id") || "";

  const normalize = (value, fallback) => {
    const normalized = String(value || "").replace(/\s+/g, " ").trim();
    return normalized || fallback;
  };

  const appendOriginalLink = (container, item) => {
    if (!item.detail_url) {
      return;
    }
    container.append(" · ");
    const original = document.createElement("a");
    original.href = item.detail_url;
    original.target = "_blank";
    original.rel = "noopener noreferrer";
    original.textContent = "Ficha original";
    container.append(original);
  };

  const cardFromPhoto = (item) => {
    const card = document.createElement("article");
    card.className = "image-card";

    const link = document.createElement("a");
    link.className = "image-card-preview";
    link.href = item.full;
    link.dataset.lightbox = "";
    link.dataset.lightboxTitle = item.title || "Fotografía histórica";
    link.dataset.lightboxDate = item.date || "";
    link.dataset.lightboxIdentifier = item.object_id || "";
    link.dataset.lightboxLicense = normalize(item.license, "Uso no comercial autorizado");
    link.dataset.lightboxFund = normalize(item.studio || item.archive, "no indicado");
    link.dataset.lightboxAuthor = normalize(item.photographer, "autor no indicado");
    link.dataset.lightboxArchive = normalize(item.archive, "Archivo Municipal de Irun");
    link.dataset.lightboxSource = item.source || "archivo-irun";
    link.dataset.lightboxDetailUrl = item.detail_url || "";
    link.dataset.lightboxPreview = item.thumb;

    const image = document.createElement("img");
    image.src = item.thumb;
    image.alt = item.title || "Fotografía de cantinera del Alarde de San Marcial";
    image.loading = "lazy";
    image.decoding = "async";
    link.append(image);

    const credit = document.createElement("p");
    credit.className = "image-credit";
    credit.append(
      `${normalize(item.archive, "Archivo Municipal de Irun")} · ${normalize(item.studio, "fondo no indicado")} · Ref. ${item.object_id} · ${normalize(item.license, "uso no comercial autorizado")}`,
    );
    appendOriginalLink(credit, item);

    card.append(link, credit);
    return card;
  };

  fetch("data/cantinera-fotos.json?v=1")
    .then((response) => response.json())
    .then((data) => {
      const entry = (data.entries || []).find((item) => item.id === id);

      if (!entry) {
        title.textContent = "Galería no localizada";
        meta.textContent = "No hay fotografías identificadas para esta cantinera.";
        gallery.replaceChildren();
        return;
      }

      title.textContent = entry.name;
      meta.textContent = `${entry.company} · ${entry.year} · ${entry.photos.length} foto${entry.photos.length === 1 ? "" : "s"} identificada${entry.photos.length === 1 ? "" : "s"}`;

      const fragment = document.createDocumentFragment();
      entry.photos.forEach((photo) => fragment.append(cardFromPhoto(photo)));
      gallery.replaceChildren(fragment);
    })
    .catch(() => {
      title.textContent = "No se ha podido cargar la galería";
      meta.textContent = "";
      gallery.replaceChildren();
    });
})();
