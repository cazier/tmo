function _getDarkMode() {
    var resp =  document.documentElement.dataset.theme == "dark";
    return resp;
}

function _setDarkMode(on) {
    document.documentElement.dataset.theme = on ? "dark" : ""
    localStorage.setItem('dark_mode', JSON.stringify(on));
}

function setDarkMode(on = null) {
    if (on === null) {
        var on = localStorage.getItem("dark_mode");
        if (on === null) {
            on = window.matchMedia("(prefers-color-scheme: dark)").matches;
        } else {
            on = JSON.parse(on);
        }
    }

    _setDarkMode(on);

    // if (on) {
    //     document.documentElement.dataset.theme = "dark";
    // } else {
    //     document.documentElement.dataset.theme = "";
    // }

}

function setDarkModeIcon(span) {
    console.log("Dark Mode Set");
    var icon = span.querySelector("i");

    if (_getDarkMode()) {
        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun")
    } else {
        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon")
    }

}

window.addEventListener('load', () => {
    var button = document.querySelector("#dark_toggle");
    setDarkModeIcon(button);

    button.addEventListener("click", () => {
        _setDarkMode(! _getDarkMode());
        setDarkModeIcon(button);
    })
});
