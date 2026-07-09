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
        <p class="lightbox-caption"></p>
        <a class="lightbox-download" href="#" download>Descargar</a>
      </div>
    </div>
  `;
  document.body.append(dialog);

  const image = dialog.querySelector(".lightbox-image");
  const caption = dialog.querySelector(".lightbox-caption");
  const download = dialog.querySelector(".lightbox-download");
  let previousFocus = null;
  let loadToken = 0;

  const truncate = (text, maxLength = 110) => {
    const normalized = text.replace(/\s+/g, " ").trim();
    return normalized.length > maxLength
      ? `${normalized.slice(0, maxLength - 1)}...`
      : normalized;
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
    caption.textContent = label;
    download.href = link.href;
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
