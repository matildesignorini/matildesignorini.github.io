// Publications: filter by authorship, sort by date or group by topic.
(function () {
  var box = document.querySelector(".pubs");
  var controls = document.querySelector(".pub-controls");
  if (!box || !controls) return;
  controls.hidden = false;

  var pubs = Array.prototype.slice.call(box.querySelectorAll(".pub"));
  var count = controls.querySelector(".pub-count");
  var state = { filter: "all", sort: "date" };

  // topic -> colour class, read from the research-interest cards
  var colours = {};
  document.querySelectorAll(".interest").forEach(function (card) {
    var cls = Array.prototype.find.call(card.classList, function (c) { return c.indexOf("c-") === 0; });
    colours[card.querySelector("h3").textContent.trim()] = cls || "c-ink";
  });
  var topicOrder = Object.keys(colours);

  function key(li) { return (+li.dataset.year) * 100 + (+li.dataset.month); }
  function shown(li) {
    var first = li.dataset.first === "true";
    return state.filter === "all" || (state.filter === "first" ? first : !first);
  }

  function render() {
    box.querySelectorAll(".group-head, .pub.copy").forEach(function (n) { n.remove(); });
    var visible = pubs.filter(shown).sort(function (a, b) { return key(b) - key(a); });
    pubs.forEach(function (li) { li.hidden = true; });

    if (state.sort === "date") {
      visible.forEach(function (li) { li.hidden = false; box.appendChild(li); });
    } else {
      // a paper with two topics appears under both
      var topics = topicOrder.slice();
      visible.forEach(function (li) {
        li.dataset.topics.split("|").forEach(function (t) { if (t && topics.indexOf(t) < 0) topics.push(t); });
      });
      topics.forEach(function (t) {
        var inTopic = visible.filter(function (li) { return li.dataset.topics.split("|").indexOf(t) >= 0; });
        if (!inTopic.length) return;
        var head = document.createElement("li");
        head.className = "group-head " + (colours[t] || "c-ink");
        var tag = document.createElement("span");
        tag.textContent = t + " · " + inTopic.length;
        head.appendChild(tag);
        box.appendChild(head);
        inTopic.forEach(function (li) {
          var node = li;
          if (!li.hidden) { node = li.cloneNode(true); node.classList.add("copy"); }
          node.hidden = false;
          box.appendChild(node);
        });
      });
    }
    count.textContent = visible.length + (visible.length === 1 ? " paper" : " papers");
    box.parentElement.scrollTop = 0;
  }

  controls.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    var group = b.parentElement;
    group.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
    if (b.dataset.filter) state.filter = b.dataset.filter;
    if (b.dataset.sort) state.sort = b.dataset.sort;
    render();
  });

  render();
})();
