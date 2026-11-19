// Quarto build 
document.addEventListener("DOMContentLoaded", () => {
  // Update copyright year in the footer
  const yearEl = document.getElementById("copyright-year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Smooth scroll for the back-to-top button
  const backToTop = document.getElementById("quarto-back-to-top");
  if (backToTop) {
    backToTop.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  const applyPlotTheme = () => {
    const dark = document.documentElement.getAttribute("data-bs-theme") === "dark"
      || document.body.classList.contains("quarto-dark");
    const text = dark ? "#ddd8d0" : "#252320";
    const muted = dark ? "#8b8077" : "#77736a";
    const grid = dark ? "#233548" : "#ddd8d0";
    const axis = dark ? "#8b8077" : "#6b6559";

    document.querySelectorAll(".plotly").forEach((plot) => {
      if (!plot.layout) return;
      Plotly.relayout(plot, {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font.color": text,
        "xaxis.color": text,
        "xaxis.tickfont.color": text,
        "xaxis.title.font.color": text,
        "xaxis.linecolor": axis,
        "xaxis.gridcolor": grid,
        "yaxis.color": text,
        "yaxis.tickfont.color": text,
        "yaxis.title.font.color": text,
        "yaxis.linecolor": axis,
        "yaxis.gridcolor": grid,
        "legend.font.color": text,
        "legend.bgcolor": "rgba(0,0,0,0)"
      });
    });
  };

  const observer = new MutationObserver(applyPlotTheme);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-bs-theme", "class"] });
  observer.observe(document.body, { attributes: true, attributeFilter: ["class"] });
  setTimeout(applyPlotTheme, 500);
});