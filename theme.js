function toggleDarkMode() {
  const dark = document.body.classList.toggle("dark-mode");
  localStorage.setItem("theme", dark ? "dark" : "light");
}

if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-mode");
}
