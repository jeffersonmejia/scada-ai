(function () {
  const icons = {
    "add-outline": [
      ["path", { d: "M12 5v14" }],
      ["path", { d: "M5 12h14" }]
    ],
    "arrow-up-outline": [
      ["path", { d: "M12 19V5" }],
      ["path", { d: "m6 11 6-6 6 6" }]
    ],
    "chatbubble-ellipses-outline": [
      ["path", { d: "M21 11.5a8.4 8.4 0 0 1-8.5 8.5 8.9 8.9 0 0 1-3.7-.8L3 21l1.9-5.2A8 8 0 0 1 4 11.5 8.4 8.4 0 0 1 12.5 3 8.4 8.4 0 0 1 21 11.5Z" }],
      ["path", { d: "M8.5 12h.01" }],
      ["path", { d: "M12.5 12h.01" }],
      ["path", { d: "M16.5 12h.01" }]
    ],
    "hardware-chip-outline": [
      ["rect", { x: "7", y: "7", width: "10", height: "10", rx: "2" }],
      ["path", { d: "M9 1v3" }],
      ["path", { d: "M15 1v3" }],
      ["path", { d: "M9 20v3" }],
      ["path", { d: "M15 20v3" }],
      ["path", { d: "M1 9h3" }],
      ["path", { d: "M1 15h3" }],
      ["path", { d: "M20 9h3" }],
      ["path", { d: "M20 15h3" }],
      ["path", { d: "M10 10h4v4h-4z" }]
    ],
    "moon-outline": [
      ["path", { d: "M12 3a6.7 6.7 0 0 0 8.9 8.9A8.2 8.2 0 1 1 12 3Z" }]
    ],
    "musical-notes-outline": [
      ["path", { d: "M9 18V5l12-2v13" }],
      ["path", { d: "M9 9l12-2" }],
      ["circle", { cx: "6", cy: "18", r: "3" }],
      ["circle", { cx: "18", cy: "16", r: "3" }]
    ],
    "shield-checkmark-outline": [
      ["path", { d: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" }],
      ["path", { d: "m9 12 2 2 4-5" }]
    ],
    "sunny-outline": [
      ["circle", { cx: "12", cy: "12", r: "4" }],
      ["path", { d: "M12 2v2" }],
      ["path", { d: "M12 20v2" }],
      ["path", { d: "M4.93 4.93 6.34 6.34" }],
      ["path", { d: "M17.66 17.66 19.07 19.07" }],
      ["path", { d: "M2 12h2" }],
      ["path", { d: "M20 12h2" }],
      ["path", { d: "M4.93 19.07 6.34 17.66" }],
      ["path", { d: "M17.66 6.34 19.07 4.93" }]
    ]
  };

  class IonIcon extends HTMLElement {
    static get observedAttributes() {
      return ["name"];
    }

    connectedCallback() {
      this.render();
    }

    attributeChangedCallback() {
      this.render();
    }

    render() {
      const name = this.getAttribute("name");
      const shapes = icons[name];
      if (!shapes) return;

      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("viewBox", "0 0 24 24");
      svg.setAttribute("fill", "none");
      svg.setAttribute("stroke", "currentColor");
      svg.setAttribute("stroke-width", "2");
      svg.setAttribute("stroke-linecap", "round");
      svg.setAttribute("stroke-linejoin", "round");
      svg.setAttribute("aria-hidden", "true");
      svg.style.display = "block";
      svg.style.height = "100%";
      svg.style.width = "100%";

      shapes.forEach(([tag, attrs]) => {
        const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
        Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
        svg.appendChild(node);
      });

      this.replaceChildren(svg);
    }
  }

  if (!customElements.get("ion-icon")) {
    customElements.define("ion-icon", IonIcon);
  }
})();
