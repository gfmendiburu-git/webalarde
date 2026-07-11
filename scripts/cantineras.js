(function () {
  const modeInputs = document.querySelectorAll("[name='cantinera-view']");
  const yearSelect = document.querySelector("#cantinera-year");
  const companySelect = document.querySelector("#cantinera-company");
  const yearControl = document.querySelector("#cantinera-year-control");
  const companyControl = document.querySelector("#cantinera-company-control");
  const resultTitle = document.querySelector("#cantinera-result-title");
  const resultMeta = document.querySelector("#cantinera-result-meta");
  const resultBody = document.querySelector("#cantinera-results");

  if (!modeInputs.length || !yearSelect || !companySelect || !resultBody) {
    return;
  }

  const collator = new Intl.Collator("es", { sensitivity: "base" });

  const byYear = (a, b) => Number(a) - Number(b);
  const byCompany = (a, b) => collator.compare(a, b);

  const currentMode = () => {
    const checked = document.querySelector("[name='cantinera-view']:checked");
    return checked ? checked.value : "year";
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

  const renderTable = (entries, columns) => {
    const table = document.createElement("table");
    table.className = "cantineras-table";

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    columns.forEach((column) => {
      const th = document.createElement("th");
      th.textContent = column.label;
      headRow.append(th);
    });
    thead.append(headRow);

    const tbody = document.createElement("tbody");
    entries.forEach((entry) => {
      const row = document.createElement("tr");
      columns.forEach((column) => {
        const cell = document.createElement("td");
        if (column.key === "name") {
          const name = document.createElement("strong");
          name.textContent = entry.name;
          cell.append(name);
          if (entry.needs_review) {
            cell.append(" ");
            cell.append(reviewBadge());
          }
        } else if (column.key === "source") {
          cell.append(sourceLink(entry));
        } else {
          cell.textContent = entry[column.key];
        }
        row.append(cell);
      });
      tbody.append(row);
    });

    table.append(thead, tbody);
    return table;
  };

  const render = (data) => {
    const mode = currentMode();
    yearControl.hidden = mode !== "year";
    companyControl.hidden = mode !== "company";

    if (mode === "year") {
      const year = Number(yearSelect.value);
      const entries = data.entries
        .filter((entry) => entry.year === year)
        .sort((a, b) => byCompany(a.company, b.company));
      resultTitle.textContent = `Cantineras de ${year}`;
      resultMeta.textContent = `${entries.length} registros localizados`;
      resultBody.replaceChildren(renderTable(entries, [
        { key: "company", label: "Compañía" },
        { key: "name", label: "Cantinera" },
        { key: "source", label: "Referencia" },
      ]));
      return;
    }

    const company = companySelect.value;
    const entries = data.entries
      .filter((entry) => entry.company === company)
      .sort((a, b) => byYear(a.year, b.year));
    resultTitle.textContent = company;
    resultMeta.textContent = `${entries.length} años con registro localizado`;
    resultBody.replaceChildren(renderTable(entries, [
      { key: "year", label: "Año" },
      { key: "name", label: "Cantinera" },
      { key: "source", label: "Referencia" },
    ]));
  };

  fetch("data/cantineras.json?v=1")
    .then((response) => response.json())
    .then((data) => {
      const years = [...new Set(data.entries.map((entry) => entry.year))].sort(byYear);
      const companies = [...new Set(data.entries.map((entry) => entry.company))].sort(byCompany);

      years.forEach((year) => {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        yearSelect.append(option);
      });
      yearSelect.value = years[years.length - 1];

      companies.forEach((company) => {
        const option = document.createElement("option");
        option.value = company;
        option.textContent = company;
        companySelect.append(option);
      });

      modeInputs.forEach((input) => input.addEventListener("change", () => render(data)));
      yearSelect.addEventListener("change", () => render(data));
      companySelect.addEventListener("change", () => render(data));
      render(data);
    })
    .catch(() => {
      resultTitle.textContent = "No se ha podido cargar el listado";
      resultMeta.textContent = "";
      resultBody.replaceChildren();
    });
})();
