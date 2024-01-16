/**
 * Represents a color with red, green, and blue components.
 */
class Color {
    /**
     * Creates a new Color instance.
     * @param {number} red - The red component (0-255).
     * @param {number} green - The green component (0-255).
     * @param {number} blue - The blue component (0-255).
     */
    constructor(red, green, blue) {
        this.red = red;
        this.green = green;
        this.blue = blue;
    }

    /**
     * Returns the RGB representation of the color.
     * @returns {string} The RGB string.
     */
    rgb() {
        return `rgb(${this.red},${this.green},${this.blue})`
    }

    static fromHex(string) { return new Color(parseInt(string.slice(1, 3), 16), parseInt(string.slice(3, 5), 16), parseInt(string.slice(5, 7), 16)) }

    static red()     { return Color.fromHex("#FF3F3F"); };
    static yellow()  { return Color.fromHex("#FCEF64"); };
    static green()   { return Color.fromHex("#4AE27A"); };
    static magenta() { return Color.fromHex("#D67AB1"); };

    static increase() { return Color.red().rgb() };
    static decrease() { return Color.green().rgb() };
}

/**
 * Generates a color gradient between three colors.
 * @param {number} steps - The number of steps in the gradient.
 * @param {Color} start - The starting color.
 * @param {Color} middle - The middle color.
 * @param {Color} stop - The ending color.
 * @returns {Array<string>} An array of RGB strings representing the gradient.
 */
function colorGradient(steps, start, middle, stop) {
    const result = [];
    const threshold = steps / 2;

    for (let step = 0; step <= steps; step++) {
        const diff = step / steps;
        let from, to;

        if (step < threshold) {
            from = start;
            to = middle;
        } else if (step > threshold) {
            from = middle;
            to = stop;
        } else {
            from = middle;
            to = middle;
        }

        const red = to.red - from.red;
        const green = to.green - from.green;
        const blue = to.blue - from.blue;

        result.push(new Color(
            Math.floor(from.red + (red * diff)),
            Math.floor(from.green + (green * diff)),
            Math.floor(from.blue + (blue * diff))
        ).rgb());
    }

    return result;
}

const colors = colorGradient($(`#minutes td`).length, Color.red(), Color.yellow(), Color.green());

/**
 * Colors the cells in a row based on the specified identifier.
 * @param {string} identifier - The identifier of the row.
 */
function colorRow(identifier) {
    var elements = $(`#${identifier} td`);
    var values = Object.values(elements.map((_, x) => parseFloat(x.querySelector("span").textContent))).sort((a, b) => a - b);

    elements.each((_, x) => { x.style.backgroundColor = colors[values.indexOf(parseFloat(x.querySelector("span").textContent))] });
};

/**
 * Compares the content of two HTML elements and applies a background color based on the difference.
 * @param {HTMLElement} present - The present HTML element for comparison.
 * @param {HTMLElement} previous - The previous HTML element for comparison.
 * @param {Function} callback - A callback function to modify the present element before applying styles.
 */
function compare(present, previous, callback) {
    var diff = parseFloat(present.textContent) - parseFloat(previous.textContent);
    var color = (diff > 0) ? Color.increase() : ((diff == 0) ? "" : Color.decrease());
    $(callback(present)).css("backgroundColor", color);
};

/**
 * Colors the total/recap column based on the change from the previous month
 */
function colorComparison() {
    var recap = $("#recap td div.currency span.currency-value");
    $("#total td div.currency span.currency-value").each(function (index, value) {
        compare(value, recap[index], (c) => c.closest("td"));
    });

    var shared = $("tr.shared td div span.currency-value");
    shared.each((index, row) => {
        if (index % 2 != 0) { return; };
        compare(row, shared[index + 1], (c) => c.closest("td"));
    })
}

// onload functions
$(function () {
    // Add color to the icon
    $("#icon").css("color", Color.magenta().rgb());

    // Enable panel display in tabs
    $("#panel ul li").on("click", function () {
        var button = this;
        $(button).addClass("is-active");
        $(button).siblings().each(function (_, value) {
            $(value).removeClass("is-active");
        });

        $("#panels").children().each(function (_, value) {
            if (value.id == button.dataset.target) { $(value).show(); }
            else { $(value).hide(); }
        });
    });

    // Enable showing navbar menu on narrow screens
    $(".navbar-burger").on("click", function () {
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
    });
});
