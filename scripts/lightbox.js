(function () {
  const dialog = document.createElement("div");
  dialog.className = "lightbox";
  dialog.hidden = true;
  dialog.innerHTML = `
    <div class="lightbox-backdrop" data-lightbox-close></div>
    <div class="lightbox-panel" role="dialog" aria-modal="true" aria-label="Vista ampliada">
      <button class="lightbox-close" type="button" aria-label="Cerrar" data-lightbox-close>&times;</button>
      <img class="lightbox-image" alt="">
      <div class="lightbox-footer">
        <div class="lightbox-caption"></div>
      </div>
    </div>
  `;
  document.body.append(dialog);

  const image = dialog.querySelector(".lightbox-image");
  const caption = dialog.querySelector(".lightbox-caption");
  let previousFocus = null;
  let loadToken = 0;

  const truncate = (text, maxLength = 110) => {
    const normalized = text.replace(/\s+/g, " ").trim();
    return normalized.length > maxLength
      ? `${normalized.slice(0, maxLength - 1)}...`
      : normalized;
  };

  const normalize = (value, fallback = "") => {
    const normalized = String(value || "").replace(/\s+/g, " ").trim();
    return normalized || fallback;
  };

  const buildCaption = (link, label) => {
    const hasStructuredMetadata = Boolean(
      link.dataset.lightboxIdentifier
        || link.dataset.lightboxFund
        || link.dataset.lightboxAuthor
        || link.dataset.lightboxDetailUrl,
    );

    if (!hasStructuredMetadata) {
      const simple = document.createDocumentFragment();
      const text = document.createElement("p");
      text.textContent = label;
      simple.append(text);
      return simple;
    }

    const title = normalize(link.dataset.lightboxTitle, label);
    const date = normalize(link.dataset.lightboxDate);
    const identifier = normalize(link.dataset.lightboxIdentifier, "no indicado");
    const license = normalize(link.dataset.lightboxLicense, "CC BY-NC 4.0");
    const fund = normalize(link.dataset.lightboxFund, "no indicado");
    const author = normalize(link.dataset.lightboxAuthor, "autor no indicado");
    const detailUrl = normalize(link.dataset.lightboxDetailUrl);
    const archive = normalize(link.dataset.lightboxArchive, "KUTXA FUNDAZIOA FOTOTEKA");
    const source = normalize(link.dataset.lightboxSource, "kutxateka");
    const fragment = document.createDocumentFragment();

    const summary = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `«${title}»`;
    summary.append(strong);
    summary.append(date ? `, ${date}. Identificador: ${identifier}.` : `. Identificador: ${identifier}.`);

    const credit = document.createElement("p");
    if (source === "archivo-irun") {
      credit.textContent = `${license} / ${archive} / ${fund}.`;
    } else {
      credit.textContent = `${license} 2015 / KUTXA FUNDAZIOA FOTOTEKA / Fondo ${fund} / ${author}.`;
    }

    fragment.append(summary, credit);

    if (detailUrl) {
      const original = document.createElement("p");
      const originalLink = document.createElement("a");
      originalLink.href = detailUrl;
      originalLink.target = "_blank";
      originalLink.rel = "noopener noreferrer";
      originalLink.textContent = source === "archivo-irun"
        ? "Ver ficha original en el Archivo Municipal de Irun."
        : "Ver ficha original en Kutxateka.";
      original.append(originalLink);
      fragment.append(original);
    }

    return fragment;
  };

  const close = () => {
    loadToken += 1;
    dialog.classList.remove("is-open");
    dialog.hidden = true;
    document.body.classList.remove("has-lightbox");
    image.removeAttribute("src");
    if (previousFocus) {
      previousFocus.focus();
    }
  };

  const open = (link) => {
    const thumbnail = link.querySelector("img");
    const label = truncate(link.dataset.lightboxTitle || thumbnail?.alt || link.textContent || "Imagen ampliada");
    const previewSrc = link.dataset.lightboxPreview || thumbnail?.currentSrc || thumbnail?.src || "";
    const currentToken = loadToken + 1;
    loadToken = currentToken;
    previousFocus = document.activeElement;
    image.removeAttribute("src");
    image.alt = label;
    if (previewSrc) {
      image.src = previewSrc;
    } else {
      image.src = link.href;
    }
    caption.replaceChildren(buildCaption(link, label));
    dialog.hidden = false;
    document.body.classList.add("has-lightbox");
    requestAnimationFrame(() => {
      if (currentToken === loadToken) {
        dialog.classList.add("is-open");
      }
    });
    dialog.querySelector(".lightbox-close").focus();

    const loader = new Image();
    loader.onload = () => {
      if (currentToken !== loadToken) {
        return;
      }
      image.src = link.href;
    };
    loader.onerror = () => {
      if (currentToken !== loadToken || previewSrc) {
        return;
      }
      image.removeAttribute("src");
    };
    loader.src = link.href;
  };

  document.addEventListener("click", (event) => {
    const link = event.target.closest("[data-lightbox]");

    if (!link) {
      return;
    }

    event.preventDefault();
    open(link);
  });

  dialog.addEventListener("click", (event) => {
    if (event.target.closest("[data-lightbox-close]")) {
      close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (!dialog.hidden && event.key === "Escape") {
      close();
    }
  });
})();
