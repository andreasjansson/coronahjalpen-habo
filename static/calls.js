function markPosted(e) {
  var checked = this.checked;
  var sid = $(e.target).data("sid");
  $.post("/samordna/samtal-postad", {
    posted: checked,
    sid: sid,
    csrfmiddlewaretoken: window.CSRF_TOKEN,
  })
}

$(".mark-posted").on("change", markPosted);
