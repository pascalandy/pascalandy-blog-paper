const THEME = "theme";
const LIGHT = "light";
const DARK = "dark";
const systemScheme = window.matchMedia("(prefers-color-scheme: dark)");

const LABELS: Record<string, string> = { [LIGHT]: "clair", [DARK]: "sombre" };

// Can be "light", "dark", or empty string for system's prefers-color-scheme
const initialColorScheme = "";

function getSystemTheme(): string {
  return systemScheme.matches ? DARK : LIGHT;
}

function getPreferTheme(): string {
  return localStorage.getItem(THEME) || initialColorScheme || getSystemTheme();
}

let themeValue = window.theme?.themeValue ?? getPreferTheme();

function setPreference(): void {
  if (themeValue === getSystemTheme()) {
    localStorage.removeItem(THEME);
  } else {
    localStorage.setItem(THEME, themeValue);
  }
  reflectPreference();
}

function reflectPreference(): void {
  document.firstElementChild?.setAttribute("data-theme", themeValue);

  document
    .querySelector("#theme-btn")
    ?.setAttribute("aria-label", LABELS[themeValue] ?? themeValue);

  const body = document.body;

  if (body) {
    const computedStyles = window.getComputedStyle(body);

    const bgColor = computedStyles.backgroundColor;

    document
      .querySelector("meta[name='theme-color']")
      ?.setAttribute("content", bgColor);
  }
}

if (window.theme) {
  window.theme.setPreference = setPreference;
  window.theme.reflectPreference = reflectPreference;
} else {
  window.theme = {
    themeValue,
    setPreference,
    reflectPreference,
    getTheme: () => themeValue,
    setTheme: (val: string) => {
      themeValue = val;
    },
  };
}

// Ensure theme is reflected (in case body wasn't ready when inline script ran)
reflectPreference();

function setThemeFeature(): void {
  // set on load so screen readers can get the latest value on the button
  reflectPreference();

  document.querySelector("#theme-btn")?.addEventListener("click", () => {
    themeValue = themeValue === LIGHT ? DARK : LIGHT;
    window.theme?.setTheme(themeValue);
    setPreference();
  });
}

setThemeFeature();

document.addEventListener("astro:after-swap", setThemeFeature);

// Set theme-color value before page transition
// to avoid navigation bar color flickering in Android dark mode
document.addEventListener("astro:before-swap", event => {
  const astroEvent = event;
  const bgColor = document
    .querySelector("meta[name='theme-color']")
    ?.getAttribute("content");

  if (bgColor) {
    astroEvent.newDocument
      .querySelector("meta[name='theme-color']")
      ?.setAttribute("content", bgColor);
  }
});

systemScheme.addEventListener("change", () => {
  themeValue = getPreferTheme();
  window.theme?.setTheme(themeValue);
  reflectPreference();
});
