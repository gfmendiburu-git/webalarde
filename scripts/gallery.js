(function () {
  const gallery = document.querySelector("#image-gallery");
  const yearFilter = document.querySelector("#gallery-year-filter");
  const count = document.querySelector("#gallery-count");

  if (!gallery || !yearFilter || !count) {
    return;
  }

  const fragmentFromItem = (item) => {
    const link = document.createElement("a");
    link.className = "image-card";
    link.href = item.full;
    link.dataset.lightbox = "";
    link.dataset.lightboxTitle = item.title || "Fotografía histórica";
    link.dataset.lightboxPreview = item.thumb;

    const image = document.createElement("img");
    image.src = item.thumb;
    image.alt = item.title || "Fotografía histórica del Alarde de San Marcial";
    image.loading = "lazy";
    image.decoding = "async";

    const body = document.createElement("span");

    const title = document.createElement("strong");
    title.textContent = item.title || "Fotografía histórica";

    const meta = document.createElement("small");
    meta.textContent = [item.date, item.photographer].filter(Boolean).join(" · ");

    body.append(title, meta);
    link.append(image, body);
    return link;
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

  fetch("data/alarde-imagenes.json")
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
