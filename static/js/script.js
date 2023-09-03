const dropdownMenu = document.querySelector(".dropdown-menu");
const dropdownButton = document.querySelector(".dropdown-button");

if (dropdownButton) {
  dropdownButton.addEventListener("click", () => {
    dropdownMenu.classList.toggle("show");
  });
}

// Upload Image
const photoInput = document.querySelector("#avatar");
const photoPreview = document.querySelector("#preview-avatar");
if (photoInput)
  photoInput.onchange = () => {
    const [file] = photoInput.files;
    if (file) {
      photoPreview.src = URL.createObjectURL(file);
    }
  };

// Scroll to Bottom
const conversationThread = document.querySelector(".room__box");
if (conversationThread) conversationThread.scrollTop = conversationThread.scrollHeight;


// For toggling between dark theme and light theme
const theme = () => {
  var radios = document.querySelectorAll('input[name="theme"');
  var dark = document.getElementById("dark");
  var light = document.getElementById("light");

  const preferColorScheme = window.matchMedia('(prefers-color-scheme:dark)');
  if (preferColorScheme.matches) {
    document.getElementById("dark").checked = true;
  }
  else {
    document.getElementById("light").checked = true;
  }

  const theme_changer = () => {
    for (let radio of radios) {
      if (radio.checked) {
        document.querySelector('body').classList = radio.value;
        radio.checked = true;
      }
    }
  }

  dark.addEventListener('click', theme_changer);
  light.addEventListener('click', theme_changer);
}
theme()