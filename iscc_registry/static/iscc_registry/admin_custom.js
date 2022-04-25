window.onload = function pretty_json() {
    Array.from(document.querySelectorAll('div.readonly')).forEach(div => {
        let data;
        try {
            data = JSON.parse(div.innerText);
        } catch {
            // Not valid JSON
            return;
        }
        div.style.whiteSpace = 'pre-wrap';
        div.style.fontFamily = 'JetBrains Mono';
        div.style.fontSize = '1em';
        div.innerText = JSON.stringify(data, null, 2);
    });
}
